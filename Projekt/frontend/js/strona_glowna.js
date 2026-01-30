const user = getUser();
if (!user) {
    window.location.href = "logowanie.html";
}
if (user.typ === 2) {
  document.getElementById("admin").style.display = "block";
}