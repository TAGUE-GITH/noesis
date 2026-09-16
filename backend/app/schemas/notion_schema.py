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


def vers_detail_notion(notion) -> dict:
    """Formate une notion complète pour l'API (US03, étendue à la
    profondeur pédagogique complète — contenu, quiz, ressources)."""
    return {
        "id": notion.id,
        "titre": notion.titre,
        "slug": notion.slug,
        "resume": notion.resume,
        "mots_cles": notion.mots_cles,
        "synonymes": notion.synonymes,
        "notions_liees": notion.notions_liees,
        "origine": notion.origine,
        "contenu": notion.contenu,
        "quiz": notion.quiz,
        "ressources": [
            {"libelle": r.libelle, "url": r.url} for r in notion.ressources
        ],
    }