fetch("http://localhost:8000/repertuar/")
  .then(res => res.json())
  .then(seanse => wyswietlSeanse(seanse))
  .catch(err => console.error("Błąd pobierania repertuaru:", err));
document.getElementById("btnSzukaj").onclick = () => {
  const tytul = document.getElementById("szukajTytul").value.trim();
  const data = document.getElementById("szukajData").value;
  if (!tytul) {
    alert("Podaj fragment tytułu!");
    return;
  }
  let url = `http://localhost:8000/repertuar/szukaj?q=${encodeURIComponent(tytul)}`;
  if (data) {
    url += `&data=${data}`;
  }
  fetch(url)
    .then(res => res.json())
    .then(seanse => wyswietlSeanse(seanse))
    .catch(err => console.error("Błąd wyszukiwania:", err));
};
function wyswietlSeanse(seanse) {
  const div = document.getElementById("listaRepertuaru");
  div.innerHTML = "";
  seanse.forEach(s => {
    const film = s.film;
    const seansId = s.id_seansu || s.id || s.idSeansu;
    const seansDiv = document.createElement("div");
    seansDiv.style.border = "1px solid black";
    seansDiv.style.margin = "10px";
    seansDiv.style.padding = "10px";
    seansDiv.innerHTML = `
      <b>${film.tytul}</b><br>
      Data: ${s.data} godz. ${s.godzina}<br>
      Sala: ${s.numer_sali}<br>
    `;
    const btn = document.createElement("button");
    btn.textContent = "Rezerwuję";
    btn.onclick = () => {
      if (!seansId) {
        alert("Brak ID seansu!");
        return;
      }
      localStorage.setItem("id_seansu", seansId);
      window.location.href = "rezerwacja.html";
    };
    seansDiv.appendChild(btn);
    div.appendChild(seansDiv);
  });
}