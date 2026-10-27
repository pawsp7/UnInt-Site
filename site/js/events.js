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

  function mediaById(catalog) {
    const map = {};
    (catalog || []).forEach(function (event) {
      if (event && event.id) map[event.id] = event;
    });
    return map;
  }

  function matchMedia(event, catalog) {
    if (!event) return null;
    const map = mediaById(catalog);
    if (event.id && map[event.id]) return map[event.id];
    const title = String(event.title || "").toLowerCase();
    for (let i = 0; i < (catalog || []).length; i += 1) {
      const item = catalog[i];
      const name = String(item.title || "").toLowerCase();
      if (!name) continue;
      if (title === name || title.indexOf(name) !== -1 || name.indexOf(title) !== -1) return item;
    }
    return null;
  }

  function shot(image) {
    if (!image) return "";
    const lazy = image.lazy ? " loading=\"lazy\"" : "";
    const klass = image.className ? " " + image.className : "";
    return (
      '<a class="shot' + klass + '" href="' + escapeHtml(image.src) + '">' +
      '<img src="' + escapeHtml(image.src) + '" width="' + image.width + '" height="' + image.height + '" alt="' + escapeHtml(image.alt) + '"' + lazy + ">" +
      "</a>"
    );
  }

  function posterPreview(event, media) {
    const poster = (media && media.poster) || event.poster;
    if (!poster) return "";
    return (
      '<a class="shot episode-poster event-poster" href="' + escapeHtml(poster.src) + '">' +
      '<img src="' + escapeHtml(poster.src) + '" width="' + poster.width + '" height="' + poster.height + '" alt="' + escapeHtml(poster.alt) + '">' +
      "</a>"
    );
  }

  function recapHtml(media) {
    if (!media || !media.recap || !media.poster) return "";
    const pages = (media.recap.pages || []).map(function (page) {
      return '<div class="recap-page">' + page.map(shot).join("") + "</div>";
    }).join("");
    const hidden = (media.recap.pages || []).length > 1 ? "" : " hidden";
    return (
      '<div class="event-recap">' +
      '<div class="recap" data-recap aria-label="' + escapeHtml(media.recap.label) + '">' +
      shot(media.poster) +
      '<div class="recap-side"><div class="recap-view">' + pages + "</div>" +
      '<button type="button" class="recap-arrow recap-prev" aria-label="Previous pictures"' + hidden + ">‹</button>" +
      '<button type="button" class="recap-arrow recap-next" aria-label="Next pictures"' + hidden + ">›</button>" +
      "</div></div></div>"
    );
  }

  function actions(event, media, withList) {
    const label = /hellorubric\.com/i.test(event.href || "") ? "View on Rubric" : "Details";
    const rubric = event.href
      ? '<a class="btn btn-small btn-lime" href="' + escapeHtml(event.href) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>"
      : "";
    const posters = media && media.poster
      ? '<a class="btn btn-small btn-ghost" href="/media/#' + encodeURIComponent(media.id) + '">Posters</a>'
      : "";
    const listLink = withList ? '<a class="btn btn-small btn-ghost" href="/events/">All events</a>' : "";
    if (!rubric && !posters && !listLink) return "";
    return rubric + posters + listLink;
  }

  function ticket(event, media) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    const poster = posterPreview(event, media);
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
      '<div class="event-actions">' + actions(event, media, true) + "</div>" +
      "</div></article>"
    );
  }

  function listedTicket(event, media) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    const href = media && media.poster ? "/media/#" + encodeURIComponent(media.id) : (event.href || "");
    const rubric = event.href
      ? '<a class="btn btn-small btn-lime" href="' + escapeHtml(event.href) + '" target="_blank" rel="noopener noreferrer">View on Rubric</a>'
      : "";
    const cue = media && media.poster
      ? '<a class="photos-cue" href="' + href + '">' + (media.recap ? "Photos →" : "Posters →") + "</a>"
      : "";
    return (
      '<article class="ticket has-poster">' +
      posterPreview(event, media) +
      (href ? '<a class="ticket-link" href="' + escapeHtml(href) + '" aria-label="Open ' + escapeHtml(event.title) + '"></a>' : "") +
      '<div class="ticket-stub">' +
      '<span class="kicker" style="color: var(--lime);">' + escapeHtml(card.kicker || "Club night") + "</span>" +
      "<strong>" + stubBig(card.big) + "</strong>" +
      "<span>" + escapeHtml(card.time || "") + "</span>" +
      "</div>" +
      '<div class="ticket-body">' +
      '<p class="kicker" style="color: var(--wine);">' + escapeHtml(card.place || event.where) + "</p>" +
      "<h3>" + escapeHtml(event.title) + "</h3>" +
      "<p>" + escapeHtml(card.blurb || event.summary) + "</p>" +
      '<div class="meta">' + chips + cue + "</div>" +
      (rubric ? '<div class="event-actions">' + rubric + "</div>" : "") +
      "</div></article>"
    );
  }

  function row(event, media) {
    const when = escapeHtml(event.whenLabel) + (event.whenDetail ? "<br>" + escapeHtml(event.whenDetail) : "");
    const datetime = event.datetime ? ' datetime="' + escapeHtml(event.datetime) + '"' : "";
    const tone = event.tone === "lime" || event.tone === "cyan" ? event.tone : "ghost";
    return (
      '<article class="event">' +
      "<time" + datetime + ">" + when + "</time>" +
      "<div><h3>" + escapeHtml(event.title) + "</h3>" +
      '<p class="where">' + escapeHtml(event.where) + "</p>" +
      "<p>" + escapeHtml(event.summary) + "</p>" +
      (event.href || (media && media.poster) ? '<div class="event-actions">' + actions(event, media, false) + "</div>" : "") +
      "</div>" +
      '<span class="chip chip-' + tone + '">' + escapeHtml(event.status) + "</span>" +
      "</article>"
    );
  }

  function pastBlock(event, media, heading) {
    const card = event.ticket || {};
    const chips = (card.chips || []).map(function (chip) {
      return '<span class="chip chip-ink">' + escapeHtml(chip) + "</span>";
    }).join("");
    const head = heading
      ? '<div class="section-head"><p class="kicker">Already ran</p><h2>' + escapeHtml(event.title) + ".</h2></div>"
      : '<div class="section-head"><h2>' + escapeHtml(event.title) + ".</h2></div>";
    const poster = !media || !media.recap ? posterPreview(event, media) : "";
    const article = (
      '<article class="ticket' + (poster ? " has-poster" : "") + '">' +
      poster +
      '<div class="ticket-stub">' +
      '<span class="kicker" style="color: var(--olive);">' + escapeHtml(card.kicker || "Past") + "</span>" +
      "<strong>" + stubBig(card.big) + "</strong>" +
      "<span>" + escapeHtml(card.time || "") + "</span>" +
      "</div>" +
      '<div class="ticket-body">' +
      '<p class="kicker" style="color: var(--wine);">' + escapeHtml(card.place || event.where) + "</p>" +
      "<h3>" + escapeHtml(event.title) + "</h3>" +
      "<p>" + escapeHtml(card.blurb || event.summary) + "</p>" +
      '<div class="meta">' + chips + (media && (media.recap || media.poster) ? '<span class="photos-cue">Photos →</span>' : "") + "</div>" +
      "</div></article>"
    );
    const linked = media && (media.recap || media.poster)
      ? '<a class="past-event" href="' + escapeHtml("/media/#" + encodeURIComponent(media.id || event.id || "")) + '">' + head + article + "</a>"
      : head + article;
    return '<div class="past-night">' + linked + recapHtml(media) + "</div>";
  }

  function renderUpcoming(events, catalog) {
    if (!events.length) {
      return '<p class="empty-state">No upcoming nights are on Rubric yet. When one is published there, it shows up here.</p>';
    }
    return '<div class="event-list">' + events.map(function (event) {
      const media = matchMedia(event, catalog);
      return media && media.poster ? listedTicket(event, media) : row(event, media);
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

  function renderPast(events, catalog) {
    const nights = events.slice();
    (catalog || []).forEach(function (item) {
      if (!item.past || !item.listed) return;
      const exists = nights.some(function (event) {
        return event.id === item.id || String(event.title || "").toLowerCase() === String(item.title || "").toLowerCase();
      });
      if (!exists) nights.push(item);
    });
    nights.sort(function (left, right) {
      return String(left.datetime || "").localeCompare(String(right.datetime || ""));
    });
    return nights.map(function (event, index) {
      return pastBlock(event, matchMedia(event, catalog), index === 0);
    }).join("");
  }

  function apply(data, catalog) {
    const events = data.events || [];
    const upcoming = events.filter(function (event) { return !event.past; });
    const past = events.filter(function (event) { return event.past; });
    const unavailable = data.rubric === false
      ? '<p class="empty-state">Rubric could not be loaded. Refresh in a moment.</p>'
      : "";
    if (next) {
      const media = upcoming[0] ? matchMedia(upcoming[0], catalog) : null;
      next.innerHTML = upcoming.length
        ? ticket(upcoming[0], media)
        : (unavailable || '<p class="empty-state">No upcoming nights are on Rubric yet. When one is published there, it shows up here.</p>');
    }
    if (list) list.innerHTML = upcoming.length || !unavailable ? renderUpcoming(upcoming, catalog) : unavailable;
    if (pastSlot) pastSlot.innerHTML = renderPast(past, catalog);
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
    fetch("/events/data.json").then(function (response) {
      if (!response.ok) throw new Error("events");
      return response.json();
    }).catch(function () { return { events: [] }; }),
    fetch("/api/club").then(function (response) {
      if (!response.ok) throw new Error("club");
      return response.json();
    })
  ]).then(function (results) {
    apply(results[1], (results[0] && results[0].events) || []);
  }).catch(function () {
    const message = '<p class="empty-state">Rubric could not be loaded. Refresh in a moment.</p>';
    if (next) next.innerHTML = message;
    if (list) list.innerHTML = message;
    fillSlots(teamSlots, message);
    fillSlots(merchSlots, message);
  });
})();
