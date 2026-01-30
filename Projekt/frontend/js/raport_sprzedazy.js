function pobierzRaport() {
  const data = document.getElementById("dataRaportu").value;
  if (!data) {
    alert("Podaj datę!");
    return;
  }
  fetch(`http://localhost:8000/raport/sprzedaz-dzienna?data=${data}`)
    .then(r => r.json())
    .then(wynik => {
      console.log("RAPORT:", wynik);
      const tabela = document.getElementById("tabelaRaport");
      tabela.innerHTML = "";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${wynik.data}</td>
        <td>${wynik.liczba_biletow}</td>
        <td>${wynik.przychod} zł</td>
      `;
      tabela.appendChild(tr);
    })
    .catch(e => alert("Błąd: " + e));
}
