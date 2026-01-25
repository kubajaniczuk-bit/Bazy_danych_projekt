const user = getUser();

// jeżeli nie zalogowany → login
if (!user) {
    window.location.href = "login.html";
}

// jeżeli ADMIN → pokaż formularz
if (user.typ === 2) {
    document.getElementById("admin-panel").style.display = "block";
}
fetch(`${API_BASE}/filmy`)
    .then(res => res.json())
    .then(data => {
        const ul = document.getElementById("lista-filmow");
        ul.innerHTML = "";

        data.forEach(film => {
            const li = document.createElement("li");
            li.textContent = `${film.tytul} (${film.czas_trwania} min)`;
            ul.appendChild(li);
        });
    });
function dodajFilm() {
    const tytul = document.getElementById("tytul").value;
    const typ = document.getElementById("typ").value;
    const czas = document.getElementById("czas").value;

    fetch(`${API_BASE}/filmy`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            tytul: tytul,
            typ: typ,
            czas_trwania: Number(czas)
        })
    })
    .then(res => {
        if (!res.ok) throw new Error("Błąd dodawania filmu");
        return res.json();
    })
    .then(() => {
        document.getElementById("admin-msg").textContent = "Film dodany!";
        location.reload(); // odśwież listę
    })
    .catch(err => {
        document.getElementById("admin-msg").textContent = err.message;
    });
}