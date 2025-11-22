from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/repertuar",
    tags=["repertuar"],
)


@router.get("/", response_model=List[schemas.SeansRepertuarOut])
def pobierz_repertuar(
    data: Optional[str] = Query(
        None,
        description="Data w formacie YYYY-MM-DD. Jeśli pusta – zwracane są wszystkie seanse.",
    ),
    id_filmu: Optional[int] = Query(
        None,
        description="Opcjonalny filtr po id_filmu.",
    ),
    db: Session = Depends(get_db),
):
    """
    UC-DB1: Pobranie repertuaru i seansów

    - Jeśli podana jest data -> filtrujemy po dacie.
    - Jeśli podany jest id_filmu -> filtrujemy po filmie.
    - Można podać oba naraz.
    """

    # Ładujemy seanse razem z powiązanym filmem i salą
    query = (
        db.query(models.Seans)
        .options(
            joinedload(models.Seans.film),
            joinedload(models.Seans.sala),
        )
    )

    if data:
        query = query.filter(models.Seans.data == data)

    if id_filmu:
        query = query.filter(models.Seans.id_filmu == id_filmu)

    seanse = query.all()

    # Budujemy listę słowników pasującą do SeansRepertuarOut
    wynik: List[dict] = []
    for seans in seanse:
        if not seans.film or not seans.sala:
            # Teoretycznie nie powinno się zdarzyć, ale dla bezpieczeństwa
            continue

        wynik.append(
            {
                "id_seansu": seans.id_seansu,
                "data": seans.data,
                "godzina": seans.godzina,
                "numer_sali": seans.sala.numer_sali,
                "film": {
                    "id_filmu": seans.film.id_filmu,
                    "tytul": seans.film.tytul,
                    "typ": seans.film.typ,
                    "czas_trwania": seans.film.czas_trwania,
                },
            }
        )

    return wynik


@router.get("/szukaj", response_model=List[schemas.SeansRepertuarOut])
def szukaj_w_repertuarze(
    q: str = Query(..., min_length=1, description="Fragment tytułu filmu"),
    data: Optional[str] = Query(
        None,
        description="Opcjonalna data w formacie YYYY-MM-DD – ogranicza wyniki do tego dnia.",
    ),
    db: Session = Depends(get_db),
):
    """
    Wyszukiwanie seansów w repertuarze po fragmencie tytułu filmu.

    Przykłady:
    - /repertuar/szukaj?q=avatar
    - /repertuar/szukaj?q=man&data=2025-01-20
    """

    query = (
        db.query(models.Seans)
        .join(models.Film, models.Seans.id_filmu == models.Film.id_filmu)
        .options(
            joinedload(models.Seans.film),
            joinedload(models.Seans.sala),
        )
        .filter(models.Film.tytul.ilike(f"%{q}%"))
    )

    if data:
        query = query.filter(models.Seans.data == data)

    seanse = query.all()

    wynik: List[dict] = []
    for seans in seanse:
        if not seans.film or not seans.sala:
            continue

        wynik.append(
            {
                "id_seansu": seans.id_seansu,
                "data": seans.data,
                "godzina": seans.godzina,
                "numer_sali": seans.sala.numer_sali,
                "film": {
                    "id_filmu": seans.film.id_filmu,
                    "tytul": seans.film.tytul,
                    "typ": seans.film.typ,
                    "czas_trwania": seans.film.czas_trwania,
                },
            }
        )

    return wynik
