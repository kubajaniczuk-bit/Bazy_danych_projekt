from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Float,  
)
from sqlalchemy.orm import relationship

from .db import Base


# ======================================
#              TABELA: UZYTKOWNIK
# ======================================
class Uzytkownik(Base):
    __tablename__ = "Uzytkownik"

    id_uzytkownika = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    haslo = Column(String, nullable=False)
    imie = Column(String, nullable=False)
    nazwisko = Column(String, nullable=False)
    typ = Column(Integer)  # np. 0 - klient, 1 - pracownik itd.

    rezerwacje = relationship("Rezerwacja", back_populates="uzytkownik")


# ======================================
#              TABELA: SALA
# ======================================
class Sala(Base):
    __tablename__ = "Sala"

    id_sali = Column(Integer, primary_key=True, index=True)
    numer_sali = Column(Integer, nullable=False)

    miejsca = relationship("Miejsce", back_populates="sala", cascade="all, delete-orphan")
    seanse = relationship("Seans", back_populates="sala", cascade="all, delete-orphan")
    rezerwacje = relationship("Rezerwacja", back_populates="sala", cascade="all, delete-orphan")


# ======================================
#              TABELA: MIEJSCE
# ======================================
class Miejsce(Base):
    __tablename__ = "Miejsce"

    id_miejsca = Column(Integer, primary_key=True, index=True)
    id_sali = Column(Integer, ForeignKey("Sala.id_sali", ondelete="CASCADE"), nullable=False)
    rzad = Column(Integer, nullable=False)
    numer = Column(Integer, nullable=False)
    status = Column(String, nullable=True, default="Wolne")

    sala = relationship("Sala", back_populates="miejsca")
    rezerwacje_miejsca = relationship(
        "RezerwacjaMiejsca", back_populates="miejsce", cascade="all, delete-orphan"
    )


# ======================================
#              TABELA: FILM
# ======================================
class Film(Base):
    __tablename__ = "Film"

    id_filmu = Column(Integer, primary_key=True, index=True)
    tytul = Column(String, nullable=False)
    typ = Column(String, nullable=True)
    czas_trwania = Column(Integer, nullable=False)

    seanse = relationship("Seans", back_populates="film", cascade="all, delete-orphan")


# ======================================
#              TABELA: SEANS
# ======================================
class Seans(Base):
    __tablename__ = "Seans"

    id_seansu = Column(Integer, primary_key=True, index=True)
    id_filmu = Column(Integer, ForeignKey("Film.id_filmu", ondelete="CASCADE"), nullable=False)
    id_sali = Column(Integer, ForeignKey("Sala.id_sali", ondelete="CASCADE"), nullable=False)
    data = Column(String, nullable=False)     # TEXT w SQLite
    godzina = Column(String, nullable=False)  # TEXT w SQLite

    film = relationship("Film", back_populates="seanse")
    sala = relationship("Sala", back_populates="seanse")
    rezerwacje = relationship("Rezerwacja", back_populates="seans", cascade="all, delete-orphan")


# ======================================
#              TABELA: REZERWACJA
# ======================================
class Rezerwacja(Base):
    __tablename__ = "Rezerwacja"

    id_rezerwacji = Column(Integer, primary_key=True, index=True)
    id_uzytkownika = Column(
        Integer, ForeignKey("Uzytkownik.id_uzytkownika", ondelete="CASCADE"), nullable=False
    )
    id_sali = Column(
        Integer, ForeignKey("Sala.id_sali", ondelete="CASCADE"), nullable=False
    )
    id_seansu = Column(
        Integer, ForeignKey("Seans.id_seansu", ondelete="CASCADE"), nullable=False
    )
    status_rezerwacji = Column(String, nullable=True, default="Oczekująca")
    data_wygasniecia = Column(String, nullable=True)

    uzytkownik = relationship("Uzytkownik", back_populates="rezerwacje")
    sala = relationship("Sala", back_populates="rezerwacje")
    seans = relationship("Seans", back_populates="rezerwacje")
    miejsca = relationship(
        "RezerwacjaMiejsca", back_populates="rezerwacja", cascade="all, delete-orphan"
    )


# ======================================
#        TABELA: REZERWACJA_MIEJSCA
# ======================================
class RezerwacjaMiejsca(Base):
    __tablename__ = "Rezerwacja_Miejsca"

    id_rezerwacji = Column(
        Integer, ForeignKey("Rezerwacja.id_rezerwacji", ondelete="CASCADE"), primary_key=True
    )
    id_miejsca = Column(
        Integer, ForeignKey("Miejsce.id_miejsca", ondelete="CASCADE"), primary_key=True
    )
    typ_biletu = Column(String, nullable=True)
    cena_biletu = Column(Float, nullable=True)  # <--- NOWA KOLUMNA W ORM

    rezerwacja = relationship("Rezerwacja", back_populates="miejsca")
    miejsce = relationship("Miejsce", back_populates="rezerwacje_miejsca")

