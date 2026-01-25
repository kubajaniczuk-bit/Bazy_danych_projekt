function dodajSeans() {
  const id_filmu = document.getElementById("filmId").value;
  const id_sali = document.getElementById("salaId").value;
  const data = document.getElementById("data").value;
  const godzina = document.getElementById("godzina").value;

  fetch("http://localhost:8000/seanse/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      id_filmu: parseInt(id_filmu),
      id_sali: parseInt(id_sali),
      data: data,
      godzina: godzina
    })
  })
  .then(r => r.json())
  .then(d => {
    if (d.detail) alert(d.detail);
    else alert("Dodano seans ID=" + d.id_seansu);
  });
}