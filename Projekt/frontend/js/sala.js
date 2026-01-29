async function dodajIGeneruj() {
  const numer = document.getElementById("numerSali").value;
  const rzedy = document.getElementById("rzedy").value;
  const naRzad = document.getElementById("naRzad").value;

  const sala = await fetch("http://localhost:8000/sale/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ numer_sali: parseInt(numer) })
  }).then(r => r.json());

  const id = sala.id_sali;

  await fetch(`http://localhost:8000/sale/${id}/generuj_miejsca?rzedy=${rzedy}&na_rzad=${naRzad}`, {
    method: "POST"
  });

  alert("Sala dodana i miejsca wygenerowane!");
}