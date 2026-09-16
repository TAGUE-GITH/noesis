from app.clients import ia_client
from app.models.notion import Notion


def construire_contexte(notion: Notion) -> str:
    """Construit le texte transmis à l'IA comme contexte — uniquement le
    contenu de CETTE notion, rien d'autre (pas les autres notions, pas de
    connaissance externe). C'est cette restriction qui garantit que la
    réponse reste ancrée dans un contenu déjà affiché au visiteur plutôt
    que dans les connaissances générales du modèle."""
    lignes = [f"Titre : {notion.titre}", f"Résumé : {notion.resume}"]
    for bloc in notion.contenu:
        titre_bloc = bloc.get("titre") or ""
        texte_bloc = bloc.get("texte") or ""
        lignes.append(f"{titre_bloc} : {texte_bloc}".strip(" :"))
        if bloc.get("code"):
            lignes.append(f"Code ({bloc.get('langage', '')}) :\n{bloc['code']}")
        if bloc.get("etapes"):
            lignes.append("Étapes : " + " -> ".join(bloc["etapes"]))
    return "\n".join(lignes)


def repondre_question(notion: Notion, question: str) -> dict:
    """Orchestre la réponse : construit le contexte à partir de la notion,
    interroge l'IA, et renvoie la réponse accompagnée de sa source — pour
    que le frontend puisse toujours afficher "réponse basée sur : <notion>"
    plutôt qu'une réponse dont l'origine est invisible."""
    contexte = construire_contexte(notion)
    reponse = ia_client.poser_question(contexte, question)
    return {
        "reponse": reponse,
        "source": {"slug": notion.slug, "titre": notion.titre},
    }


def generer_quiz(notion: Notion) -> dict:
    """Même principe que repondre_question : le quiz est généré à partir du
    contenu de CETTE notion uniquement, donc la correction (bonne réponse +
    explication) reste ancrée dans un contenu déjà affiché. Un nouvel appel
    IA à chaque clic sur "Générer un quiz" (pas de mise en cache ici) : un
    quiz de base réutilisable pourra être introduit plus tard (incrément
    exercices) sans changer cette fonction."""
    contexte = construire_contexte(notion)
    questions = ia_client.generer_quiz(contexte)
    return {
        "questions": questions,
        "source": {"slug": notion.slug, "titre": notion.titre},
    }