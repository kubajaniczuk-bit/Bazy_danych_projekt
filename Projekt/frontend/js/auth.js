async function login() {
    const email = document.getElementById("email").value;
    const haslo = document.getElementById("haslo").value;
    const res = await fetch(`${API_BASE}/uzytkownicy/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, haslo })
    });
    if (!res.ok) {
        alert("Nieprawidłowy email lub hasło");
        return;
    }
    const data = await res.json();
    setUser(data.uzytkownik);
    window.location.href = "strona_glowna.html";
}
async function register() {
    const email = document.getElementById("email").value.trim();
    const haslo = document.getElementById("haslo").value.trim();
    const imie = document.getElementById("imie").value.trim();
    const nazwisko = document.getElementById("nazwisko").value.trim();
    if (!email || !haslo || !imie || !nazwisko) {
        alert("Wszystkie pola są wymagane!");
        return;
    }
    const res = await fetch("http://localhost:8000/uzytkownicy/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, haslo, imie, nazwisko, typ: 0 })
    });
    if (!res.ok) {
        alert("Błąd rejestracji (email może być zajęty)");
        return;
    }
    alert("Konto utworzone, możesz się zalogować");
    window.location.href = "logowanie.html";
}
