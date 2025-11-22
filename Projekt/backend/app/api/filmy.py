from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/filmy",
    tags=["filmy"],
)


# =======================
# UC: Dodawanie filmu
# =======================
@router.post("/", response_model=schemas.FilmOut, status_code=status.HTTP_201_CREATED)
def dodaj_film(
    film_in: schemas.FilmCreate,
    db: Session = Depends(get_db),
):
    """
    UC: Dodawanie filmu przez operatora.
    """

    # Sprawdzenie, czy film o takim tytule już istnieje
    istnieje = (
        db.query(models.Film)
        .filter(models.Film.tytul == film_in.tytul)
        .first()
    )
    if istnieje:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Film o podanym tytule już istnieje.",
        )

    nowy_film = models.Film(
        tytul=film_in.tytul,
        typ=film_in.typ,
        czas_trwania=film_in.czas_trwania,
    )

    db.add(nowy_film)
    db.commit()
    db.refresh(nowy_film)

    return nowy_film


# =======================
# Lista filmów
# =======================
@router.get("/", response_model=List[schemas.FilmOut])
def lista_filmow(
    db: Session = Depends(get_db),
):
    filmy = db.query(models.Film).all()
    return filmy


# =======================
# Edycja filmu
# =======================
@router.patch("/{id_filmu}", response_model=schemas.FilmOut)
def edytuj_film(
    id_filmu: int,
    film_update: schemas.FilmUpdate,
    db: Session = Depends(get_db),
):
    """
    Część UC-DB6: edycja filmu.
    """

    film = (
        db.query(models.Film)
        .filter(models.Film.id_filmu == id_filmu)
        .first()
    )
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film o podanym id nie istnieje.",
        )

    # Jeśli zmieniamy tytuł, sprawdź unikalność
    if film_update.tytul and film_update.tytul != film.tytul:
        istnieje = (
            db.query(models.Film)
            .filter(models.Film.tytul == film_update.tytul)
            .first()
        )
        if istnieje:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Film o nowym tytule już istnieje.",
            )

    if film_update.tytul is not None:
        film.tytul = film_update.tytul
    if film_update.typ is not None:
        film.typ = film_update.typ
    if film_update.czas_trwania is not None:
        film.czas_trwania = film_update.czas_trwania

    db.commit()
    db.refresh(film)

    return film


# =======================
# Usuwanie filmu
# =======================
@router.delete("/{id_filmu}")
def usun_film(
    id_filmu: int,
    db: Session = Depends(get_db),
):
    """
    Część UC-DB6: usuwanie filmu.

    Dla bezpieczeństwa blokujemy usunięcie filmu,
    jeśli są z nim powiązane seanse.
    """

    film = (
        db.query(models.Film)
        .filter(models.Film.id_filmu == id_filmu)
        .first()
    )
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film o podanym id nie istnieje.",
        )

    # Sprawdzenie, czy film ma powiązane seanse
    liczba_seansow = (
        db.query(models.Seans)
        .filter(models.Seans.id_filmu == id_filmu)
        .count()
    )

    if liczba_seansow > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Nie można usunąć filmu, który ma powiązane seanse. "
                "Najpierw usuń seanse dla tego filmu."
            ),
        )

    db.delete(film)
    db.commit()

    return {"detail": "Film został usunięty."}

@router.get("/szukaj", response_model=List[schemas.FilmOut])
def szukaj_filmow(
    q: str = Query(..., min_length=1, description="Fragment tytułu filmu"),
    db: Session = Depends(get_db),
):
    """
    Wyszukiwanie filmów po fragmencie tytułu.

    Przykłady:
    - /filmy/szukaj?q=avatar
    - /filmy/szukaj?q=man
    """

    # SQLite jest z natury case-insensitive dla LIKE, ilike też zadziała
    filmy = (
        db.query(models.Film)
        .filter(models.Film.tytul.ilike(f"%{q}%"))
        .all()
    )

    return filmy