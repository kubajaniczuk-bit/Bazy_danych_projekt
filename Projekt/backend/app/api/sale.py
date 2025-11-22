from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/sale",
    tags=["sale"],
)


# =======================
# Dodawanie sali
# =======================
@router.post("/", response_model=schemas.SalaOut, status_code=status.HTTP_201_CREATED)
def dodaj_sale(
    sala_in: schemas.SalaCreate,
    db: Session = Depends(get_db),
):
    """
    UC: Dodawanie sali przez operatora.

    1. Operator podaje numer sali.
    2. System sprawdza, czy numer sali nie jest już zajęty.
    3. System tworzy rekord w tabeli Sala.
    """

    istnieje = (
        db.query(models.Sala)
        .filter(models.Sala.numer_sali == sala_in.numer_sali)
        .first()
    )
    if istnieje:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sala o podanym numerze już istnieje.",
        )

    nowa_sala = models.Sala(
        numer_sali=sala_in.numer_sali,
    )

    db.add(nowa_sala)
    db.commit()
    db.refresh(nowa_sala)

    return nowa_sala


# =======================
# Lista sal
# =======================
@router.get("/", response_model=List[schemas.SalaOut])
def lista_sal(
    db: Session = Depends(get_db),
):
    """
    Lista wszystkich sal w systemie.
    Przydatne przy konfiguracji i wyborze sali przy tworzeniu seansu.
    """
    sale = db.query(models.Sala).all()
    return sale


# =======================
# Generowanie miejsc w sali
# =======================
@router.post("/{id_sali}/generuj_miejsca")
def generuj_miejsca_w_sali(
    id_sali: int,
    rzedy: int = Query(..., gt=0, description="Liczba rzędów w sali"),
    na_rzad: int = Query(..., gt=0, description="Liczba miejsc w jednym rzędzie"),
    nadpisz: bool = Query(
        False,
        description=(
            "Jeśli True – najpierw usunie istniejące miejsca w sali, "
            "a potem wygeneruje nowe. Domyślnie False (chroni przed przypadkowym nadpisaniem)."
        ),
    ),
    db: Session = Depends(get_db),
):
    """
    Generuje układ miejsc dla danej sali.

    - Sprawdza, czy sala istnieje.
    - Jeśli sala ma już miejsca i nadpisz=False -> błąd.
    - Jeśli nadpisz=True -> usuwa stare miejsca i tworzy nowe.
    - Tworzy miejsca w tabeli Miejsce:
        rząd:    1 .. rzedy
        numer:   1 .. na_rzad
        status:  'Wolne'
    """

    # 1. Czy sala istnieje?
    sala = (
        db.query(models.Sala)
        .filter(models.Sala.id_sali == id_sali)
        .first()
    )
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala o podanym id nie istnieje.",
        )

    # 2. Sprawdzenie, czy sala ma już miejsca
    istniejące_miejsca_count = (
        db.query(models.Miejsce)
        .filter(models.Miejsce.id_sali == id_sali)
        .count()
    )

    if istniejące_miejsca_count > 0 and not nadpisz:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Sala ma już zdefiniowane miejsca (liczba miejsc: {istniejące_miejsca_count}). "
                f"Użyj parametru nadpisz=true, jeśli chcesz je nadpisać."
            ),
        )

    # 3. Jeśli nadpisz=True – usuwamy stare miejsca
    if istniejące_miejsca_count > 0 and nadpisz:
        db.query(models.Miejsce).filter(
            models.Miejsce.id_sali == id_sali
        ).delete(synchronize_session=False)
        db.commit()

    # 4. Generowanie nowych miejsc
    nowe_miejsca = []
    for rzad in range(1, rzedy + 1):
        for numer in range(1, na_rzad + 1):
            nowe_miejsca.append(
                models.Miejsce(
                    id_sali=id_sali,
                    rzad=rzad,
                    numer=numer,
                    status="Wolne",
                )
            )

    db.add_all(nowe_miejsca)
    db.commit()

    return {
        "id_sali": id_sali,
        "rzedy": rzedy,
        "miejsca_w_rzedzie": na_rzad,
        "liczba_wygenerowanych_miejsc": len(nowe_miejsca),
        "nadpisano_poprzednie": istniejące_miejsca_count > 0 and nadpisz,
    }
