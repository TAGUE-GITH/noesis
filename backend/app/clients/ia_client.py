import os
import re

from anthropic import Anthropic, APIError


class AssistantIndisponible(Exception):
    """Levée quand l'assistant IA ne peut pas répondre : clé API absente,
    erreur réseau, ou erreur renvoyée par l'API Anthropic. Le reste de
    l'application n'a pas besoin de savoir POURQUOI ça a échoué — juste que
    ça a échoué, pour afficher un message propre plutôt qu'un 500 brut."""


_INSTRUCTION_SYSTEME = (
    "Tu es l'assistant pédagogique de Yamia, un moteur de recherche "
    "orienté apprentissage. Un visiteur consulte une notion et te pose une "
    "question à ce sujet.\n\n"
    "Règle stricte : réponds UNIQUEMENT à partir du contexte fourni "
    "ci-dessous, qui provient de cette notion. Si la question ne peut pas "
    "être répondue avec ce contexte, dis clairement que cette information "
    "ne s'y trouve pas, sans inventer de réponse et sans utiliser de "
    "connaissances extérieures à ce contexte.\n\n"
    "Réponds de façon concise (quelques phrases), en français."
)


def poser_question(contexte: str, question: str) -> str:
    """Envoie la question à Claude avec le contexte de la notion, et renvoie
    le texte de la réponse. Le nom du modèle vient d'une variable
    d'environnement plutôt que d'être codé en dur, pour pouvoir en changer
    sans toucher au code."""
    cle_api = os.environ.get("ANTHROPIC_API_KEY")
    if not cle_api:
        raise AssistantIndisponible("ANTHROPIC_API_KEY n'est pas configurée")

    modele = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

    client = Anthropic(api_key=cle_api)
    try:
        message = client.messages.create(
            model=modele,
            max_tokens=500,
            system=_INSTRUCTION_SYSTEME,
            messages=[
                {
                    "role": "user",
                    "content": f"Contexte (notion) :\n{contexte}\n\nQuestion : {question}",
                }
            ],
        )
    except APIError as erreur:
        raise AssistantIndisponible(str(erreur)) from erreur

    return message.content[0].text


_INSTRUCTION_SYSTEME_QUIZ = (
    "Tu génères un quiz de compréhension à partir UNIQUEMENT du contexte "
    "fourni (le contenu d'une notion). Chaque question doit pouvoir être "
    "répondue avec ce contexte seul, sans connaissance extérieure. Propose "
    "des questions à choix multiples, une seule bonne réponse par question, "
    "et une explication courte de la bonne réponse, toujours basée sur le "
    "contexte. En français."
)

# Schéma qu'on force l'IA à respecter (tool use) : plutôt que de lui
# demander d'écrire du JSON dans du texte libre (fragile — elle peut
# l'entourer de commentaires ou se tromper de syntaxe), on décrit la
# structure attendue et l'API garantit que la réponse s'y conforme.
_OUTIL_QUIZ = {
    "name": "soumettre_quiz",
    "description": "Soumet un quiz de compréhension généré à partir du contexte fourni.",
    "input_schema": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "minItems": 3,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "enonce": {"type": "string"},
                        "choix": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 4,
                        },
                        "reponse_correcte": {
                            "type": "integer",
                            "description": "Index (à partir de 0) de la bonne réponse dans 'choix'.",
                        },
                        "explication": {"type": "string"},
                    },
                    "required": ["enonce", "choix", "reponse_correcte", "explication"],
                },
            }
        },
        "required": ["questions"],
    },
}


def generer_quiz(contexte: str) -> list[dict]:
    """Génère un quiz à choix multiples à partir du contexte fourni.
    Contrairement à `poser_question`, on force ici une réponse structurée
    (tool use) : le format de chaque question est garanti, pas juste
    probable — plus besoin de parser un texte en espérant que ce soit
    du JSON valide."""
    cle_api = os.environ.get("ANTHROPIC_API_KEY")
    if not cle_api:
        raise AssistantIndisponible("ANTHROPIC_API_KEY n'est pas configurée")

    modele = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

    client = Anthropic(api_key=cle_api)
    try:
        message = client.messages.create(
            model=modele,
            max_tokens=1500,
            system=_INSTRUCTION_SYSTEME_QUIZ,
            tools=[_OUTIL_QUIZ],
            tool_choice={"type": "tool", "name": "soumettre_quiz"},
            messages=[{"role": "user", "content": f"Contexte :\n{contexte}"}],
        )
    except APIError as erreur:
        raise AssistantIndisponible(str(erreur)) from erreur

    for bloc in message.content:
        if bloc.type == "tool_use" and bloc.name == "soumettre_quiz":
            return bloc.input["questions"]

    # Ne devrait normalement jamais arriver puisqu'on force tool_choice,
    # mais on ne laisse jamais un cas non prévu remonter comme un 500 brut.
    raise AssistantIndisponible("Réponse inattendue de l'IA : pas de quiz reçu.")


