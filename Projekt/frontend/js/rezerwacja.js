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
  sala.innerHTML = ""; // czyścimy div
  let currentRow = "";

  miejsca.forEach(m => {
    if (m.rzad !== currentRow) {
      currentRow = m.rzad;
      const br = document.createElement("br");
      const label = document.createElement("b");
      label.innerText = "Rząd " + currentRow + ":";
      sala.appendChild(br);
      sala.appendChild(label);
      sala.appendChild(document.createElement("br"));
    }

    const btn = document.createElement("button");
    btn.textContent = m.numer;
    btn.dataset.id = m.id_miejsca;
    btn.dataset.selected = "0";

    btn.style.width = "30px";
    btn.style.height = "30px";
    btn.style.margin = "3px";

    if (m.status !== "Wolne") {
      btn.style.background = "red";
      btn.disabled = true;
    } else {
      btn.style.background = "lightgreen";
      btn.onclick = () => {
        btn.dataset.selected = btn.dataset.selected === "1" ? "0" : "1";
        btn.style.background = btn.dataset.selected === "1" ? "blue" : "lightgreen";
      };
    }

    sala.appendChild(btn);
  });
}


// rezerwacja
function zapiszRezerwacje() {
  const wybrane = [...document.querySelectorAll("#sala button")]
    .filter(b => b.dataset.selected === "1")
    .map(b => parseInt(b.dataset.id));
  console.log("Wybrane miejsca:", wybrane);
  const idSeansu = localStorage.getItem("seans_id");
  const userString = localStorage.getItem("uzytkownik");
  const user = JSON.parse(userString); // zamiana string -> obiekt JS
  const idUzytkownika = user.id;       // pobranie tylko id
  console.log("ID użytkownika:", idUzytkownika);
  if (!idSeansu) {
    alert("Nie wybrano seansu!");
    return;
  }
  if (wybrane.length === 0) {
    alert("Nie wybrano żadnych miejsc.");
    return;
  }

  console.log("Wybrane miejsca:", wybrane, "idSeansu:", idSeansu);

  fetch("http://localhost:8000/rezerwacje/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id_uzytkownika: parseInt(idUzytkownika),
      id_seansu: parseInt(idSeansu),
      miejsca: wybrane,
      typ_biletu: "normalny"
    })
  })
  .then(res => {
    if (!res.ok) throw new Error("Błąd zapisu rezerwacji: " + res.status);
    return res.json();
  })
  .then(data => {
    alert("Rezerwacja zapisana! ID: " + data.id_rezerwacji);
    // odświeżenie widoku miejsc
    fetch(`http://localhost:8000/seanse/${idSeansu}/miejsca`)
      .then(res => res.json())
      .then(miejsca => renderujMiejsca(miejsca));
  })
  .catch(err => {
    console.error(err);
    alert("Wystąpił błąd przy zapisie rezerwacji.");
  });
}



