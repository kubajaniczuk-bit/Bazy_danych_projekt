# backend/app/api/raporty.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/raport",
    tags=["raporty"],
)


@router.get("/sprzedaz-dzienna", response_model=schemas.RaportSprzedazyDzienny)
def raport_sprzedaz_dzienna(
    data: str = Query(..., description="Dzień w formacie YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """
    UC-DB7: Raport sprzedaży dziennej

    - bierzemy tylko rezerwacje 'Potwierdzona'
    - łączymy z seansami po id_seansu
    - filtrujemy po dacie seansu
    - liczymy liczbę sprzedanych biletów (miejsc)
    - sumujemy przychód na podstawie cena_biletu
    """

    liczba_biletow, przychod = (
        db.query(
            func.count(models.RezerwacjaMiejsca.id_miejsca),
            func.coalesce(func.sum(models.RezerwacjaMiejsca.cena_biletu), 0.0),
        )
        .join(
            models.Rezerwacja,
            models.RezerwacjaMiejsca.id_rezerwacji == models.Rezerwacja.id_rezerwacji,
        )
        .join(
            models.Seans,
            models.Rezerwacja.id_seansu == models.Seans.id_seansu,
        )
        .filter(
            models.Rezerwacja.status_rezerwacji == "Potwierdzona",
            models.Seans.data == data,
        )
        .one()
    )

    return schemas.RaportSprzedazyDzienny(
        data=data,
        liczba_biletow=liczba_biletow,
        przychod=float(przychod),
    )
