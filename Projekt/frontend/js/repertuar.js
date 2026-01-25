fetch("http://localhost:8000/repertuar/")
  .then(res => res.json())
  .then(seanse => {
    const div = document.getElementById("listaRepertuaru");
    div.innerHTML = "";

    seanse.forEach(s => {
      const film = s.film;

      div.innerHTML += `
        <div style="border:1px solid black; margin:10px; padding:10px;">
          <b>${film.tytul}</b><br>
          Typ: ${film.typ}<br>
          Czas trwania: ${film.czas_trwania} min<br>
          Data: ${s.data} godz. ${s.godzina}<br>
          Sala: ${s.numer_sali}<br>
          <button onclick="window.location.href='rezerwacja.html?id_seansu=1'">
  Rezerwuję
</button>
        </div>
      `;
    });
  });

function przejdzDoRezerwacji(idSeansu) {
  localStorage.setItem("seans_id", idSeansu);
  window.location.href = "rezerwacja.html";
}
