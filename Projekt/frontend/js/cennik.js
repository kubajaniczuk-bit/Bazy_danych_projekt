const API_URL = "http://localhost:8000/cennik/";


const user = getUser();
if (!user) {
    window.location.href = "logowanie.html";
}
if (user.typ === 2) {
  document.getElementById("admin").style.display = "block";
}

const info = document.createElement("p");
if (user.typ === 2) {
    info.textContent = "Jesteś zalogowany jako ADMIN";
} else if (user.typ === 0) {
    info.textContent = "Jesteś zalogowany jako KLIENT";
} else {
    info.textContent = "Zalogowany użytkownik";
}




