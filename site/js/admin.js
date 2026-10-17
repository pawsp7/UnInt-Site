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

  let deskData = null;

  function showDesk(data) {
    deskData = Object.assign({}, deskData, data);
    desk.innerHTML = renderDesk(deskData);
    const nameInput = desk.querySelector("[name='name']");
    try {
      const saved = localStorage.getItem("ui-desk-name");
      if (nameInput && saved) nameInput.value = saved;
    } catch (err) { /* private mode */ }
    const list = desk.querySelector(".log-list");
    if (list) list.scrollTop = list.scrollHeight;
  }

  function saveNote(data, yes) {
    return data.persisted ? yes : "Saved on this server for now. Set EVENTS_GITHUB_TOKEN on the host so it sticks after a restart.";
  }

  desk.addEventListener("submit", async function (event) {
    const form = event.target;
    if (!form.matches || !form.matches("#custom-event")) return;
    event.preventDefault();
    const error = form.querySelector(".form-error");
    if (error) error.textContent = "";
    const button = form.querySelector("button");
    button.disabled = true;
    const fields = new FormData(form);
    const payload = {
      action: "create",
      title: fields.get("title"),
      date: fields.get("date"),
      time: fields.get("time"),
      place: fields.get("place"),
      summary: fields.get("summary"),
      link: fields.get("link"),
      past: fields.get("past") === "on"
    };
    try {
      const response = await fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json().catch(function () { return {}; });
      if (!response.ok) {
        if (error) error.textContent = data.error || "That night was not added.";
        button.disabled = false;
        return;
      }
      showDesk({ sections: deskData.sections, events: data.events });
      const status = document.querySelector("#event-save");
      if (status) status.textContent = saveNote(data, "Added to the public site.");
    } catch (err) {
      if (error) error.textContent = "The desk could not be reached.";
      button.disabled = false;
    }
  });

  desk.addEventListener("click", async function (event) {
    const button = event.target.closest ? event.target.closest("[data-remove-event]") : null;
    if (!button) return;
    const id = button.getAttribute("data-remove-event");
    if (!window.confirm("Remove this night from the site?")) return;
    button.disabled = true;
    try {
      const response = await fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "delete", id: id })
      });
      const data = await response.json().catch(function () { return {}; });
      if (!response.ok) {
        const status = document.querySelector("#event-save");
        if (status) status.textContent = data.error || "That night was not removed.";
        button.disabled = false;
        return;
      }
      showDesk({ sections: deskData.sections, events: data.events });
      const status = document.querySelector("#event-save");
      if (status) status.textContent = saveNote(data, "Removed from the public site.");
    } catch (err) {
      button.disabled = false;
    }
  });

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
        status.textContent = saveNote(data, want ? "Published on the public site." : "Hidden on the public site.");
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

  desk.addEventListener("submit", async function (event) {
    const form = event.target;
    if (!form.matches || !form.matches("#desk-log-form")) return;
    event.preventDefault();
    const status = document.querySelector("#log-save");
    const button = form.querySelector("button[type='submit']");
    const name = new FormData(form).get("name");
    const text = new FormData(form).get("text");
    if (status) status.textContent = "";
    button.disabled = true;
    try {
      const response = await fetch("/api/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, text: text })
      });
      const data = await response.json().catch(function () { return {}; });
      if (response.status === 401) {
        window.location.href = "/admin/";
        return;
      }
      if (!response.ok) {
        if (status) status.textContent = data.error || "That note did not save.";
        return;
      }
      try { localStorage.setItem("ui-desk-name", String(name || "").trim()); } catch (err) { /* private mode */ }
      form.querySelector("[name='text']").value = "";
      if (deskData) deskData.messages = data.messages;
      paintLog(data.messages, true);
      if (status) {
        status.textContent = data.persisted
          ? "Posted to the shared log."
          : "Saved on this server for now. Set GITHUB_TOKEN on the host so the log sticks after a restart.";
      }
    } catch (err) {
      if (status) status.textContent = "The desk could not be reached.";
    } finally {
      button.disabled = false;
    }
  });

  desk.addEventListener("click", async function (event) {
    const button = event.target.closest ? event.target.closest("[data-log-remove]") : null;
    if (!button) return;
    const status = document.querySelector("#log-save");
    button.disabled = true;
    try {
      const response = await fetch("/api/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "delete", id: button.getAttribute("data-log-remove") })
      });
      const data = await response.json().catch(function () { return {}; });
      if (response.status === 401) {
        window.location.href = "/admin/";
        return;
      }
      if (!response.ok) {
        if (status) status.textContent = data.error || "That note stayed in the log.";
        button.disabled = false;
        return;
      }
      if (deskData) deskData.messages = data.messages;
      paintLog(data.messages, false);
      if (status) status.textContent = "Removed from the log.";
    } catch (err) {
      button.disabled = false;
      if (status) status.textContent = "The desk could not be reached.";
    }
  });

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
      showDesk(data);
      window.setInterval(refreshLog, 10000);
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

  function eventRow(event) {
    const toggle = (
      '<label class="event-toggle">' +
      '<input type="checkbox" data-event-id="' + escapeHtml(event.id) + '"' + (event.visible ? " checked" : "") + ">" +
      "<span><strong>" + escapeHtml(event.title) + "</strong>" +
      "<em>" + escapeHtml(event.whenLabel) + (event.whenDetail ? " · " + escapeHtml(event.whenDetail) : "") + " · " + escapeHtml(event.status) + "</em></span>" +
      '<span class="chip ' + (event.visible ? "chip-lime" : "chip-ghost") + '" data-event-chip="' + escapeHtml(event.id) + '">' +
      (event.visible ? "On the site" : "Hidden") + "</span></label>"
    );
    if (!event.custom) return toggle;
    return (
      '<div class="event-row">' + toggle +
      '<button class="btn btn-ghost btn-small" type="button" data-remove-event="' + escapeHtml(event.id) + '">Remove</button></div>'
    );
  }

  function renderEvents(events) {
    const listed = (events || []).filter(function (event) { return event.custom || !event.past; });
    const past = (events || []).filter(function (event) { return event.past && !event.custom; });
    const rows = listed.map(eventRow).join("");
    const pastLine = past.length
      ? "<p>Already on the Events page: " + past.map(function (event) { return escapeHtml(event.title); }).join(", ") + ".</p>"
      : "";
    return (
      '<article class="panel desk-card">' +
      '<p class="kicker">Events</p>' +
      "<h3>Add a night</h3>" +
      "<p>Rubric nights show on the public site on their own. Add a night here when it is not on Rubric yet. It goes on the Events page immediately.</p>" +
      '<form class="event-form" id="custom-event">' +
      '<label>Title<input name="title" required maxlength="80" autocomplete="off"></label>' +
      '<div class="event-form-row">' +
      '<label>Date<input name="date" type="date"></label>' +
      '<label>Time<input name="time" maxlength="40" placeholder="6:00–8:00 PM" autocomplete="off"></label>' +
      "</div>" +
      '<label>Place<input name="place" maxlength="120" placeholder="Room and building" autocomplete="off"></label>' +
      '<label>What happens<textarea name="summary" maxlength="400" rows="3"></textarea></label>' +
      '<label>Link<input name="link" type="url" maxlength="300" placeholder="https://" autocomplete="off"></label>' +
      '<label class="check"><input name="past" type="checkbox">This night already happened</label>' +
      '<button class="btn btn-lime" type="submit">Add to the site</button>' +
      '<p class="form-error" role="alert"></p>' +
      "</form>" +
      "<h3 style=\"margin-top:22px\">Show on the public site</h3>" +
      '<div class="event-toggles">' + rows + "</div>" +
      pastLine +
      '<p class="event-save" id="event-save" role="status"></p>' +
      "</article>"
    );
  }

  function formatWhen(iso) {
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleString("en-CA", {
      timeZone: "America/Edmonton",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit"
    });
  }

  function renderMessages(messages) {
    if (!messages || !messages.length) {
      return "<li class=\"log-empty\"><p class=\"empty-state\">Nothing in the log yet. A note here is shared with every exec who opens the desk.</p></li>";
    }
    return messages.map(function (message) {
      return (
        "<li class=\"log-item\">" +
        "<div class=\"log-meta\"><strong>" + escapeHtml(message.name) + "</strong>" +
        "<time datetime=\"" + escapeHtml(message.at) + "\">" + escapeHtml(formatWhen(message.at)) + "</time></div>" +
        "<p>" + escapeHtml(message.text) + "</p>" +
        "<button class=\"log-remove\" type=\"button\" data-log-remove=\"" + escapeHtml(message.id) + "\">Remove</button>" +
        "</li>"
      );
    }).join("");
  }

  function paintLog(messages, scroll) {
    const list = document.querySelector(".log-list");
    if (!list) return;
    const stamp = (messages || []).map(function (message) { return message.id; }).join(" ");
    if (list.getAttribute("data-stamp") === stamp) return;
    const nearBottom = list.scrollHeight - list.scrollTop - list.clientHeight < 48;
    list.innerHTML = renderMessages(messages);
    list.setAttribute("data-stamp", stamp);
    if (scroll || nearBottom) list.scrollTop = list.scrollHeight;
  }

  async function refreshLog() {
    if (document.hidden) return;
    try {
      const response = await fetch("/api/log");
      if (response.status === 401) {
        window.location.href = "/admin/";
        return;
      }
      if (!response.ok) return;
      const data = await response.json();
      if (deskData) deskData.messages = data.messages;
      paintLog(data.messages, false);
    } catch (err) { /* leave the log as it is */ }
  }

  function renderLog(messages) {
    return (
      '<article class="panel desk-card desk-log">' +
      '<p class="kicker">Log</p>' +
      "<h3>Shared chat</h3>" +
      "<p>One thread for the execs. Everyone who signs in sees the same notes, newest at the bottom. This stays off the public site — do not put bank numbers or personal phone numbers here.</p>" +
      '<ol class="log-list" data-stamp="' + escapeHtml((messages || []).map(function (message) { return message.id; }).join(" ")) + '">' +
      renderMessages(messages) +
      "</ol>" +
      '<form class="log-form" id="desk-log-form">' +
      '<div class="log-form-row">' +
      '<label>Your name<input name="name" maxlength="40" autocomplete="nickname" required></label>' +
      '<label>Note<textarea name="text" maxlength="1000" rows="2" required></textarea></label>' +
      '<button class="btn btn-lime" type="submit">Post</button>' +
      "</div>" +
      '<p class="log-save" id="log-save" role="status"></p>' +
      "</form></article>"
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
    return renderLog(data.messages) + "<div class=\"desk-grid\">" + renderEvents(data.events) + sections + "</div>";
  }
})();