# Outil "serveur" : contrairement à _OUTIL_QUIZ (qu'on définit et qu'on
# doit interpréter nous-mêmes), web_search est exécuté par Anthropic lui-
# même. Le modèle décide seul quand chercher, effectue la recherche, lit
# les résultats et les utilise pour répondre — on n'a aucune API de
# recherche à gérer. max_uses limite le nombre de recherches par génération
# (coût et latence).
_OUTIL_RECHERCHE_WEB = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
}

# Nombre de sources conservées comme ressources de la notion : une
# recherche peut en renvoyer beaucoup plus (potentiellement une quinzaine
# avec max_uses=3) — on ne garde que les plus pertinentes.
_MAX_SOURCES_CONSERVEES = 4


def _nettoyer_reponse(morceaux_texte: list[str]) -> str:
    """Nettoie le texte renvoyé par le modèle avant utilisation : même avec
    une consigne stricte, il arrive que le modèle glisse un peu de
    Markdown (titres "#", puces "*") — comme ce texte n'est que la matière
    première transmise à l'étape de structuration suivante (pas affiché
    tel quel), on retire ces marqueurs pour ne pas les laisser polluer la
    génération du contenu structuré."""
    lignes_propres = []
    for morceau in morceaux_texte:
        for ligne in morceau.splitlines():
            ligne = re.sub(r"^\s*#{1,6}\s*", "", ligne)
            ligne = re.sub(r"^\s*[-*]\s+", "", ligne)
            ligne = ligne.strip()
            if ligne:
                lignes_propres.append(ligne)
    texte = " ".join(lignes_propres)
    return re.sub(r"\s{2,}", " ", texte).strip()


_INSTRUCTION_SYSTEME_MATIERE = (
    "Tu rassembles des informations fiables et à jour sur une notion "
    "informatique, en cherchant sur le web si nécessaire. Ne rédige pas "
    "encore de contenu structuré : donne un ensemble d'informations denses "
    "et factuelles qui serviront de matière première, pensées pour "
    "quelqu'un qui découvre le sujet.\n\n"
    "Priorité absolue : les PRÉREQUIS et notions fondamentales avant les "
    "détails d'implémentation avancés. Si le sujet est un langage de "
    "programmation, couvre impérativement, avec un exemple concret pour "
    "chacune : la syntaxe de base (variables, types, structures de "
    "contrôle), et s'il est orienté objet, les classes et objets, "
    "l'encapsulation, l'héritage et le polymorphisme. Les détails internes "
    "(compilation, machine virtuelle, optimisations) viennent en "
    "complément, jamais à la place de ces bases. Si le sujet n'est pas un "
    "langage (un outil, un concept, une architecture...), applique le même "
    "principe : ses propres prérequis et notions fondamentales d'abord.\n\n"
    "En français."
)


def _rassembler_matiere(terme: str) -> tuple[str, list[dict]]:
    """Étape 1/2 de la génération d'une notion : une recherche web libre
    pour rassembler une matière dense et fiable. Renvoie aussi les pages
    réellement consultées (extraites des blocs `web_search_tool_result`),
    pour qu'elles deviennent les ressources affichées sur la notion — même
    principe de transparence des sources que pour une fiche vérifiée."""
    cle_api = os.environ.get("ANTHROPIC_API_KEY")
    if not cle_api:
        raise AssistantIndisponible("ANTHROPIC_API_KEY n'est pas configurée")

    modele = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

    client = Anthropic(api_key=cle_api)
    try:
        message = client.messages.create(
            model=modele,
            max_tokens=2500,
            system=_INSTRUCTION_SYSTEME_MATIERE,
            tools=[_OUTIL_RECHERCHE_WEB],
            messages=[{"role": "user", "content": terme}],
        )
    except APIError as erreur:
        raise AssistantIndisponible(str(erreur)) from erreur

    morceaux = []
    sources = []
    urls_vues = set()
    for bloc in message.content:
        if bloc.type == "text":
            morceaux.append(bloc.text)
        elif bloc.type == "web_search_tool_result" and isinstance(bloc.content, list):
            for resultat in bloc.content:
                if resultat.url not in urls_vues:
                    urls_vues.add(resultat.url)
                    sources.append({"libelle": resultat.title, "url": resultat.url})

    matiere = _nettoyer_reponse(morceaux)
    if not matiere:
        raise AssistantIndisponible("Recherche vide pour la génération de la notion.")
    return matiere, sources[:_MAX_SOURCES_CONSERVEES]


