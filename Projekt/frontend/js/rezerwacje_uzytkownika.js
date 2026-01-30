document.addEventListener("DOMContentLoaded", () => {
  const userString = localStorage.getItem("uzytkownik");
  const tabela = document.getElementById("tabelaRezerwacji");

  if (!tabela) {
    console.error("Brak elementu tabelaRezerwacji w HTML!");
    return;
  }

  if (!userString) {
    alert("Brak zalogowanego użytkownika!");
    return;
  }

  const user = JSON.parse(userString);
  const idUzytkownika = user.id;

  fetch(`http://localhost:8000/uzytkownicy/${idUzytkownika}/rezerwacje`)
    .then(r => {
      console.log("STATUS:", r.status);
      return r.json();
    })
    .then(data => {
  tabela.innerHTML = "";
  const aktywne = data.filter(rez => rez.status_rezerwacji !== "Anulowana");
  aktywne.forEach(rez => {

    const miejsca = rez.miejsca
      .map(m => `#${m.id_miejsca} (${m.typ_biletu})`)
      .join(", ");

    const suma = rez.miejsca.reduce((s, m) => s + m.cena_biletu, 0);

    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${rez.id_rezerwacji}</td>
      <td>${rez.seans.id_seansu}</td>
      <td>${rez.seans.data} ${rez.seans.godzina}</td>
      <td>${miejsca}</td>
      <td>${suma} zł</td>
      <td>
      <button class="potwierdzBtn">Potwierdz rezerwacje</button>
      </td>
      <td>
        <button class="usunBtn">Anuluj rezerwacje</button>
      </td>
    `;
    tr.querySelector(".usunBtn").addEventListener("click", () => {
      usunRezerwacje(rez.id_rezerwacji);
    });
      tr.querySelector(".potwierdzBtn").addEventListener("click", () => {
      potwierdzRezerwacje(rez.id_rezerwacji);
    });

    tabela.appendChild(tr);
  });
});
function usunRezerwacje(id) {
  if (!confirm("Czy na pewno usunąć rezerwację " + id + "?")) return;

  fetch(`http://localhost:8000/rezerwacje/${id}/anuluj`, {
    method: "PATCH"
  })
  .then(r => {
    if (!r.ok) throw new Error("Błąd usuwania");
    alert("Rezerwacja usunięta");
    location.reload(); // odśwież tabelę
  })
  .catch(e => alert("Błąd: " + e));
}
function potwierdzRezerwacje(id) {
  if (!confirm("Czy na pewno potwierdzic rezerwację " + id + "?")) return;

  fetch(`http://localhost:8000/rezerwacje/${id}/potwierdz`, {
    method: "PATCH"
  })
  .then(r => {
    if (!r.ok) throw new Error("Błąd płatności");
    alert("Rezerwacja potwierdzona");
    location.reload(); // odśwież tabelę
  })
  .catch(e => alert("Błąd: " + e));
}})
