import { existsSync, readdirSync, readFileSync } from "node:fs";
import { basename, join } from "node:path";
import { imageSize, isImage } from "./event-media.mjs";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function dateParts(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value || "").trim());
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
  return {
    iso: match[0],
    day,
    weekday: WEEKDAYS[date.getUTCDay()],
    monthName: MONTHS[month - 1],
    year
  };
}

function todayIso(now = new Date()) {
  return now.toISOString().slice(0, 10);
}

function listImages(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((name) => isImage(name) && !name.startsWith("."))
    .sort((a, b) => a.localeCompare(b, "en", { numeric: true, sensitivity: "base" }));
}

function publicSrc(eventId, rel) {
  return `/assets/events/${eventId}/${rel}`;
}

function describeImage(event, file, fallback) {
  const alts = event.alts && typeof event.alts === "object" ? event.alts : {};
  return alts[file] || alts[basename(file)] || fallback;
}

function shotFrom(event, folderRel, file, extra = {}) {
  const abs = join(event.dir, folderRel, file);
  const size = existsSync(abs) ? imageSize(abs) : { width: 0, height: 0 };
  const classNames = extra.className || "";
  return {
    src: publicSrc(event.id, folderRel ? `${folderRel}/${file}` : file),
    file,
    width: size.width || extra.width || 1600,
    height: size.height || extra.height || 1067,
    alt: extra.alt || describeImage(event, file, extra.fallback || `Image from ${event.title}.`),
    className: classNames,
    lazy: extra.lazy === true
  };
}

function paginateRecap(photos, wideNames) {
  if (!photos.length) return [];
  const marked = photos.map((photo, index) => {
    const wide = wideNames.has(photo.file) || (index === 0 && photo.width > photo.height * 1.15);
    return { ...photo, className: [photo.className, wide ? "wide" : ""].filter(Boolean).join(" ") };
  });
  const pages = [];
  const firstCount = /\bwide\b/.test(marked[0].className) ? 5 : 6;
  pages.push(marked.slice(0, firstCount));
  for (let i = firstCount; i < marked.length; i += 6) {
    pages.push(marked.slice(i, i + 6).map((photo) => ({ ...photo, lazy: true })));
  }
  return pages;
}

export function loadEvents(root) {
  const manifestPath = join(root, "site/events/events.json");
  const raw = JSON.parse(readFileSync(manifestPath, "utf8"));
  const records = Array.isArray(raw.events) ? raw.events : [];
  const today = todayIso();
  return records.map((item) => presentEvent(root, item, today));
}

function presentEvent(root, item, today) {
  const id = String(item.id || "").trim();
  const dir = join(root, "site/events", id);
  const when = dateParts(item.date);
  const recapFiles = listImages(join(dir, "recap"));
  const posterFiles = listImages(join(dir, "posters"));
  const past = item.past === true || recapFiles.length > 0 || Boolean(when && item.date < today && item.past !== false);
  const listed = item.listed !== false;
  const media = item.media !== false && Boolean(item.poster || recapFiles.length || posterFiles.length);
  const event = {
    ...item,
    id,
    dir,
    title: item.title || id,
    past,
    listed,
    media,
    featured: item.featured === true,
    datetime: when ? when.iso : "",
    whenLabel: when ? `${when.day} ${when.monthName} ${when.year}` : (item.whenLabel || (past ? "Date TBA" : "Date TBA")),
    whenDetail: item.time || "",
    where: item.place || "",
    summary: item.summary || "",
    status: past ? "Past" : (item.statusLabel || "Upcoming"),
    tone: item.tone || (past ? "ghost" : "cyan"),
    posterFile: item.poster || "",
    recapFiles,
    posterFiles,
    announce: item.announce === true || (item.announce !== false && !past && Boolean(item.poster) && item.statusLabel !== "Proposed")
  };

  const posterPath = event.posterFile ? join(dir, event.posterFile) : "";
  event.poster = posterPath && existsSync(posterPath)
    ? shotFrom(event, "", event.posterFile, {
      alt: item.posterAlt || describeImage(event, event.posterFile, `${event.title} poster.`),
      className: "poster",
      fallback: `${event.title} poster.`
    })
    : null;

  const wide = new Set((item.layout && item.layout.wide) || []);
  const classes = (item.layout && item.layout.classes) || {};
  const recapPhotos = recapFiles.map((file) => shotFrom(event, "recap", file, {
    className: classes[file] || "",
    fallback: `Photograph from ${event.title}.`
  }));
  event.recap = recapPhotos.length
    ? {
      label: `Pictures from ${event.title}`,
      pages: paginateRecap(recapPhotos, wide)
    }
    : null;

  event.posters = posterFiles.map((file) => shotFrom(event, "posters", file, {
    className: "sheet",
    fallback: `${event.title} poster.`
  }));

  event.ticket = {
    kicker: item.kicker || (past ? "Past" : "Club night"),
    big: when ? `${when.day}<br>${when.monthName}` : (item.ticketBig || "TBA"),
    time: item.time || (past ? "" : "Time TBA"),
    place: item.place || "Place to be posted",
    blurb: item.blurb || item.summary || "",
    chips: [...(past ? ["Past"] : []), ...(Array.isArray(item.chips) ? item.chips : [])]
  };

  return event;
}

