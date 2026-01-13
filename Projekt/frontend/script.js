const API_URL = "http://localhost:8000/cennik/";

document.getElementById("loadPrices").addEventListener("click", () => {
    fetch(API_URL)
        .then(response => {
            if (!response.ok) {
                throw new Error("Błąd sieci");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById("normalny").textContent = data.normalny;
            document.getElementById("ulgowy").textContent = data.ulgowy;
        })
        .catch(error => {
            console.error("Błąd:", error);
            alert("Nie udało się pobrać cennika");
        });
});
