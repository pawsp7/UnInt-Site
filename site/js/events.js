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

  let mediaItems = [];

  function mediaFor(event) {
    const id = String(event.id || "").toLowerCase();
    const title = String(event.title || "").toLowerCase();
    for (let i = 0; i < mediaItems.length; i += 1) {
      const item = mediaItems[i];
      if (item.id === id) return item;
      const parts = item.match || [];
      if (parts.length && parts.every(function (part) { return title.indexOf(part) !== -1; })) return item;
    }
    return null;
  }

  function posterFor(event) {
    const item = mediaFor(event);
    const poster = item && item.poster;
    if (!poster || !poster.src || !item.id) return null;
    const prefix = "/assets/events/" + item.id + "/poster/";
    if (poster.src.indexOf(prefix) !== 0) return null;
    return poster;
  }

  function applyMedia(event) {
    const item = mediaFor(event);
    if (!item) return event;
    const next = Object.assign({}, event);
    if (item.place) next.where = item.place;
    if (item.datetime) next.datetime = item.datetime;
    if (item.whenLabel) next.whenLabel = item.whenLabel;
    if (item.whenDetail) next.whenDetail = item.whenDetail;
    if (item.ticket) {
      next.ticket = Object.assign({}, event.ticket || {}, item.ticket);
      if (item.ticket.place) next.where = item.ticket.place;
    }
    return next;
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

  function shot(image) {
    if (!image || !image.src) return "";
    const lazy = image.lazy ? " loading=\"lazy\"" : "";
    const klass = image.className ? " " + image.className : "";
    return (
      '<a class="shot' + klass + '" href="' + escapeHtml(image.src) + '">' +
      '<img src="' + escapeHtml(image.src) + '" width="' + image.width + '" height="' + image.height + '" alt="' + escapeHtml(image.alt) + '"' + lazy + ">" +
      "</a>"
    );
  }

  function recapHtml(event) {
    const item = mediaFor(event);
    const recap = item && item.recap;
    if (!recap || !recap.pages || !recap.pages.length) return "";
    const poster = recap.poster || item.poster;
    const pages = recap.pages.map(function (page) {
      return '<div class="recap-page">' + page.map(shot).join("") + "</div>";
    }).join("");
    const hidden = recap.pages.length > 1 ? "" : " hidden";
    return (
      '<div class="event-recap">' +
      '<div class="recap" data-recap aria-label="' + escapeHtml(recap.label) + '">' +
      shot(poster) +
      '<div class="recap-side"><div class="recap-view">' + pages + "</div>" +
      '<button type="button" class="recap-arrow recap-prev" aria-label="Previous pictures"' + hidden + ">‹</button>" +
      '<button type="button" class="recap-arrow recap-next" aria-label="Next pictures"' + hidden + ">›</button>" +
      "</div></div></div>"
    );
  }

  function actions(event, withList) {
    const label = /hellorubric\.com/i.test(event.href || "") ? "View on Rubric" : "Details";
    const rubric = event.href
      ? '<a class="btn btn-small btn-lime" href="' + escapeHtml(event.href) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>"
      : "";
    const list = withList
      ? '<a class="btn btn-small btn-ghost" href="/events/">All events</a>'
      : "";
    if (!rubric && !list) return "";
    return rubric + list;
  }

  function listedTicket(event) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    const rubric = event.href
      ? '<a class="btn btn-small btn-lime" href="' + escapeHtml(event.href) + '" target="_blank" rel="noopener noreferrer">View on Rubric</a>'
      : "";
    return (
      '<article class="ticket has-poster">' +
      posterPreview(event) +
      '<div class="ticket-stub">' +
      '<span class="kicker" style="color: var(--lime);">' + escapeHtml(card.kicker || "Club night") + "</span>" +
      "<strong>" + stubBig(card.big) + "</strong>" +
      "<span>" + escapeHtml(card.time || "") + "</span>" +
      "</div>" +
      '<div class="ticket-body">' +
      '<p class="kicker" style="color: var(--wine);">' + escapeHtml(card.place || event.where) + "</p>" +
      "<h3>" + escapeHtml(event.title) + "</h3>" +
      "<p>" + escapeHtml(card.blurb || event.summary) + "</p>" +
      '<div class="meta">' + chips + "</div>" +
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
      (event.href ? '<div class="event-actions">' + actions(event, false) + "</div>" : "") +
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
      : '<div class="section-head"><h2>' + escapeHtml(event.title) + ".</h2></div>";
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
    const linked = event.custom
      ? head + article
      : '<a class="past-event" href="' + escapeHtml("/media/#" + encodeURIComponent(event.id || "")) + '">' + head + article + "</a>";
    return '<div class="past-night">' + linked + recapHtml(event) + "</div>";
  }

  function renderUpcoming(events) {
    if (!events.length) {
      return '<p class="empty-state">No upcoming nights are on Rubric yet. When one is published there, it shows up here.</p>';
    }
    return '<div class="event-list">' + events.map(function (event) {
      return posterFor(event) ? listedTicket(event) : row(event);
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
    const nights = events.slice();
    mediaItems.forEach(function (item) {
      if (!item.recap || !item.fallback) return;
      const exists = nights.some(function (event) {
        const found = mediaFor(event);
        return found && found.id === item.id;
      });
      if (!exists) nights.push(Object.assign({ id: item.id }, item.fallback));
    });
    nights.sort(function (left, right) {
      return String(left.datetime || "").localeCompare(String(right.datetime || ""));
    });
    return nights.map(function (event, index) {
      return pastBlock(event, index === 0);
    }).join("");
  }

  function isUnnaturalGames(event) {
    const id = String(event.id || "").toLowerCase();
    const title = String(event.title || "").toLowerCase();
    return id === "unnatural-games" || title.indexOf("unnatural games") !== -1;
  }

  function seriesKey(event) {
    if (isUnnaturalGames(event)) return "unnatural-games";
    return String(event.title || "").toLowerCase();
  }

  function uniqueSoonest(events) {
    const seen = {};
    const out = [];
    events.forEach(function (event) {
      const key = seriesKey(event);
      if (seen[key]) return;
      seen[key] = true;
      out.push(event);
    });
    return out;
  }

  function homeUpcoming(events, limit) {
    const unique = uniqueSoonest(events);
    const featured = [];
    const rest = [];
    unique.forEach(function (event) {
      if (isUnnaturalGames(event)) featured.push(event);
      else rest.push(event);
    });
    const slots = Math.max(0, limit - featured.length);
    return rest.slice(0, slots).concat(featured).sort(function (left, right) {
      const a = left.datetime || "9999-99-99";
      const b = right.datetime || "9999-99-99";
      return a.localeCompare(b);
    }).slice(0, limit);
  }

  function paint(data) {
      const events = (data.events || []).map(applyMedia);
      const upcoming = events.filter(function (event) { return !event.past; });
      const past = events.filter(function (event) { return event.past; });
      const unavailable = data.rubric === false
        ? '<p class="empty-state">Rubric could not be loaded. Refresh in a moment.</p>'
        : "";
      if (next) {
        const shown = homeUpcoming(upcoming, 3);
        next.innerHTML = shown.length
          ? shown.map(ticket).join("")
          : (unavailable || '<p class="empty-state">No upcoming nights are on Rubric yet. When one is published there, it shows up here.</p>');
      }
      if (list) list.innerHTML = upcoming.length || !unavailable ? renderUpcoming(upcoming) : unavailable;
      if (pastSlot) pastSlot.innerHTML = renderPast(past);
      if (window.initRecaps) window.initRecaps();
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
  }

  Promise.all([
    fetch("/assets/events/events.json").then(function (response) {
      return response.ok ? response.json() : { events: [] };
    }).catch(function () { return { events: [] }; }),
    fetch("/api/club").then(function (response) {
      if (!response.ok) throw new Error("club");
      return response.json();
    })
  ]).then(function (results) {
    mediaItems = (results[0] && results[0].events) || [];
    paint(results[1]);
  }).catch(function () {
      const message = '<p class="empty-state">Rubric could not be loaded. Refresh in a moment.</p>';
      if (next) next.innerHTML = message;
      if (list) list.innerHTML = message;
      fillSlots(teamSlots, message);
      fillSlots(merchSlots, message);
    });
})();