export function publicEvent(event) {
  return {
    id: event.id,
    title: event.title,
    past: event.past,
    listed: event.listed,
    media: event.media,
    featured: event.featured,
    datetime: event.datetime,
    whenLabel: event.whenLabel,
    whenDetail: event.whenDetail,
    where: event.where,
    summary: event.summary,
    status: event.status,
    tone: event.tone,
    ticket: event.ticket,
    poster: event.poster,
    posters: event.posters,
    recap: event.recap
  };
}

export function inject(html, name, inner) {
  const re = new RegExp(`<!-- inject:${name} -->[\\s\\S]*?<!-- /inject:${name} -->`);
  if (!re.test(html)) {
    throw new Error(`Missing <!-- inject:${name} --> marker`);
  }
  return html.replace(re, `<!-- inject:${name} -->\n${inner}\n<!-- /inject:${name} -->`);
}

function shotHtml(image) {
  const lazy = image.lazy ? " loading=\"lazy\"" : "";
  const klass = image.className ? ` ${image.className}` : "";
  return (
    `<a class="shot${klass}" href="${escapeHtml(image.src)}">` +
    `<img src="${escapeHtml(image.src)}" width="${image.width}" height="${image.height}" alt="${escapeHtml(image.alt)}"${lazy}>` +
    "</a>"
  );
}

function chipsHtml(chips) {
  return (chips || []).map((chip) => `<span class="chip chip-ink">${escapeHtml(chip)}</span>`).join("");
}

export function recapHtml(event) {
  if (!event.recap || !event.poster) return "";
  const pages = event.recap.pages.map((page) => `<div class="recap-page">${page.map(shotHtml).join("")}</div>`).join("");
  const hidden = event.recap.pages.length > 1 ? "" : " hidden";
  return (
    `<div class="event-recap"><div class="recap" data-recap aria-label="${escapeHtml(event.recap.label)}">` +
    shotHtml(event.poster) +
    `<div class="recap-side"><div class="recap-view">${pages}</div>` +
    `<button type="button" class="recap-arrow recap-prev" aria-label="Previous pictures"${hidden}>‹</button>` +
    `<button type="button" class="recap-arrow recap-next" aria-label="Next pictures"${hidden}>›</button>` +
    "</div></div></div>"
  );
}

function stubBig(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/&lt;br\s*\/?&gt;/gi, "<br>");
}

export function ticketHtml(event, options = {}) {
  const card = event.ticket || {};
  const poster = options.withPoster && event.poster
    ? `<a class="shot episode-poster event-poster" href="${escapeHtml(event.poster.src)}"><img src="${escapeHtml(event.poster.src)}" width="${event.poster.width}" height="${event.poster.height}" alt="${escapeHtml(event.poster.alt)}"></a>`
    : "";
  const media = event.recap ? `/media/#${encodeURIComponent(event.id)}` : (event.poster ? event.poster.src : "");
  const link = options.link && media
    ? `<a class="ticket-link" href="${escapeHtml(media)}" aria-label="${event.recap ? "Photos" : "Poster"} for ${escapeHtml(event.title)}"></a>`
    : "";
  const cue = options.photosCue
    ? (options.photosCue === "span"
      ? `<span class="photos-cue">${event.recap ? "Photos →" : "Poster →"}</span>`
      : (event.recap
        ? `<a class="photos-cue" href="${escapeHtml(media)}">Photos →</a>`
        : (event.poster ? `<a class="photos-cue" href="${escapeHtml(event.poster.src)}">Poster →</a>` : "")))
    : "";
  return (
    `<article class="ticket${poster ? " has-poster" : ""}">${poster}${link}` +
    `<div class="ticket-stub"><span class="kicker" style="color: var(--${options.stubColor || "lime"});">${escapeHtml(card.kicker || "")}</span>` +
    `<strong>${stubBig(card.big)}</strong><span>${escapeHtml(card.time || "")}</span></div>` +
    `<div class="ticket-body"><p class="kicker" style="color: var(--wine);">${escapeHtml(card.place || event.where)}</p>` +
    `<h3>${escapeHtml(event.title)}</h3><p>${escapeHtml(card.blurb || event.summary)}</p>` +
    `<div class="meta">${chipsHtml(card.chips)}${cue}</div></div></article>`
  );
}

export function pastBlockHtml(event, heading) {
  const head = heading
    ? `<div class="section-head"><p class="kicker">Already ran</p><h2>${escapeHtml(event.title)}.</h2></div>`
    : `<div class="section-head"><h2>${escapeHtml(event.title)}.</h2></div>`;
  const article = ticketHtml(event, {
    stubColor: "olive",
    withPoster: !event.recap && Boolean(event.poster),
    photosCue: event.recap || event.poster ? "span" : false
  });
  const linked = event.recap || event.media
    ? `<a class="past-event" href="/media/#${encodeURIComponent(event.id)}">${head}${article}</a>`
    : head + article;
  return `<div class="past-night">${linked}${recapHtml(event)}</div>`;
}

