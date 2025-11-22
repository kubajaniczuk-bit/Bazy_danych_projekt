from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..db import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/uzytkownicy",
    tags=["uzytkownicy"],
)

# --- konfiguracja hashowania haseł ---
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ======================================
#   REJESTRACJA / DODANIE UŻYTKOWNIKA
# ======================================
@router.post("/", response_model=schemas.UzytkownikOut, status_code=status.HTTP_201_CREATED)
def utworz_uzytkownika(
    dane: schemas.UzytkownikCreate,
    db: Session = Depends(get_db),
):
    """
    UC-DB9: Dodanie nowego użytkownika

    1. Sprawdzamy, czy email jest unikalny.
    2. Hashujemy hasło.
    3. Tworzymy rekord w tabeli Uzytkownik.
    """

    # 1. Czy email jest już zajęty?
    istnieje = (
        db.query(models.Uzytkownik)
        .filter(models.Uzytkownik.email == dane.email)
        .first()
    )
    if istnieje:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Użytkownik o podanym adresie email już istnieje.",
        )

    # 2. Tworzymy użytkownika z HASHOWANYM hasłem
    nowy = models.Uzytkownik(
        email=dane.email,
        haslo=hash_password(dane.haslo),
        imie=dane.imie,
        nazwisko=dane.nazwisko,
        typ=dane.typ,
    )

    db.add(nowy)
    db.commit()
    db.refresh(nowy)

    return nowy


# ======================================
#   LISTA UŻYTKOWNIKÓW
# ======================================
@router.get("/", response_model=List[schemas.UzytkownikOut])
def lista_uzytkownikow(
    db: Session = Depends(get_db),
):
    uzytkownicy = db.query(models.Uzytkownik).all()
    return uzytkownicy


# ======================================
#   SZCZEGÓŁY PO ID
# ======================================
@router.get("/{id_uzytkownika}", response_model=schemas.UzytkownikOut)
def pobierz_uzytkownika(
    id_uzytkownika: int,
    db: Session = Depends(get_db),
):
    uzytkownik = (
        db.query(models.Uzytkownik)
        .filter(models.Uzytkownik.id_uzytkownika == id_uzytkownika)
        .first()
    )
    if not uzytkownik:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Użytkownik o podanym id nie istnieje.",
        )
    return uzytkownik


# ======================================
#   LOGOWANIE
# ======================================
@router.post("/login")
def login(
    email: str = Body(...),
    haslo: str = Body(...),
    db: Session = Depends(get_db),
):
    """
    Proste logowanie użytkownika:
    - sprawdza, czy istnieje email
    - weryfikuje hasło (pbkdf2_sha256)
    - zwraca komunikat + dane użytkownika
    """

    uzytkownik = (
        db.query(models.Uzytkownik)
        .filter(models.Uzytkownik.email == email)
        .first()
    )

    if not uzytkownik:
        raise HTTPException(
            status_code=400,
            detail="Nieprawidłowy email lub hasło.",
        )

    # jeśli hasło w bazie nie jest hashem pbkdf2_sha256 -> verify wywali błąd
    try:
        ok = pwd_context.verify(haslo, uzytkownik.haslo)
    except Exception:
        ok = False

    if not ok:
        raise HTTPException(
            status_code=400,
            detail="Nieprawidłowy email lub hasło.",
        )

    return {
        "message": "Logowanie poprawne",
        "uzytkownik": {
            "id": uzytkownik.id_uzytkownika,
            "email": uzytkownik.email,
            "imie": uzytkownik.imie,
            "nazwisko": uzytkownik.nazwisko,
            "typ": uzytkownik.typ,
        },
    }
@router.get("/{id_uzytkownika}/rezerwacje", response_model=List[schemas.RezerwacjaUzytkownikaOut])
def lista_rezerwacji_uzytkownika(
    id_uzytkownika: int,
    db: Session = Depends(get_db),
):
    """
    Zwraca wszystkie rezerwacje danego użytkownika wraz z:
    - informacjami o seansie (film, sala, data, godzina)
    - listą miejsc (id, typ biletu, cena biletu)
    """

    uzytkownik = (
        db.query(models.Uzytkownik)
        .filter(models.Uzytkownik.id_uzytkownika == id_uzytkownika)
        .first()
    )

    if not uzytkownik:
        raise HTTPException(
            status_code=404,
            detail="Użytkownik nie istnieje."
        )

    rezerwacje = (
        db.query(models.Rezerwacja)
        .filter(models.Rezerwacja.id_uzytkownika == id_uzytkownika)
        .all()
    )

    wynik = []

    for rez in rezerwacje:
        # pobranie seansu wraz z filmem i salą
        seans = rez.seans

        # pobranie miejsc z typem biletu i ceną
        miejsca_rez = db.query(models.RezerwacjaMiejsca).filter(
            models.RezerwacjaMiejsca.id_rezerwacji == rez.id_rezerwacji
        ).all()

        miejsca_out = [
            schemas.MiejsceRezerwacjiOut(
                id_miejsca=m.id_miejsca,
                typ_biletu=m.typ_biletu,
                cena_biletu=m.cena_biletu,
            )
            for m in miejsca_rez
        ]

        wynik.append(
            schemas.RezerwacjaUzytkownikaOut(
                id_rezerwacji=rez.id_rezerwacji,
                status_rezerwacji=rez.status_rezerwacji,
                data_wygasniecia=rez.data_wygasniecia,
                seans=seans,
                miejsca=miejsca_out,
            )
        )

    return wynik
