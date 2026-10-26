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
  const dialog = document.createElement("dialog");
  dialog.className = "lightbox";
  dialog.innerHTML = '<form method="dialog"><button class="lightbox-close" type="submit">Close</button></form><img alt="">';
  document.body.appendChild(dialog);
  const img = dialog.querySelector("img");
  document.addEventListener("click", function (event) {
    const shot = event.target.closest("a.shot");
    if (!shot) return;
    event.preventDefault();
    const source = shot.querySelector("img");
    img.src = shot.getAttribute("href");
    img.alt = source ? source.alt : "";
    dialog.showModal();
  });
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", function () {
    img.removeAttribute("src");
  });
})();

window.initRecaps = function (root) {
  const frames = (root || document).querySelectorAll("[data-recap]");
  if (!frames.length) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  frames.forEach(function (frame) {
    if (frame.getAttribute("data-recap-ready") === "true") return;
    const view = frame.querySelector(".recap-view");
    const pages = frame.querySelectorAll(".recap-page");
    const prev = frame.querySelector(".recap-prev");
    const next = frame.querySelector(".recap-next");
    if (!view || !prev || !next || pages.length < 2) return;
    frame.setAttribute("data-recap-ready", "true");
    prev.hidden = false;
    next.hidden = false;
    function update() {
      const max = view.scrollWidth - view.clientWidth;
      prev.disabled = view.scrollLeft <= 2;
      next.disabled = view.scrollLeft >= max - 2;
    }
    function slide(direction) {
      view.scrollBy({ left: direction * view.clientWidth, behavior: reduce ? "auto" : "smooth" });
    }
    prev.addEventListener("click", function () { slide(-1); });
    next.addEventListener("click", function () { slide(1); });
    view.addEventListener("scroll", update, { passive: true });
    update();
  });
};
window.initRecaps();
