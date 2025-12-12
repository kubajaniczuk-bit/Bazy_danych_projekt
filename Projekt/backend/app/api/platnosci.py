from __future__ import annotations

from uuid import uuid4
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from .. import schemas

from ..config_cennik import CENNIK_BILETOW


router = APIRouter(
    prefix="/platnosci",
    tags=["platnosci"],
)


def _parse_iso_datetime(dt_str: str) -> Optional[datetime]:
    """
    Bezpieczne parsowanie datetime z tekstu (ISO).
    Zwraca None jeśli nie da się sparsować.
    """
    if not dt_str:
        return None
    try:
        # obsługa np. "2025-01-01T12:30:00" (najczęściej u Was)
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None


def _czy_rezerwacja_wygasla(rez: models.Rezerwacja) -> bool:
    """
    Zwraca True jeśli rezerwacja ma ustawioną datę wygaśnięcia i już wygasła.
    """
    if not rez.data_wygasniecia:
        return False
    dt = _parse_iso_datetime(rez.data_wygasniecia)
    if dt is None:
        # jeśli format jest błędny, zachowujemy się konserwatywnie: nie blokujemy potwierdzenia,
        # ale można to zmienić na błąd 400.
        return False
    return dt < datetime.now()


def _policz_kwote_rezerwacji(db: Session, id_rezerwacji: int) -> float:
    """
    Liczy kwotę rezerwacji. Priorytet:
    1) jeśli w RezerwacjaMiejsca jest kolumna cena_biletu -> sumujemy
    2) w przeciwnym razie liczymy z typ_biletu na podstawie CENNIK_BILETOW
    """
    pozycje = (
        db.query(models.RezerwacjaMiejsca)
        .filter(models.RezerwacjaMiejsca.id_rezerwacji == id_rezerwacji)
        .all()
    )

    suma = 0.0
    for p in pozycje:
        # 1) jeśli masz już kolumnę cena_biletu w modelu:
        if hasattr(p, "cena_biletu") and p.cena_biletu is not None:
            suma += float(p.cena_biletu)
        else:
            # 2) fallback: z cennika wg typ_biletu
            cena = CENNIK_BILETOW.get(p.typ_biletu or "", None)
            if cena is None:
                # jeśli typ biletu nieznany – licz 0 (albo rzuć błąd)
                cena = 0.0
            suma += float(cena)

    return float(suma)


@router.post("/start",response_model=schemas.PlatnoscStartOut)
def start_platnosci(
    payload: schemas.PlatnoscStartIn, db: Session = Depends(get_db)
):
    """
    Start płatności (symulacja).

    Wejście:
      { "id_rezerwacji": 123 }

    Wyjście:
      {
        "payment_id": "...uuid...",
        "id_rezerwacji": 123,
        "kwota": 50.0
      }
    """
    id_rezerwacji = payload.id_rezerwacji
    if not isinstance(id_rezerwacji, int):
        raise HTTPException(status_code=400, detail="Brak lub niepoprawne id_rezerwacji (int).")

    rez = (
        db.query(models.Rezerwacja)
        .filter(models.Rezerwacja.id_rezerwacji == id_rezerwacji)
        .first()
    )
    if not rez:
        raise HTTPException(status_code=404, detail="Rezerwacja nie została znaleziona.")

    if rez.status_rezerwacji != "Oczekująca":
        raise HTTPException(
            status_code=400,
            detail=f"Nie można rozpocząć płatności. Aktualny status: {rez.status_rezerwacji}",
        )

    if _czy_rezerwacja_wygasla(rez):
        raise HTTPException(
            status_code=400,
            detail="Nie można rozpocząć płatności – rezerwacja wygasła (data_wygasniecia).",
        )

    kwota = _policz_kwote_rezerwacji(db, id_rezerwacji)

    return {
        "payment_id": str(uuid4()),
        "id_rezerwacji": id_rezerwacji,
        "kwota": kwota,
    }


@router.post("/confirm",response_model=schemas.PlatnoscConfirmOut)
def confirm_platnosci(
    payload: schemas.PlatnoscConfirmIn, db: Session = Depends(get_db)
):
    """
    Potwierdzenie płatności (symulacja webhooka).

    Wejście:
      { "id_rezerwacji": 123 }

    Efekt:
      Rezerwacja Oczekująca -> Potwierdzona (czyli zapłacona)

    Wyjście:
      { "detail": "Platnosc potwierdzona", "id_rezerwacji": 123 }
    """
    id_rezerwacji = payload.id_rezerwacji
    if not isinstance(id_rezerwacji, int):
        raise HTTPException(status_code=400, detail="Brak lub niepoprawne id_rezerwacji (int).")

    rez = (
        db.query(models.Rezerwacja)
        .filter(models.Rezerwacja.id_rezerwacji == id_rezerwacji)
        .first()
    )
    if not rez:
        raise HTTPException(status_code=404, detail="Rezerwacja nie została znaleziona.")

    if rez.status_rezerwacji != "Oczekująca":
        raise HTTPException(
            status_code=400,
            detail=f"Nie można potwierdzić płatności. Aktualny status: {rez.status_rezerwacji}",
        )

    if _czy_rezerwacja_wygasla(rez):
        raise HTTPException(
            status_code=400,
            detail="Nie można potwierdzić płatności – rezerwacja wygasła (data_wygasniecia).",
        )

    rez.status_rezerwacji = "Potwierdzona"
    db.commit()

    return {
        "detail": "Platnosc potwierdzona",
        "id_rezerwacji": id_rezerwacji,
    }
