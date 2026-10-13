(function () {
  const next = document.querySelector("[data-next-event]");
  const list = document.querySelector("[data-events]");
  const pastSlot = document.querySelector("[data-past-events]");
  if (!next && !list && !pastSlot) return;

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function stubBig(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/&lt;br\s*\/?&gt;/gi, "<br>");
  }

  function ticket(event) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    return (
      '<article class="ticket">' +
      '<div class="ticket-stub">' +
      '<span class="kicker" style="color: var(--lime);">' + escapeHtml(card.kicker || "") + "</span>" +
      "<strong>" + stubBig(card.big) + "</strong>" +
      "<span>" + escapeHtml(card.time || "") + "</span>" +
      "</div>" +
      '<div class="ticket-body">' +
      '<p class="kicker" style="color: var(--wine);">' + escapeHtml(card.place || "") + "</p>" +
      "<h3>" + escapeHtml(event.title) + "</h3>" +
      "<p>" + escapeHtml(card.blurb || event.summary) + "</p>" +
      '<div class="meta">' + chips + "</div>" +
      '<p style="margin-top: 16px;"><a class="btn btn-small" href="/events/" style="background: var(--ink); color: var(--paper);">Full event list</a></p>' +
      "</div></article>"
    );
  }

  function row(event) {
    const when = escapeHtml(event.whenLabel) + (event.whenDetail ? "<br>" + escapeHtml(event.whenDetail) : "");
    const datetime = event.datetime ? ' datetime="' + escapeHtml(event.datetime) + '"' : "";
    const tone = event.tone === "lime" || event.tone === "cyan" ? event.tone : "ghost";
    return (
      '<article class="event">' +
      "<time" + datetime + ">" + when + "</time>" +
      "<div><h3>" + escapeHtml(event.title) + "</h3>" +
      '<p class="where">' + escapeHtml(event.where) + "</p>" +
      "<p>" + escapeHtml(event.summary) + "</p></div>" +
      '<span class="chip chip-' + tone + '">' + escapeHtml(event.status) + "</span>" +
      "</article>"
    );
  }

  function pastBlock(event, heading) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    const head = heading
      ? '<div class="section-head"><p class="kicker">Already ran</p><h2>' + escapeHtml(event.title) + ".</h2></div>"
      : '<div class="section-head" style="margin-top:36px"><h2>' + escapeHtml(event.title) + ".</h2></div>";
    return (
      head +
      '<article class="ticket">' +
      '<div class="ticket-stub">' +
      '<span class="kicker" style="color: var(--olive);">' + escapeHtml(card.kicker || "Past") + "</span>" +
      "<strong>" + stubBig(card.big) + "</strong>" +
      "<span>" + escapeHtml(card.time || "") + "</span>" +
      "</div>" +
      '<div class="ticket-body">' +
      '<p class="kicker" style="color: var(--wine);">' + escapeHtml(card.place || event.where) + "</p>" +
      "<h3>" + escapeHtml(event.title) + "</h3>" +
      "<p>" + escapeHtml(card.blurb || event.summary) + "</p>" +
      '<div class="meta">' + chips + "</div>" +
      "</div></article>"
    );
  }

  function renderUpcoming(events) {
    if (!events.length) {
      return '<p class="empty-state">No upcoming nights are posted yet. An exec publishes one from the desk, and it shows up here.</p>';
    }
    return '<div class="event-list">' + events.map(row).join("") + "</div>";
  }

  function renderPast(events) {
    return events.map(function (event, index) {
      return pastBlock(event, index === 0);
    }).join("");
  }

  fetch("/api/events")
    .then(function (response) {
      if (!response.ok) throw new Error("events");
      return response.json();
    })
    .then(function (data) {
      const events = data.events || [];
      const upcoming = events.filter(function (event) { return !event.past; });
      const past = events.filter(function (event) { return event.past; });
      if (next) {
        next.innerHTML = upcoming.length
          ? ticket(upcoming[0])
          : '<p class="empty-state">No events are posted yet. An exec publishes a night from the desk, and the next one shows up here.</p>';
      }
      if (list) list.innerHTML = renderUpcoming(upcoming);
      if (pastSlot && past.length) pastSlot.innerHTML = renderPast(past);
    })
    .catch(function () {
      const message = '<p class="empty-state">The schedule could not be loaded. Refresh in a moment.</p>';
      if (next) next.innerHTML = message;
      if (list) list.innerHTML = message;
    });
})();
