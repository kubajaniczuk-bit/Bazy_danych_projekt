from pydantic import BaseModel, Field
from typing import Optional, List

# ---------- FILM ----------
class FilmOut(BaseModel):
    id_filmu: int
    tytul: str
    typ: Optional[str] = None
    czas_trwania: int

    class Config:
        from_attributes = True  # Pydantic v2


# ---------- SEANS W REPERTUARZE ----------
class SeansRepertuarOut(BaseModel):
    id_seansu: int
    data: str
    godzina: str
    numer_sali: int
    film: FilmOut

    class Config:
        from_attributes = True  # Pydantic v2

class MiejsceSeansuOut(BaseModel):
    id_miejsca: int
    rzad: int
    numer: int
    status: str  # "Wolne", "Zarezerwowane", "Opłacone"

    class Config:
        from_attributes = True


class SeansCreate(BaseModel):
    """Dane potrzebne do utworzenia seansu (wysyłane przez operatora)."""
    id_filmu: int
    id_sali: int
    data: str    # np. "2025-12-24"
    godzina: str # np. "18:30"


class SeansOut(BaseModel):
    """Dane zwracane po utworzeniu seansu."""
    id_seansu: int
    id_filmu: int
    id_sali: int
    data: str
    godzina: str

    class Config:
        from_attributes = True


class FilmCreate(BaseModel):
    """Dane wymagane do utworzenia nowego filmu (operator)."""
    tytul: str = Field(..., min_length=1)
    typ: Optional[str] = None
    czas_trwania: int = Field(..., gt=0, description="Czas trwania w minutach")

# --------------------------
# Rezerwacja (UC-DB5)
# --------------------------

class RezerwacjaCreate(BaseModel):
    id_uzytkownika: int
    id_seansu: int
    miejsca: List[int]  # lista id_miejsca
    typ_biletu: Optional[str] = "normalny"


class RezerwacjaOut(BaseModel):
    id_rezerwacji: int
    id_uzytkownika: int
    id_seansu: int
    status_rezerwacji: str
    miejsca: List[int]

    class Config:
        from_attributes = True

class SalaCreate(BaseModel):
    numer_sali: int = Field(..., gt=0, description="Numer sali (np. 1, 2, 3)")


class SalaOut(BaseModel):
    id_sali: int
    numer_sali: int

    class Config:
        from_attributes = True

# --------------------------
# Użytkownik
# --------------------------

class UzytkownikCreate(BaseModel):
    email: str
    haslo: str
    imie: str
    nazwisko: str
    typ: Optional[int] = 0  # np. 0 - klient, 1 - pracownik


class UzytkownikOut(BaseModel):
    id_uzytkownika: int
    email: str
    imie: str
    nazwisko: str
    typ: Optional[int]

    class Config:
        from_attributes = True

# --------------------------
# Aktualizacja filmu
# --------------------------

class FilmUpdate(BaseModel):
    tytul: Optional[str] = None
    typ: Optional[str] = None
    czas_trwania: Optional[int] = Field(
        None, gt=0, description="Czas trwania w minutach"
    )


# --------------------------
# Aktualizacja seansu
# --------------------------

class SeansUpdate(BaseModel):
    id_filmu: Optional[int] = None
    id_sali: Optional[int] = None
    data: Optional[str] = None
    godzina: Optional[str] = None

class RaportSprzedazyDzienny(BaseModel):
    data: str
    liczba_biletow: int
    przychod: float


class MiejsceRezerwacjiOut(BaseModel):
    id_miejsca: int
    typ_biletu: str | None = None
    cena_biletu: float | None = None


class RezerwacjaUzytkownikaOut(BaseModel):
    id_rezerwacji: int
    status_rezerwacji: str
    data_wygasniecia: str | None
    seans: SeansOut
    miejsca: List[MiejsceRezerwacjiOut]

    class Config:
        from_attributes = True

class PlatnoscStartIn(BaseModel):
    id_rezerwacji: int


class PlatnoscStartOut(BaseModel):
    payment_id: str
    id_rezerwacji: int
    kwota: float


class PlatnoscConfirmIn(BaseModel):
    id_rezerwacji: int


class PlatnoscConfirmOut(BaseModel):
    detail: str
    id_rezerwacji: int