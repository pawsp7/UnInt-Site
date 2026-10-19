(function () {
  const next = document.querySelector("[data-next-event]");
  const list = document.querySelector("[data-events]");
  const pastSlot = document.querySelector("[data-past-events]");
  const teamSlots = document.querySelectorAll("[data-team]");
  const merchSlots = document.querySelectorAll("[data-merch]");
  if (!next && !list && !pastSlot && !teamSlots.length && !merchSlots.length) return;

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

  function posterFor(event) {
    const title = String(event.title || "").toLowerCase();
    if (title.indexOf("ai agent") !== -1) {
      return {
        src: "/assets/events/ai-agents/ink.png",
        width: 1651,
        height: 2550,
        alt: "AI Agents poster, Ink. Perceive, decide, act.",
        href: "/media/#ai-agents"
      };
    }
    return null;
  }

  function posterPreview(event) {
    const poster = posterFor(event);
    if (!poster) return "";
    return (
      '<a class="shot episode-poster event-poster" href="' + escapeHtml(poster.src) + '">' +
      '<img src="' + escapeHtml(poster.src) + '" width="' + poster.width + '" height="' + poster.height + '" alt="' + escapeHtml(poster.alt) + '">' +
      "</a>"
    );
  }

  function ticket(event) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    const poster = posterPreview(event);
    return (
      '<article class="ticket' + (poster ? " has-poster" : "") + '">' +
      poster +
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
      '<div class="event-actions">' + actions(event, true) + "</div>" +
      "</div></article>"
    );
  }

  function posterHref(event) {
    const poster = posterFor(event);
    return poster ? poster.href : "";
  }

  function actions(event, withList) {
    const label = /hellorubric\.com/i.test(event.href || "") ? "View on Rubric" : "Details";
    const rubric = event.href
      ? '<a class="btn btn-small btn-lime" href="' + escapeHtml(event.href) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>"
      : "";
    const posters = posterHref(event)
      ? '<a class="btn btn-small btn-ghost" href="' + posterHref(event) + '">Posters</a>'
      : "";
    const list = withList
      ? '<a class="btn btn-small btn-ghost" href="/events/">All events</a>'
      : "";
    if (!rubric && !posters && !list) return "";
    return rubric + posters + list;
  }

  function listedTicket(event) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    const media = posterHref(event);
    const rubric = event.href
      ? '<a class="btn btn-small btn-lime" href="' + escapeHtml(event.href) + '" target="_blank" rel="noopener noreferrer">View on Rubric</a>'
      : "";
    return (
      '<article class="ticket has-poster">' +
      posterPreview(event) +
      '<a class="ticket-link" href="' + media + '" aria-label="Posters for ' + escapeHtml(event.title) + '"></a>' +
      '<div class="ticket-stub">' +
      '<span class="kicker" style="color: var(--lime);">' + escapeHtml(card.kicker || "Club night") + "</span>" +
      "<strong>" + stubBig(card.big) + "</strong>" +
      "<span>" + escapeHtml(card.time || "") + "</span>" +
      "</div>" +
      '<div class="ticket-body">' +
      '<p class="kicker" style="color: var(--wine);">' + escapeHtml(card.place || event.where) + "</p>" +
      "<h3>" + escapeHtml(event.title) + "</h3>" +
      "<p>" + escapeHtml(card.blurb || event.summary) + "</p>" +
      '<div class="meta">' + chips + '<a class="photos-cue" href="' + media + '">Posters →</a></div>' +
      (rubric ? '<div class="event-actions">' + rubric + "</div>" : "") +
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
      "<p>" + escapeHtml(event.summary) + "</p>" +
      (event.href || posterHref(event) ? '<div class="event-actions">' + actions(event, false) + "</div>" : "") +
      "</div>" +
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
    const article = (
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
      '<div class="meta">' + chips + (event.custom ? "" : '<span class="photos-cue">Photos →</span>') + "</div>" +
      "</div></article>"
    );
    if (event.custom) return head + article;
    const href = "/media/#" + encodeURIComponent(event.id || "");
    return '<a class="past-event" href="' + escapeHtml(href) + '">' + head + article + "</a>";
  }

  function renderUpcoming(events) {
    if (!events.length) {
      return '<p class="empty-state">No upcoming nights are on Rubric yet. When one is published there, it shows up here.</p>';
    }
    return '<div class="event-list">' + events.map(function (event) {
      return posterHref(event) ? listedTicket(event) : row(event);
    }).join("") + "</div>";
  }

  function personCard(member) {
    const photo = member.photo
      ? '<img class="portrait" src="' + escapeHtml(member.photo) + '" alt="">'
      : '<img src="/assets/jelly-happy.svg" alt="">';
    return (
      '<a class="person" href="' + escapeHtml(member.href) + '" target="_blank" rel="noopener noreferrer">' +
      photo +
      "<h3>" + escapeHtml(member.name) + "</h3>" +
      '<div class="role">' + escapeHtml(member.role) + "</div>" +
      '<span class="go">On Rubric</span>' +
      "</a>"
    );
  }

  function merchCard(item) {
    const image = item.image ? '<img src="' + escapeHtml(item.image) + '" alt="">' : "";
    return (
      '<article class="merch">' +
      image +
      '<div class="body"><h3>' + escapeHtml(item.title) + "</h3>" +
      (item.summary ? "<p>" + escapeHtml(item.summary) + "</p>" : "") +
      '<div class="meta"><span class="chip chip-' + (item.price === "Free" ? "lime" : "cyan") + '">' + escapeHtml(item.price) + "</span></div>" +
      '<div class="event-actions"><a class="btn btn-small btn-lime" href="' + escapeHtml(item.href) + '" target="_blank" rel="noopener noreferrer">Buy on Rubric</a></div>' +
      "</div></article>"
    );
  }

  function fillSlots(slots, html) {
    slots.forEach(function (slot) { slot.innerHTML = html; });
  }

  function renderPast(events) {
    return events.map(function (event, index) {
      return pastBlock(event, index === 0);
    }).join("");
  }

  fetch("/api/club")
    .then(function (response) {
      if (!response.ok) throw new Error("club");
      return response.json();
    })
    .then(function (data) {
      const events = data.events || [];
      const upcoming = events.filter(function (event) { return !event.past; });
      const past = events.filter(function (event) { return event.past; });
      const unavailable = data.rubric === false
        ? '<p class="empty-state">Rubric could not be loaded. Refresh in a moment.</p>'
        : "";
      if (next) {
        next.innerHTML = upcoming.length
          ? ticket(upcoming[0])
          : (unavailable || '<p class="empty-state">No upcoming nights are on Rubric yet. When one is published there, it shows up here.</p>');
      }
      if (list) list.innerHTML = upcoming.length || !unavailable ? renderUpcoming(upcoming) : unavailable;
      if (pastSlot && past.length) pastSlot.innerHTML = renderPast(past);
      if (teamSlots.length) {
        const team = data.team || [];
        fillSlots(teamSlots, team.length
          ? team.map(personCard).join("")
          : (unavailable || '<p class="empty-state">The exec list is not on Rubric yet.</p>'));
      }
      if (merchSlots.length) {
        const merchandise = data.merchandise || [];
        fillSlots(merchSlots, merchandise.length
          ? merchandise.map(merchCard).join("")
          : (unavailable || '<p class="empty-state">Nothing is in the Rubric shop yet.</p>'));
      }
    })
    .catch(function () {
      const message = '<p class="empty-state">Rubric could not be loaded. Refresh in a moment.</p>';
      if (next) next.innerHTML = message;
      if (list) list.innerHTML = message;
      fillSlots(teamSlots, message);
      fillSlots(merchSlots, message);
    });
})();
