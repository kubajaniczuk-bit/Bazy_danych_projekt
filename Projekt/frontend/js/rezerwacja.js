const idSeansu = localStorage.getItem("id_seansu");
const idSali = localStorage.getItem("id_sali");
fetch(`http://localhost:8000/seanse/${idSeansu}/miejsca`)
  .then(res => res.json())
  .then(miejsca => {
    renderujMiejsca(miejsca);
  })
  .catch(err => {
    console.error("Błąd pobierania miejsc:", err);
  });
function renderujMiejsca(miejsca) {
  const sala = document.getElementById("sala");
  sala.innerHTML = "";
  let currentRow = "";
  miejsca.forEach(m => {
    if (m.rzad !== currentRow) {
      currentRow = m.rzad;
      sala.appendChild(document.createElement("br"));
      const label = document.createElement("b");
      label.innerText = "Rząd " + currentRow + ":";
      sala.appendChild(label);
      sala.appendChild(document.createElement("br"));
    }
    const btn = document.createElement("button");
    btn.textContent = m.numer;
    btn.dataset.id = m.id_miejsca;
    btn.style.width = "30px";
    btn.style.height = "30px";
    btn.style.margin = "3px";
    if (m.status !== "Wolne") {
      btn.style.background = "red";
      btn.disabled = true;
    } else {
      btn.style.background = "lightgreen";
      btn.onclick = () => wybierzMiejsce(btn);
    }
    sala.appendChild(btn);
  });
}
let wybraneMiejsca = [];
function wybierzMiejsce(btn) {
  const id = parseInt(btn.dataset.id);
  // czy już wybrane
  const istnieje = wybraneMiejsca.find(m => m.id === id);
  if (istnieje) {
    wybraneMiejsca = wybraneMiejsca.filter(m => m.id !== id);
    btn.style.background = "lightgreen";
  } else {
    wybraneMiejsca.push({ id, typ: "normalny" });
    btn.style.background = "blue";
  }
  renderujPanelBiletow();
}
function renderujPanelBiletow() {
  const panel = document.getElementById("panelBiletow");
  panel.innerHTML = "";
  wybraneMiejsca.forEach(m => {
    const div = document.createElement("div");
    const select = document.createElement("select");
    select.innerHTML = `
      <option value="normalny">Normalny</option>
      <option value="ulgowy">Ulgowy</option>
    `;
    select.value = m.typ;
    select.addEventListener("change", e => {
      m.typ = e.target.value;
      console.log("Zmieniono:", m);
    });
    div.innerHTML = `Miejsce ${m.id}: `;
    div.appendChild(select);
    panel.appendChild(div);
  });
}
function zapiszRezerwacje() {
  const idSeansu = localStorage.getItem("id_seansu");
  const user = JSON.parse(localStorage.getItem("uzytkownik"));
  const idUzytkownika = user.id;
  if (wybraneMiejsca.length === 0) {
    alert("Nie wybrano miejsc!");
    return;
  }
  fetch("http://localhost:8000/rezerwacje/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      id_uzytkownika: idUzytkownika,
      id_seansu: idSeansu,
      miejsca: wybraneMiejsca.map(m => m.id),
      typ_biletu: wybraneMiejsca.map(m => m.typ) 
    })
  })
  .then(r => r.json())
  .then(d => alert("Rezerwacja zapisana! ID=" + d.id_rezerwacji));
}