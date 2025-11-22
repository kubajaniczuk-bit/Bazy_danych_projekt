# Backend – System rezerwacji miejsc w kinie

Backend aplikacji webowej do rezerwacji biletów w kinie.  
Zaimplementowany w **Python + FastAPI + SQLAlchemy + SQLite**.

Backend obsługuje:

- repertuar i seanse (UC-DB1, UC-DB6),
- mapę miejsc (UC-DB2),
- tworzenie / potwierdzanie / anulowanie rezerwacji (UC-DB3–UC-DB5),
- sprzątanie wygasłych rezerwacji (UC-DB8),
- raport dziennej sprzedaży (UC-DB7),
- użytkowników + logowanie (UC-DB9),
- typy biletów i ceny.

---

## 1. Wymagania

- Python **3.10+**
- `pip`
- system: Windows (projekt tworzony i testowany na Windows)

---

## 2. Struktura katalogów (backend)

W repozytorium ten backend znajduje się w:

```text
Projekt/
  backend/
    app/
      api/
        cennik.py          – endpoint testowy dla cennika (opcjonalne)
        filmy.py           – zarządzanie filmami
        raporty.py         – raport dzienny sprzedaży
        repertuar.py       – pobieranie repertuaru
        rezerwacje.py      – tworzenie/zmiana rezerwacji
        sale.py            – generowanie miejsc w sali
        seanse.py          – zarządzanie seansami + mapa miejsc
        uzytkownicy.py     – rejestracja i logowanie użytkowników
      __init__.py
      config_cennik.py     – stałe z cennikiem biletów
      db.py                – konfiguracja bazy (SQLAlchemy + SQLite)
      main.py              – główny plik FastAPI
      models.py            – modele ORM SQLAlchemy
      schemas.py           – schematy Pydantic (wejście/wyjście API)
    requirements.txt       – lista zależności Pythona
    README.md              – ten plik

# tworzenie środowiska
python -m venv .venv

# AKTYWACJA (Windows, PowerShell)
.venv\Scripts\Activate.ps1

# jeśli jesteś w CMD:
.venv\Scripts\activate.bat

Instalacja zależności
pip install -r requirements.txt


uvicorn app.main:app --reload

Serwer będzie dostępny pod adresem:

API: http://127.0.0.1:8000

dokumentacja Swagger: http://127.0.0.1:8000/docs
