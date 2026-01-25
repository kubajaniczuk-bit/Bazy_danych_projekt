const API_URL = "http://localhost:8000/cennik/";


const user = getUser();
if (!user) {
    window.location.href = "logowanie.html";
}
const info = document.createElement("p");
if (user.typ === 2) {
    info.textContent = "Jesteś zalogowany jako ADMIN";
} else if (user.typ === 0) {
    info.textContent = "Jesteś zalogowany jako KLIENT";
} else {
    info.textContent = "Zalogowany użytkownik";
}

document.body.prepend(info); 
// pobieramy cennik (publiczny endpoint)
fetch(`${API_BASE}/cennik/`)
    .then(res => res.json())
    .then(data => {
        document.getElementById("normalny").textContent = data.normalny;
        document.getElementById("ulgowy").textContent = data.ulgowy;
    });


