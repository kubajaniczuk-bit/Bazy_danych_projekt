from fastapi import FastAPI

from .db import Base, engine
from . import models
from .api import repertuar, seanse, filmy, rezerwacje, sale, uzytkownicy,  raporty, cennik



Base.metadata.create_all(bind=engine)

app = FastAPI(title="System rezerwacji kina")

# Routery API
app.include_router(repertuar.router)
app.include_router(seanse.router)
app.include_router(filmy.router)  
app.include_router(rezerwacje.router)
app.include_router(sale.router)
app.include_router(uzytkownicy.router)
app.include_router(raporty.router)   
app.include_router(cennik.router)    


@app.get("/")
def read_root():
    return {"message": "Backend działa poprawnie!"}