from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..db import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/seanse",
    tags=["seanse"],
)


def _map_status_rezerwacji_na_status_miejsca(status_rezerwacji: str) -> str | None:
    """
    Zamienia status rezerwacji (z tabeli Rezerwacja.status_rezerwacji)
    na status miejsca zgodny z UC-DB2.
    """
    if status_rezerwacji == "Oczekująca":
        return "Zarezerwowane"
    if status_rezerwacji == "Potwierdzona":
        return "Opłacone"
    return None

from fastapi import Query

@router.get("/", response_model=List[schemas.SeansOut])
def lista_seansow(
    data: str | None = Query(None, description="Filtruj po dacie (YYYY-MM-DD)"),
    id_filmu: int | None = Query(None, description="Filtruj po ID filmu"),
    db: Session = Depends(get_db),
):
    """
    Lista seansów z opcjonalnym filtrowaniem:
    - /seanse -> wszystkie seanse
    - /seanse?data=2025-01-20
    - /seanse?id_filmu=3
    - /seanse?data=2025-01-20&id_filmu=3
    """

    zapytanie = db.query(models.Seans)

    if data:
        zapytanie = zapytanie.filter(models.Seans.data == data)

    if id_filmu:
        zapytanie = zapytanie.filter(models.Seans.id_filmu == id_filmu)

    return zapytanie.all()


# =======================
# UC-DB2: mapa miejsc
# =======================
@router.get("/{id_seansu}/miejsca", response_model=List[schemas.MiejsceSeansuOut])
def pobierz_miejsca_dla_seansu(
    id_seansu: int,
    db: Session = Depends(get_db),
):
    """
    UC-DB2: Mapa dostępności miejsc dla seansu.
    """

    seans = (
        db.query(models.Seans)
        .filter(models.Seans.id_seansu == id_seansu)
        .first()
    )
    if not seans:
        raise HTTPException(status_code=404, detail="Seans nie został znaleziony")

    miejsca = (
        db.query(models.Miejsce)
        .filter(models.Miejsce.id_sali == seans.id_sali)
        .all()
    )

    if not miejsca:
        return []

    rezerwacje_miejsca = (
        db.query(
            models.RezerwacjaMiejsca.id_miejsca,
            models.Rezerwacja.status_rezerwacji,
        )
        .join(
            models.Rezerwacja,
            models.RezerwacjaMiejsca.id_rezerwacji == models.Rezerwacja.id_rezerwacji,
        )
        .filter(models.Rezerwacja.id_seansu == id_seansu)
        .all()
    )

    statusy_miejsc: Dict[int, str] = {m.id_miejsca: "Wolne" for m in miejsca}
    priorytet = {"Wolne": 0, "Zarezerwowane": 1, "Opłacone": 2}

    for id_miejsca, status_rezerwacji in rezerwacje_miejsca:
        status_miejsca = _map_status_rezerwacji_na_status_miejsca(status_rezerwacji)
        if status_miejsca is None:
            continue

        obecny_status = statusy_miejsc.get(id_miejsca, "Wolne")

        if priorytet[status_miejsca] > priorytet[obecny_status]:
            statusy_miejsc[id_miejsca] = status_miejsca

    wynik = [
        {
            "id_miejsca": m.id_miejsca,
            "rzad": m.rzad,
            "numer": m.numer,
            "status": statusy_miejsc.get(m.id_miejsca, "Wolne"),
        }
        for m in miejsca
    ]

    return wynik


# =======================
# Dodawanie seansu
# =======================
@router.post("/", response_model=schemas.SeansOut, status_code=status.HTTP_201_CREATED)
def dodaj_seans(
    seans_in: schemas.SeansCreate,
    db: Session = Depends(get_db),
):
    """
    UC-DB6 (część): dodawanie seansu przez operatora.
    """

    film = (
        db.query(models.Film)
        .filter(models.Film.id_filmu == seans_in.id_filmu)
        .first()
    )
    if not film:
        raise HTTPException(status_code=404, detail="Film o podanym id nie istnieje")

    sala = (
        db.query(models.Sala)
        .filter(models.Sala.id_sali == seans_in.id_sali)
        .first()
    )
    if not sala:
        raise HTTPException(status_code=404, detail="Sala o podanym id nie istnieje")

    konflikt = (
        db.query(models.Seans)
        .filter(
            models.Seans.id_sali == seans_in.id_sali,
            models.Seans.data == seans_in.data,
            models.Seans.godzina == seans_in.godzina,
        )
        .first()
    )
    if konflikt:
        raise HTTPException(
            status_code=400,
            detail="W tej sali jest już seans o podanej dacie i godzinie.",
        )

    nowy_seans = models.Seans(
        id_filmu=seans_in.id_filmu,
        id_sali=seans_in.id_sali,
        data=seans_in.data,
        godzina=seans_in.godzina,
    )

    db.add(nowy_seans)
    db.commit()
    db.refresh(nowy_seans)

    return nowy_seans


