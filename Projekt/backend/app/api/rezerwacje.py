# backend/app/api/rezerwacje.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..db import get_db
from .. import models, schemas
from ..config_cennik import CENNIK_BILETOW

router = APIRouter(
    prefix="/rezerwacje",
    tags=["rezerwacje"],
)


@router.post("/", response_model=schemas.RezerwacjaOut, status_code=status.HTTP_201_CREATED)
def utworz_rezerwacje(
    dane: schemas.RezerwacjaCreate,
    db: Session = Depends(get_db),
):
    """
    UC-DB3: Utworzenie rezerwacji

    - sprawdzamy seans
    - sprawdzamy, czy miejsca należą do sali seansu
    - sprawdzamy dostępność miejsc
    - tworzymy rezerwację ze statusem 'Oczekująca'
    - wyliczamy data_wygasniecia = teraz + 15 min
    - nadajemy cenę biletu na podstawie typu (CENNIK_BILETOW)
    """

    # --- 1. Czy seans istnieje? ---
    seans = db.query(models.Seans).filter(models.Seans.id_seansu == dane.id_seansu).first()
    if not seans:
        raise HTTPException(status_code=404, detail="Seans nie istnieje.")

    # --- 2. Czy miejsca istnieją i należą do sali tego seansu? ---
    miejsca_w_sali = (
        db.query(models.Miejsce)
        .filter(models.Miejsce.id_sali == seans.id_sali)
        .all()
    )
    id_miejsc_w_sali = {m.id_miejsca for m in miejsca_w_sali}

    for m in dane.miejsca:
        if m not in id_miejsc_w_sali:
            raise HTTPException(
                status_code=400,
                detail=f"Miejsce {m} nie należy do sali tego seansu."
            )

    # --- 3. Czy miejsca są wolne? ---
    zajete = (
        db.query(models.RezerwacjaMiejsca.id_miejsca)
        .join(models.Rezerwacja)
        .filter(
            models.Rezerwacja.id_seansu == dane.id_seansu,
            models.RezerwacjaMiejsca.id_miejsca.in_(dane.miejsca),
            models.Rezerwacja.status_rezerwacji.in_(["Oczekująca", "Potwierdzona"])
        )
        .all()
    )
    zajete_ids = {z[0] for z in zajete}

    if zajete_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Miejsca zajęte: {sorted(list(zajete_ids))}"
        )

    # --- 4. Tworzymy rekord rezerwacji ---
    teraz = datetime.now()
    data_wygasniecia = (teraz + timedelta(minutes=15)).isoformat()

    nowa_rez = models.Rezerwacja(
        id_uzytkownika=dane.id_uzytkownika,
        id_seansu=dane.id_seansu,
        id_sali=seans.id_sali,
        status_rezerwacji="Oczekująca",  # przetwarzana
        data_wygasniecia=data_wygasniecia,
    )

    db.add(nowa_rez)
    db.commit()
    db.refresh(nowa_rez)

    # --- 5. Dodajemy miejsca rezerwacji + cena biletu ---

    for id_miejsca, typ in zip(dane.miejsca, dane.typ_biletu):
        cena_jednego = CENNIK_BILETOW.get(typ, 0.0)
        rm = models.RezerwacjaMiejsca(
            id_rezerwacji=nowa_rez.id_rezerwacji,
            id_miejsca=id_miejsca,
            typ_biletu=typ,
            cena_biletu=cena_jednego,
        )
        db.add(rm)

    db.commit()

    return schemas.RezerwacjaOut(
        id_rezerwacji=nowa_rez.id_rezerwacji,
        id_uzytkownika=nowa_rez.id_uzytkownika,
        id_seansu=nowa_rez.id_seansu,
        status_rezerwacji=nowa_rez.status_rezerwacji,
        miejsca=dane.miejsca,
    )