export function upcomingHtml(events) {
  if (!events.length) {
    return `<p class="empty-state">No upcoming nights are posted yet. When one is on <a href="https://campus.hellorubric.com/?s=16226">Rubric</a>, it shows up here.</p>`;
  }
  return `<div class="event-list">${events.map((event) => {
    if (event.poster) return ticketHtml(event, { withPoster: true, link: true, photosCue: true, stubColor: "lime" });
    const datetime = event.datetime ? ` datetime="${escapeHtml(event.datetime)}"` : "";
    const tone = event.tone === "lime" || event.tone === "cyan" ? event.tone : "ghost";
    return (
      `<article class="event"><time${datetime}>${escapeHtml(event.whenLabel)}${event.whenDetail ? `<br>${escapeHtml(event.whenDetail)}` : ""}</time>` +
      `<div><h3>${escapeHtml(event.title)}</h3><p class="where">${escapeHtml(event.where)}</p><p>${escapeHtml(event.summary)}</p></div>` +
      `<span class="chip chip-${tone}">${escapeHtml(event.status)}</span></article>`
    );
  }).join("")}</div>`;
}

export function pastHtml(events) {
  if (!events.length) return `<p class="empty-state">Past nights will land here with their poster and recap photos.</p>`;
  return events.map((event, index) => pastBlockHtml(event, index === 0)).join("");
}

export function featuredHtml(events) {
  if (!events.length) return "";
  return events.map((event) => {
    if (!event.poster) return "";
    const caption = [event.whenLabel, event.whenDetail, event.where].filter(Boolean).join(" · ");
    return (
      `<figure><a class="shot episode-poster" href="${escapeHtml(event.poster.src)}">` +
      `<img src="${escapeHtml(event.poster.src)}" width="${event.poster.width}" height="${event.poster.height}" alt="${escapeHtml(event.poster.alt)}">` +
      `</a><figcaption><a href="/media/#${encodeURIComponent(event.id)}">${escapeHtml(event.title)}</a>` +
      `<span>${escapeHtml(caption)}</span></figcaption></figure>`
    );
  }).join("");
}

function posterFigure(image, event, caption) {
  return (
    `<figure><a class="shot episode-poster" href="${escapeHtml(image.src)}">` +
    `<img src="${escapeHtml(image.src)}" width="${image.width}" height="${image.height}" alt="${escapeHtml(image.alt)}">` +
    `</a><figcaption><span>${escapeHtml(caption || event.title)}</span></figcaption></figure>`
  );
}

export function mediaNightHtml(event) {
  const kicker = [event.whenLabel, event.whenDetail, event.where].filter(Boolean).join(" · ");
  const recap = recapHtml(event);
  const sheets = [];
  if (event.poster && !event.recap) sheets.push(event.poster);
  sheets.push(...(event.posters || []));
  const sheetGrid = sheets.length
    ? `${event.recap ? `<div class="section-head night-sheets-head"><p class="kicker">Print</p><h2>More sheets.</h2></div>` : ""}` +
      `<div class="poster-feature sheets">${sheets.map((image) => posterFigure(image, event)).join("")}</div>`
    : "";
  return (
    `<article class="night" id="${escapeHtml(event.id)}">` +
    `<p class="kicker">${escapeHtml(kicker)}</p>` +
    `<h2>${escapeHtml(event.title)}</h2>` +
    `<p class="night-note">${escapeHtml(event.summary)}</p>` +
    recap +
    sheetGrid +
    "</article>"
  );
}

export function mediaHtml(events) {
  const ran = events.filter((event) => event.past && (event.recap || event.poster));
  const board = events.filter((event) => !event.past && event.media);
  const ranBlock = ran.length
    ? `<div class="section-head"><p class="kicker">From the room</p><h2>Nights that already ran.</h2><p>The poster, then the pictures from that night. A night on the <a href="/events/">Events</a> page opens its set here.</p></div>${ran.map(mediaNightHtml).join("")}`
    : "";
  const boardBlock = board.length
    ? `<div class="section-head" style="margin-top: 48px;"><p class="kicker">On the board</p><h2>Posters still in play.</h2><p>Sheets for nights that are proposed or waiting on a room. Drop recap photos in the event folder after the night runs.</p></div>${board.map(mediaNightHtml).join("")}`
    : "";
  return ranBlock + boardBlock;
}

export function splitEvents(events, now = new Date()) {
  const today = todayIso(now);
  const publicEvents = events.filter((event) => event.listed);
  const upcoming = publicEvents.filter((event) => !event.past && event.announce && !(event.datetime && event.datetime < today));
  const past = publicEvents.filter((event) => event.past || (event.datetime && event.datetime < today)).sort((a, b) => String(a.datetime).localeCompare(String(b.datetime)));
  const featured = events.filter((event) => event.featured && event.poster).sort((a, b) => String(b.datetime).localeCompare(String(a.datetime)));
  const media = events.filter((event) => event.media);
  return { upcoming, past, featured, media };
}
