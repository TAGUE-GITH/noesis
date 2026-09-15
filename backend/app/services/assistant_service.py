from app.clients import ia_client
from app.models.fiche import Fiche


def construire_contexte(fiche: Fiche) -> str:
    """Construit le texte transmis à l'IA comme contexte — uniquement les
    champs de LA fiche consultée, rien d'autre (pas les autres fiches, pas
    de connaissance externe). C'est cette restriction qui garantit que la
    réponse reste ancrée dans un contenu vérifié par Franck plutôt que dans
    les connaissances générales du modèle."""
    lignes = [
        f"Titre : {fiche.titre}",
        f"Définition : {fiche.definition}",
    ]
    if fiche.concepts_cles:
        lignes.append("Concepts clés : " + ", ".join(fiche.concepts_cles))
    if fiche.prerequis:
        lignes.append("Prérequis : " + ", ".join(fiche.prerequis))
    if fiche.pour_aller_plus_loin:
        lignes.append("Pour aller plus loin : " + fiche.pour_aller_plus_loin)
    return "\n".join(lignes)


def repondre_question(fiche: Fiche, question: str) -> dict:
    """Orchestre la réponse : construit le contexte à partir de la fiche,
    interroge l'IA, et renvoie la réponse accompagnée de sa source — pour
    que le frontend puisse toujours afficher "réponse basée sur : <fiche>"
    plutôt qu'une réponse dont l'origine est invisible."""
    contexte = construire_contexte(fiche)
    reponse = ia_client.poser_question(contexte, question)
    return {
        "reponse": reponse,
        "source": {"id": fiche.id, "titre": fiche.titre},
    }