def vers_resultat_recherche(ligne: dict) -> dict:
    """Formate une ligne de résultat de recherche pour l'API (US02).

    On n'expose que le strict nécessaire pour une liste de résultats —
    pas le contenu complet (réservé à la page de détail, US03), pas les
    colonnes internes. Le frontend ne doit jamais dépendre de la structure
    interne de la base de données.
    """
    return {
        "id": ligne["id"],
        "titre": ligne["titre"],
        "slug": ligne["slug"],
        "extrait": ligne["resume"],
    }


def vers_detail_notion(notion, notions_liees: list[dict]) -> dict:
    """Formate une notion complète pour l'API (US03, étendue à la
    profondeur pédagogique complète — contenu, quiz, ressources, notions
    liées).

    `notions_liees` est calculé par notion_service.obtenir_notions_liees
    (à partir des mots-clés partagés) plutôt que lu depuis la colonne du
    même nom sur `notion`, qui n'est jamais remplie pour l'instant."""
    return {
        "id": notion.id,
        "titre": notion.titre,
        "slug": notion.slug,
        "resume": notion.resume,
        "mots_cles": notion.mots_cles,
        "synonymes": notion.synonymes,
        "notions_liees": [
            {"titre": n["titre"], "slug": n["slug"]} for n in notions_liees
        ],
        "origine": notion.origine,
        "contenu": notion.contenu,
        "quiz": notion.quiz,
        "ressources": [
            {"libelle": r.libelle, "url": r.url} for r in notion.ressources
        ],
    }