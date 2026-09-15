def vers_resultat_recherche(ligne: dict) -> dict:
    return {"id": ligne["id"], "titre": ligne["titre"], "extrait": ligne["resume"]}


def vers_detail_fiche(fiche) -> dict:
    return {
        "id": fiche.id,
        "titre": fiche.titre,
        "definition": fiche.definition,
        "resume": fiche.resume,
        "concepts_cles": fiche.concepts_cles,
        "prerequis": fiche.prerequis,
        "pour_aller_plus_loin": fiche.pour_aller_plus_loin,
        "mots_cles": fiche.mots_cles,
        "ressources": [{"libelle": r.libelle, "url": r.url} for r in fiche.ressources],
    }