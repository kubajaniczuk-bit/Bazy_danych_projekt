from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from . import models
from .api import repertuar, seanse, filmy, rezerwacje, sale, uzytkownicy,  raporty, cennik, platnosci



Base.metadata.create_all(bind=engine)

app = FastAPI(title="System rezerwacji kina")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routery API
app.include_router(repertuar.router)
app.include_router(seanse.router)
app.include_router(filmy.router)  
app.include_router(rezerwacje.router)
app.include_router(sale.router)
app.include_router(uzytkownicy.router)
app.include_router(raporty.router)   
app.include_router(cennik.router)    
app.include_router(platnosci.router)


@app.get("/")
def read_root():
    return {"message": "Backend działa poprawnie!"}