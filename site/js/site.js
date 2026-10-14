(function () {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", function () {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();

(function () {
  const shots = document.querySelectorAll("a.shot");
  if (!shots.length) return;
  const dialog = document.createElement("dialog");
  dialog.className = "lightbox";
  dialog.innerHTML = '<form method="dialog"><button class="lightbox-close" type="submit">Close</button></form><img alt="">';
  document.body.appendChild(dialog);
  const img = dialog.querySelector("img");
  shots.forEach(function (shot) {
    shot.addEventListener("click", function (event) {
      event.preventDefault();
      const source = shot.querySelector("img");
      img.src = shot.getAttribute("href");
      img.alt = source ? source.alt : "";
      dialog.showModal();
    });
  });
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", function () {
    img.removeAttribute("src");
  });
})();
