from app.repositories import fiche_repository


def obtenir_detail(fiche_id: int):
    return fiche_repository.obtenir_par_id(fiche_id)