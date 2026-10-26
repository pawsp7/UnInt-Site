(function () {
  const slot = document.querySelector("[data-week-events]");
  if (!slot) return;

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function edmontonDate(date) {
    return new Intl.DateTimeFormat("en-CA", {
      timeZone: "America/Edmonton",
      year: "numeric",
      month: "2-digit",
      day: "2-digit"
    }).format(date);
  }

  function addDays(iso, days) {
    const parts = iso.split("-").map(Number);
    const date = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2] + days));
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");
    return date.getUTCFullYear() + "-" + month + "-" + day;
  }

  function currentWeek(now) {
    const today = edmontonDate(now);
    const parts = today.split("-").map(Number);
    const weekday = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2])).getUTCDay();
    const start = addDays(today, weekday === 0 ? -6 : 1 - weekday);
    return { start: start, end: addDays(start, 6) };
  }

  function syncHeader() {
    const header = document.querySelector(".site-header");
    if (header) document.documentElement.style.setProperty("--header", header.offsetHeight + "px");
  }

  function eventDay(event) {
    return String(event.datetime || "").slice(0, 10);
  }

  fetch("/api/club")
    .then(function (response) {
      if (!response.ok) throw new Error("club");
      return response.json();
    })
    .then(function (data) {
      const week = currentWeek(new Date());
      const events = (data.events || []).filter(function (event) {
        const day = eventDay(event);
        return !event.past && day >= week.start && day <= week.end && /hellorubric\.com/i.test(event.href || "");
      }).sort(function (left, right) {
        return String(left.datetime).localeCompare(String(right.datetime));
      });
      if (!events.length) return;
      slot.innerHTML = '<div class="wrap"><p class="kicker week-kicker">This week</p>' + events.map(function (event) {
        const when = event.whenLabel + (event.whenDetail ? " · " + event.whenDetail : "");
        return '<a href="' + escapeHtml(event.href) + '" target="_blank" rel="noopener noreferrer">' +
          '<time datetime="' + escapeHtml(event.datetime) + '">' + escapeHtml(when) + "</time>" +
          "<strong>" + escapeHtml(event.title) + "</strong>" +
          "<em>Rubric</em></a>";
      }).join("") + "</div>";
      slot.hidden = false;
      syncHeader();
    })
    .catch(function () {});

  window.addEventListener("resize", syncHeader);
})();

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

(function () {
  const frames = document.querySelectorAll("[data-recap]");
  if (!frames.length) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  frames.forEach(function (frame) {
    const view = frame.querySelector(".recap-view");
    const pages = frame.querySelectorAll(".recap-page");
    const prev = frame.querySelector(".recap-prev");
    const next = frame.querySelector(".recap-next");
    if (!view || !prev || !next || pages.length < 2) return;
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
})();
