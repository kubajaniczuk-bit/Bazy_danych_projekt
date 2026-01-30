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