@router.patch("/{id_rezerwacji}/potwierdz", response_model=schemas.RezerwacjaOut)
def potwierdz_rezerwacje(
    id_rezerwacji: int,
    db: Session = Depends(get_db),
):
    """
    UC-DB4: Potwierdzenie rezerwacji
    """

    rez = (
        db.query(models.Rezerwacja)
        .filter(models.Rezerwacja.id_rezerwacji == id_rezerwacji)
        .first()
    )
    if not rez:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezerwacja o podanym id nie istnieje.",
        )

    if rez.status_rezerwacji != "Oczekująca":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rezerwacja nie jest w statusie 'Oczekująca' (aktualny status: {rez.status_rezerwacji}).",
        )

    rez.status_rezerwacji = "Potwierdzona"
    db.commit()
    db.refresh(rez)

    miejsca_rez = (
        db.query(models.RezerwacjaMiejsca)
        .filter(models.RezerwacjaMiejsca.id_rezerwacji == id_rezerwacji)
        .all()
    )
    id_miejsc = [rm.id_miejsca for rm in miejsca_rez]

    return schemas.RezerwacjaOut(
        id_rezerwacji=rez.id_rezerwacji,
        id_uzytkownika=rez.id_uzytkownika,
        id_seansu=rez.id_seansu,
        status_rezerwacji=rez.status_rezerwacji,
        miejsca=id_miejsc,
    )


@router.patch("/{id_rezerwacji}/anuluj", response_model=schemas.RezerwacjaOut)
def anuluj_rezerwacje(
    id_rezerwacji: int,
    db: Session = Depends(get_db),
):
    """
    UC-DB5: Anulowanie rezerwacji przez użytkownika
    """

    rez = (
        db.query(models.Rezerwacja)
        .filter(models.Rezerwacja.id_rezerwacji == id_rezerwacji)
        .first()
    )
    if not rez:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezerwacja o podanym id nie istnieje.",
        )

    if rez.status_rezerwacji not in ["Oczekująca", "Potwierdzona"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Rezerwację można anulować tylko ze statusu 'Oczekująca' lub 'Potwierdzona'. "
                f"Aktualny status: {rez.status_rezerwacji}."
            ),
        )

    miejsca_rez = (
        db.query(models.RezerwacjaMiejsca)
        .filter(models.RezerwacjaMiejsca.id_rezerwacji == id_rezerwacji)
        .all()
    )
    id_miejsc = [rm.id_miejsca for rm in miejsca_rez]

    db.query(models.RezerwacjaMiejsca).filter(
        models.RezerwacjaMiejsca.id_rezerwacji == id_rezerwacji
    ).delete(synchronize_session=False)

    rez.status_rezerwacji = "Anulowana"
    db.commit()
    db.refresh(rez)

    return schemas.RezerwacjaOut(
        id_rezerwacji=rez.id_rezerwacji,
        id_uzytkownika=rez.id_uzytkownika,
        id_seansu=rez.id_seansu,
        status_rezerwacji=rez.status_rezerwacji,
        miejsca=id_miejsc,
    )


@router.post("/sprzataj_wygasle")
def sprzataj_wygasle_rezerwacje(
    db: Session = Depends(get_db),
):
    """
    UC-DB8: Sprzątanie rezerwacji wygasłych
    """

    teraz = datetime.now()
    wygasle_ids: List[int] = []
    bledne_formaty: List[int] = []

    rezerwacje_kandydaci = (
        db.query(models.Rezerwacja)
        .filter(
            models.Rezerwacja.status_rezerwacji == "Oczekująca",
            models.Rezerwacja.data_wygasniecia.isnot(None),
        )
        .all()
    )

    for rez in rezerwacje_kandydaci:
        if not rez.data_wygasniecia:
            continue

        try:
            data_wyg = datetime.fromisoformat(rez.data_wygasniecia)
        except ValueError:
            bledne_formaty.append(rez.id_rezerwacji)
            continue

        if data_wyg < teraz:
            wygasle_ids.append(rez.id_rezerwacji)

            db.query(models.RezerwacjaMiejsca).filter(
                models.RezerwacjaMiejsca.id_rezerwacji == rez.id_rezerwacji
            ).delete(synchronize_session=False)

            rez.status_rezerwacji = "Expired"

    db.commit()

    return {
        "liczba_wygaslcych": len(wygasle_ids),
        "id_wygaslcych": wygasle_ids,
        "bledny_format_data_wygasniecia": bledne_formaty,
    }

