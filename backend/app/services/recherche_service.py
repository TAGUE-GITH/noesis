from app.repositories import fiche_repository


def rechercher_fiches(terme: str) -> list[dict]:
    """Logique métier de la recherche (US01/US02). Pour l'instant, elle
    nettoie l'entrée et délègue au repository — mais c'est ici, et pas
    dans la route, que viendront les futures règles métier (longueur
    minimale, limite de résultats, journalisation...). La route ne
    changera pas quand ça arrivera."""
    terme_nettoye = terme.strip()
    if not terme_nettoye:
        return []
    return fiche_repository.rechercher(terme_nettoye)