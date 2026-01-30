fetch(`${API_BASE}/filmy/`)
    .then(res => res.json())
    .then(data => {
        console.log(data);
        const ul = document.getElementById("lista-filmow");
        ul.innerHTML = "";

        data.forEach(film => {
            const li = document.createElement("li");
            li.dataset.id = film.id_filmu; // dodajemy data-id
            li.textContent = `${film.tytul} (${film.czas_trwania} min) `;

            // Przyciski
            const editButton = document.createElement("button");
            editButton.textContent = "Edytuj";
            editButton.addEventListener("click", () => {
                edytujFilm(film); // przekazujemy cały obiekt filmu
            });

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Usuń";
            deleteButton.addEventListener("click", () => {
                usunFilm(film.id_filmu);
            });

            li.appendChild(editButton);
            li.appendChild(deleteButton);
            ul.appendChild(li);
        });
    });
function edytujFilm(film) {
    // Sprawdzenie czy formularz już istnieje
    if (document.getElementById(`edit-form-${film.id_filmu}`)) return;
    const li = document.querySelector(`#lista-filmow li[data-id='${film.id_filmu}']`);
    // Tworzenie formularza
    const form = document.createElement("form");
    form.id = `edit-form-${film.id_filmu}`;
    form.style.marginTop = "5px";
    form.innerHTML = `
        <input type="text" name="tytul" placeholder="Tytuł" />
        <input type="text" name="gatunek" placeholder="Gatunek" />
        <input type="number" name="czas_trwania" placeholder="Czas trwania (min)" min="1" />
        <button type="submit">Zapisz</button>
        <button type="button" id="cancel-${film.id_filmu}">Anuluj</button>
    `;
    li.appendChild(form);
    document.getElementById(`cancel-${film.id_filmu}`).addEventListener("click", () => {
        form.remove();
    });
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const data = {};
        const tytul = form.elements["tytul"].value.trim();
        const gatunek = form.elements["gatunek"].value.trim();
        const czas_trwania = form.elements["czas_trwania"].value.trim();
        if (tytul) data.tytul = tytul;
        if (gatunek) data.typ = gatunek;
        if (czas_trwania) data.czas_trwania = Number(czas_trwania);
        // Jeśli nic nie zostało wpisane, nie wysyłamy requesta
        if (Object.keys(data).length === 0) {
            alert("Nie wprowadzono żadnych zmian!");
            return;
        }
        fetch(`${API_BASE}/filmy/${film.id_filmu}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        })
        .then(res => {
            if (res.ok) {
                alert("Film zaktualizowany!");
                location.reload();
            } else {
                alert("Błąd przy aktualizacji filmu");
            }
        });
    });
}
function usunFilm(id_filmu) {
    console.log("Usuwasz film o id:", id_filmu);
    fetch(`${API_BASE}/filmy/${id_filmu}`, { method: "DELETE" })
        .then(res => {
            if (res.ok) {
                alert("Film usunięty!");
                location.reload();
            } else {
                alert("Błąd przy usuwaniu filmu");
            }
        });
}
function dodajFilm() {
    const tytul = document.getElementById("tytul").value;
    const typ = document.getElementById("typ").value;
    const czas = document.getElementById("czas").value;
    fetch(`${API_BASE}/filmy/`, {
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
        location.reload();
    })
    .catch(err => {
        document.getElementById("admin-msg").textContent = err.message;
    });
}