_INSTRUCTION_SYSTEME_STRUCTURER_NOTION = (
    "Tu rédiges le contenu pédagogique d'une notion informatique à partir "
    "de la matière fournie, pour un moteur de recherche orienté "
    "apprentissage — pas un simple résumé, un véritable mini-cours. "
    "Quelqu'un qui ne connaît pas du tout le sujet doit pouvoir suivre du "
    "début à la fin sans lacune, et donner cette notion (\"pourquoi elle "
    "existe\", une analogie de la vie réelle, comment elle fonctionne, un "
    "exemple concret et commenté, les erreurs fréquentes) plutôt qu'une "
    "simple définition.\n\n"
    "Structure en blocs ordonnés (3 à 8). Chaque bloc a un type :\n"
    "- \"texte\" : définition, pourquoi cette notion existe, fonctionnement, "
    "test/vérification — de la prose explicative.\n"
    "- \"analogie\" : UNE comparaison avec la vie réelle qui facilite "
    "vraiment la compréhension (ex. une classe = le plan d'une maison, un "
    "objet = une maison construite à partir de ce plan). Toujours inclure "
    "ce type de bloc quand une analogie pertinente existe.\n"
    "- \"code\" : un exemple concret et commenté (le champ 'texte' explique "
    "ce que fait le code étape par étape, pas juste \"voici un exemple\"). "
    "Inclure au moins un bloc code quand la notion s'y prête (langage de "
    "programmation, structure de données, outil avec syntaxe).\n"
    "- \"a_retenir\" : un court résumé des points essentiels en fin de "
    "notion.\n"
    "- \"erreur_frequente\" : une erreur ou confusion courante des "
    "débutants sur cette notion, si pertinent.\n\n"
    "Priorité : les prérequis et notions fondamentales d'abord (pour un "
    "langage orienté objet, les classes, l'encapsulation, l'héritage et le "
    "polymorphisme ne sont jamais des détails secondaires), les détails "
    "avancés ensuite. N'impose pas les mêmes types de blocs si ce n'est pas "
    "pertinent pour le sujet (une notion simple n'a pas besoin d'autant de "
    "blocs qu'un framework entier).\n\n"
    "Fournis aussi : un résumé d'une phrase (pour une liste de résultats de "
    "recherche) et une liste de mots-clés pertinents pour retrouver cette "
    "notion dans une recherche.\n\n"
    "Ton neutre et pédagogique, qui donne envie de lire, en français."
)

_TYPES_BLOC = ["texte", "analogie", "code", "a_retenir", "erreur_frequente"]

# Comme _OUTIL_QUIZ : un schéma qu'on force l'IA à respecter (tool use),
# pour obtenir un contenu déjà découpé en blocs typés exploitables par le
# frontend (vrais titres, vrais blocs de code, vrai type d'affichage) plutôt
# qu'un pavé de texte où on devrait deviner la structure.
_OUTIL_NOTION = {
    "name": "soumettre_notion",
    "description": "Soumet le contenu pédagogique structuré d'une notion informatique.",
    "input_schema": {
        "type": "object",
        "properties": {
            "titre": {"type": "string"},
            "resume": {
                "type": "string",
                "description": "Résumé en une phrase, pour une liste de résultats de recherche.",
            },
            "mots_cles": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Mots-clés pertinents pour retrouver cette notion via une recherche.",
            },
            "blocs": {
                "type": "array",
                "minItems": 3,
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": _TYPES_BLOC},
                        "titre": {"type": "string"},
                        "texte": {"type": "string"},
                        "code": {
                            "type": "string",
                            "description": "Exemple de code. Chaîne vide si le bloc n'est pas de type 'code'.",
                        },
                        "langage": {
                            "type": "string",
                            "description": "Langage de l'exemple de code. Chaîne vide si pas de code.",
                        },
                    },
                    "required": ["type", "titre", "texte", "code", "langage"],
                },
            },
        },
        "required": ["titre", "resume", "mots_cles", "blocs"],
    },
}


def generer_notion(terme: str) -> dict:
    """Génère le contenu complet d'une notion, en DEUX appels séparés :
    (1) une recherche web libre pour rassembler une matière fiable et à
    jour (_rassembler_matiere), (2) une structuration forcée (tool use) de
    cette matière en blocs pédagogiques typés.

    Pourquoi deux appels et pas un seul : forcer tool_choice sur un outil
    précis empêche le modèle d'utiliser un AUTRE outil (ici web_search)
    pendant le même appel — impossible de laisser le modèle chercher sur le
    web ET garantir une sortie structurée en un seul appel.

    Renvoie {"titre", "resume", "mots_cles", "blocs", "sources"} — "sources"
    (issu de l'étape 1) devient les ressources affichées sur la notion."""
    matiere, sources = _rassembler_matiere(terme)

    cle_api = os.environ.get("ANTHROPIC_API_KEY")
    if not cle_api:
        raise AssistantIndisponible("ANTHROPIC_API_KEY n'est pas configurée")

    modele = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

    client = Anthropic(api_key=cle_api)
    try:
        message = client.messages.create(
            model=modele,
            max_tokens=5000,
            system=_INSTRUCTION_SYSTEME_STRUCTURER_NOTION,
            tools=[_OUTIL_NOTION],
            tool_choice={"type": "tool", "name": "soumettre_notion"},
            messages=[
                {
                    "role": "user",
                    "content": f"Sujet : {terme}\n\nMatière rassemblée :\n{matiere}",
                }
            ],
        )
    except APIError as erreur:
        raise AssistantIndisponible(str(erreur)) from erreur

    for bloc in message.content:
        if bloc.type == "tool_use" and bloc.name == "soumettre_notion":
            resultat = dict(bloc.input)
            resultat["sources"] = sources
            return resultat

    raise AssistantIndisponible("Réponse inattendue de l'IA : pas de contenu reçu.")