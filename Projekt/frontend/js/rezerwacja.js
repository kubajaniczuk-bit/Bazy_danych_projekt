const urlParams = new URLSearchParams(window.location.search);
const id_seansu = urlParams.get("id_seansu");

document.getElementById("seans").innerText = id_seansu;

async function zarezerwujMiejsca() {
  // przykładowe wybrane miejsca (na razie statyczne, potem wybór z UI)
  const wybraneMiejsca = [1, 2]; 

  try {
    const res = await fetch("http://127.0.0.1:8000/rezerwacje/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_uzytkownika: 1,   // tutaj ID zalogowanego użytkownika
        id_seansu: id_seansu, // pobrane z URL
        miejsca: wybraneMiejsca,
        typ_biletu: "normalny"
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      // Backend zwrócił status 400 lub inny → wyrzucamy error
      throw new Error(data.detail || "Nieznany błąd");
    }

    alert("Rezerwacja udana! ID rezerwacji: " + data.id_rezerwacji);

  } catch (err) {
    alert("Błąd: " + err.message);
  }
}
