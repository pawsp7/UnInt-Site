(function () {
  const form = document.querySelector("#desk-login");
  const desk = document.querySelector("#desk");

  function showError(message) {
    const slot = document.querySelector(".form-error");
    if (slot) slot.textContent = message;
  }

  if (form) {
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      showError("");
      const password = new FormData(form).get("password");
      const button = form.querySelector("button");
      button.disabled = true;
      try {
        const response = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ password: password })
        });
        const data = await response.json().catch(function () { return {}; });
        if (!response.ok) {
          showError(data.error || "That password did not open the desk.");
          button.disabled = false;
          return;
        }
        window.location.href = "/admin/desk/";
      } catch (err) {
        showError("The desk could not be reached. Try again in a moment.");
        button.disabled = false;
      }
    });
  }

  if (!desk) return;

  desk.addEventListener("change", async function (event) {
    const box = event.target;
    if (!box.matches || !box.matches("[data-event-id]")) return;
    const chip = desk.querySelector('[data-event-chip="' + box.dataset.eventId + '"]');
    const status = document.querySelector("#event-save");
    const want = box.checked;
    box.disabled = true;
    try {
      const response = await fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: box.dataset.eventId, visible: want })
      });
      const data = await response.json().catch(function () { return {}; });
      if (!response.ok) {
        box.checked = !want;
        if (status) status.textContent = data.error || "That change did not save.";
        return;
      }
      if (chip) {
        chip.textContent = want ? "On the site" : "Hidden";
        chip.className = "chip " + (want ? "chip-lime" : "chip-ghost");
      }
      if (status) {
        status.textContent = data.persisted
          ? (want ? "Published on the public site." : "Hidden on the public site.")
          : "Saved on this server for now. Set GITHUB_TOKEN on the host so it sticks after a restart.";
      }
    } catch (err) {
      box.checked = !want;
      if (status) status.textContent = "The desk could not be reached.";
    } finally {
      box.disabled = false;
    }
  });

  const logout = document.querySelector("#desk-logout");
  if (logout) {
    logout.addEventListener("click", async function () {
      await fetch("/api/logout", { method: "POST" });
      window.location.href = "/admin/";
    });
  }

  fetch("/api/desk")
    .then(function (response) {
      if (response.status === 401) {
        window.location.href = "/admin/";
        return null;
      }
      if (!response.ok) throw new Error("desk");
      return response.json();
    })
    .then(function (data) {
      if (!data) return;
      desk.innerHTML = renderDesk(data);
    })
    .catch(function () {
      desk.innerHTML = "<p class=\"lede\">The desk did not load. Refresh, or sign in again.</p>";
    });

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderEvents(events) {
    const upcoming = (events || []).filter(function (event) { return !event.past; });
    const past = (events || []).filter(function (event) { return event.past; });
    const rows = upcoming.map(function (event) {
      return (
        '<label class="event-toggle">' +
        '<input type="checkbox" data-event-id="' + escapeHtml(event.id) + '"' + (event.visible ? " checked" : "") + ">" +
        "<span><strong>" + escapeHtml(event.title) + "</strong>" +
        "<em>" + escapeHtml(event.whenLabel) + " · " + escapeHtml(event.status) + "</em></span>" +
        '<span class="chip ' + (event.visible ? "chip-lime" : "chip-ghost") + '" data-event-chip="' + escapeHtml(event.id) + '">' +
        (event.visible ? "On the site" : "Hidden") + "</span></label>"
      );
    }).join("");
    const pastLine = past.length
      ? "<p>Already on the Events page: " + past.map(function (event) { return escapeHtml(event.title); }).join(", ") + ".</p>"
      : "";
    return (
      '<article class="panel desk-card">' +
      '<p class="kicker">Events</p>' +
      "<h3>Show on the public site</h3>" +
      "<p>Upcoming nights start hidden. Check one to publish it on the home page and the Events tab.</p>" +
      '<div class="event-toggles">' + rows + "</div>" +
      pastLine +
      '<p class="event-save" id="event-save" role="status"></p>' +
      "</article>"
    );
  }

  function renderDesk(data) {
    const sections = (data.sections || []).map(function (section) {
      const links = (section.links || []).map(function (link) {
        return (
          "<li><a href=\"" + escapeHtml(link.href) + "\" target=\"_blank\" rel=\"noopener noreferrer\">" +
          escapeHtml(link.label) + "</a><p>" + escapeHtml(link.note || "") + "</p></li>"
        );
      }).join("");
      const notes = (section.notes || []).map(function (note) {
        return "<li>" + escapeHtml(note) + "</li>";
      }).join("");
      return (
        "<article class=\"panel desk-card\">" +
        "<p class=\"kicker\">" + escapeHtml(section.kicker) + "</p>" +
        "<h3>" + escapeHtml(section.title) + "</h3>" +
        (links ? "<ul>" + links + "</ul>" : "") +
        (notes ? "<ul class=\"plain-notes\">" + notes + "</ul>" : "") +
        "</article>"
      );
    }).join("");
    return "<div class=\"desk-grid\">" + renderEvents(data.events) + sections + "</div>";
  }
})();
