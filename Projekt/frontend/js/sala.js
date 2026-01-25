function dodajSale() {
  const numer = document.getElementById("numerSali").value;

  fetch("http://localhost:8000/sale/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ numer_sali: parseInt(numer) })
  })
  .then(r => r.json())
  .then(d => alert("Dodano salę ID=" + d.id_sali));
}
function generuj() {
  const id = 1; // id_sali
  const rzedy = document.getElementById("rzedy").value;
  const naRzad = document.getElementById("naRzad").value;

  fetch(`http://localhost:8000/sale/${id}/generuj_miejsca?rzedy=${rzedy}&na_rzad=${naRzad}`, {
    method: "POST"
  })
  .then(r => r.json())
  .then(d => console.log(d));
}