import os

from anthropic import Anthropic, APIError


class AssistantIndisponible(Exception):
    """Levée quand l'assistant IA ne peut pas répondre : clé API absente,
    erreur réseau, ou erreur renvoyée par l'API Anthropic. Le reste de
    l'application n'a pas besoin de savoir POURQUOI ça a échoué — juste que
    ça a échoué, pour afficher un message propre plutôt qu'un 500 brut."""


_INSTRUCTION_SYSTEME = (
    "Tu es l'assistant pédagogique de Yamia, un moteur de recherche "
    "orienté apprentissage. Un visiteur consulte une fiche de connaissance "
    "et te pose une question à ce sujet.\n\n"
    "Règle stricte : réponds UNIQUEMENT à partir du contexte fourni "
    "ci-dessous, qui provient de cette fiche. Si la question ne peut pas "
    "être répondue avec ce contexte, dis clairement que cette information "
    "ne se trouve pas dans la fiche, sans inventer de réponse et sans "
    "utiliser de connaissances extérieures à ce contexte.\n\n"
    "Réponds de façon concise (quelques phrases), en français."
)


def poser_question(contexte: str, question: str) -> str:
    """Envoie la question à Claude avec le contexte de la fiche, et renvoie
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
                    "content": f"Contexte (fiche) :\n{contexte}\n\nQuestion : {question}",
                }
            ],
        )
    except APIError as erreur:
        raise AssistantIndisponible(str(erreur)) from erreur

    return message.content[0].text


_INSTRUCTION_SYSTEME_QUIZ = (
    "Tu génères un quiz de compréhension à partir UNIQUEMENT du contexte "
    "fourni (une fiche de connaissance vérifiée). Chaque question doit "
    "pouvoir être répondue avec ce contexte seul, sans connaissance "
    "extérieure. Propose des questions à choix multiples, une seule bonne "
    "réponse par question, et une explication courte de la bonne réponse, "
    "toujours basée sur le contexte. En français."
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
    """Génère un quiz à choix multiples à partir du contexte de la fiche.
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
            messages=[{"role": "user", "content": f"Contexte (fiche) :\n{contexte}"}],
        )
    except APIError as erreur:
        raise AssistantIndisponible(str(erreur)) from erreur

    for bloc in message.content:
        if bloc.type == "tool_use" and bloc.name == "soumettre_quiz":
            return bloc.input["questions"]

    # Ne devrait normalement jamais arriver puisqu'on force tool_choice,
    # mais on ne laisse jamais un cas non prévu remonter comme un 500 brut.
    raise AssistantIndisponible("Réponse inattendue de l'IA : pas de quiz reçu.")