const API_BASE = "http://localhost:8000";

function getUser() {
    return JSON.parse(localStorage.getItem("uzytkownik"));
}

function setUser(user) {
    localStorage.setItem("uzytkownik", JSON.stringify(user));
}

function logout() {
    localStorage.removeItem("uzytkownik");
    window.location.href = "logowanie.html";
}