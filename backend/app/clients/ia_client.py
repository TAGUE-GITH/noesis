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