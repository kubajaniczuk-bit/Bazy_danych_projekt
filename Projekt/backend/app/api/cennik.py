from fastapi import APIRouter

from ..config_cennik import CENNIK_BILETOW

router = APIRouter(
    prefix="/cennik",
    tags=["cennik"],
)


@router.get("/")
def pobierz_cennik():
    """
    Zwraca aktualny cennik biletów.

    Przykład odpowiedzi:
    {
      "normalny": 25.0,
      "ulgowy": 18.0
    }
    """
    return CENNIK_BILETOW