# =======================
# Edycja seansu
# =======================
@router.patch("/{id_seansu}", response_model=schemas.SeansOut)
def edytuj_seans(
    id_seansu: int,
    seans_update: schemas.SeansUpdate,
    db: Session = Depends(get_db),
):
    """
    Część UC-DB6: edycja seansu.
    """

    seans = (
        db.query(models.Seans)
        .filter(models.Seans.id_seansu == id_seansu)
        .first()
    )
    if not seans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seans o podanym id nie istnieje.",
        )

    # Ustalamy „nowe” wartości (po aktualizacji)
    new_id_filmu = seans_update.id_filmu if seans_update.id_filmu is not None else seans.id_filmu
    new_id_sali = seans_update.id_sali if seans_update.id_sali is not None else seans.id_sali
    new_data = seans_update.data if seans_update.data is not None else seans.data
    new_godzina = seans_update.godzina if seans_update.godzina is not None else seans.godzina

    # Jeśli zmieniamy film -> sprawdź, czy istnieje
    if seans_update.id_filmu is not None:
        film = (
            db.query(models.Film)
            .filter(models.Film.id_filmu == new_id_filmu)
            .first()
        )
        if not film:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nowy film o podanym id nie istnieje.",
            )

    # Jeśli zmieniamy salę -> sprawdź, czy istnieje
    if seans_update.id_sali is not None:
        sala = (
            db.query(models.Sala)
            .filter(models.Sala.id_sali == new_id_sali)
            .first()
        )
        if not sala:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nowa sala o podanym id nie istnieje.",
            )

    # Sprawdzenie konfliktu (inna projekcja w tej samej sali, o tej samej porze)
    konflikt = (
        db.query(models.Seans)
        .filter(
            models.Seans.id_sali == new_id_sali,
            models.Seans.data == new_data,
            models.Seans.godzina == new_godzina,
            models.Seans.id_seansu != id_seansu,  # pomijamy aktualny seans
        )
        .first()
    )

    if konflikt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="W tej sali jest już inny seans o podanej dacie i godzinie.",
        )

    # Aktualizacja pól
    seans.id_filmu = new_id_filmu
    seans.id_sali = new_id_sali
    seans.data = new_data
    seans.godzina = new_godzina

    db.commit()
    db.refresh(seans)

    return seans


# =======================
# Usuwanie seansu
# =======================
@router.delete("/{id_seansu}")
def usun_seans(
    id_seansu: int,
    db: Session = Depends(get_db),
):
    """
    Część UC-DB6: usuwanie seansu.

    Uwaga: w bazie masz ON DELETE CASCADE na Rezerwacjach,
    więc usunięcie seansu usunie też powiązane rezerwacje.
    """

    seans = (
        db.query(models.Seans)
        .filter(models.Seans.id_seansu == id_seansu)
        .first()
    )
    if not seans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seans o podanym id nie istnieje.",
        )

    db.delete(seans)
    db.commit()

    return {"detail": "Seans został usunięty."}


@router.post("/sprzataj_wygasle")
def sprzataj_wygasle_seanse(db: Session = Depends(get_db)):
    """
    Usuwa seanse, których data i godzina są wcześniejsze niż aktualny czas.
    Rezerwacje i miejsca powiązane usuwane są kaskadowo.
    """

    teraz = datetime.now()

    seanse = db.query(models.Seans).all()
    usuniete = 0

    for seans in seanse:
        try:
            data_seansu = datetime.fromisoformat(
                f"{seans.data} {seans.godzina}"
            )
        except ValueError:
            # jeśli format daty/godziny jest błędny – pomijamy
            continue

        if data_seansu < teraz:
            db.delete(seans)
            usuniete += 1

    db.commit()

    return {
        "detail": "Sprzątanie wygasłych seansów zakończone",
        "usuniete_seanse": usuniete,
    }