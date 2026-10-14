/** Upcoming nights from the public Rubric club page.
 *  https://campus.hellorubric.com/?s=16226
 *  The landing call lists events. A second call per event adds the description.
 */

const SOCIETY_ID = "16226";
const API = "https://api.hellorubric.com";
const DETAILS_ENDPOINT = "https://appserver.getqpay.com:9090/AppServerSwapnil/event/details";
const CLUB_PAGE = `https://campus.hellorubric.com/?s=${SOCIETY_ID}`;
const CACHE_MS = 10 * 60 * 1000;

const MONTHS = {
  jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6,
  jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12
};

let cache = { at: 0, payload: null };

function decodeEntities(value) {
  return String(value || "")
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)))
    .replace(/&#x([0-9a-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)))
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&quot;/gi, "\"")
    .replace(/&apos;|&#39;/gi, "'")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">");
}

function plainText(html) {
  return decodeEntities(
    String(html || "")
      .replace(/<\s*br\s*\/?>/gi, " ")
      .replace(/<\/\s*p\s*>/gi, " ")
      .replace(/<[^>]+>/g, " ")
  ).replace(/\s+/g, " ").trim();
}

function brief(text, max = 280, title = "") {
  let clean = plainText(text);
  const heading = plainText(title);
  if (heading && clean.toLowerCase().startsWith(heading.toLowerCase())) {
    clean = clean.slice(heading.length).replace(/^[\s:–—-]+/, "");
  }
  clean = clean.replace(/^[A-Za-z]+days?,?\s+\d{1,2}(?::\d{2})?\s*(?:[AP]M)?\s*[–-]\s*\d{1,2}(?::\d{2})?\s*(?:[AP]M)?\.?\s*/i, "");
  if (clean.length <= max) return clean;
  const slice = clean.slice(0, max);
  const stop = Math.max(slice.lastIndexOf(". "), slice.lastIndexOf("! "), slice.lastIndexOf("? "));
  if (stop >= 80) return slice.slice(0, stop + 1);
  const space = slice.lastIndexOf(" ");
  return `${(space >= 80 ? slice.slice(0, space) : slice).trim()}…`;
}

function clock(value) {
  const match = String(value || "").match(/(\d{1,2})[.:](\d{2})\s*(AM|PM)/i);
  if (!match) return "";
  return `${Number(match[1])}:${match[2]} ${match[3].toUpperCase()}`;
}

function timeRange(start, end) {
  const from = clock(start);
  const to = clock(end);
  if (!from) return "";
  if (!to) return from;
  const [fromTime, fromMeridiem] = from.split(" ");
  const [toTime, toMeridiem] = to.split(" ");
  if (fromMeridiem === toMeridiem) return `${fromTime}–${toTime} ${toMeridiem}`;
  return `${from}–${to}`;
}

function dateParts(value) {
  const match = String(value || "").match(/([A-Za-z]{3}),?\s+(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})/);
  if (!match) return null;
  const month = MONTHS[match[3].toLowerCase()];
  if (!month) return null;
  const day = Number(match[2]);
  const year = Number(match[4]);
  return {
    weekday: match[1],
    day,
    month,
    monthName: match[3],
    year,
    sort: `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`
  };
}

function shortPlace(address) {
  const parts = String(address || "").split(",").map((part) => part.trim()).filter(Boolean);
  const kept = [];
  for (const part of parts) {
    if (/^(canada|ab|alberta)$/i.test(part)) break;
    if (/\d/.test(part) && /avenue|street|road|drive|way/i.test(part)) break;
    kept.push(part);
    if (kept.length === 2) break;
  }
  return kept.join(", ");
}

function money(amount) {
  const value = Number(amount);
  if (!Number.isFinite(value)) return "";
  const cents = Math.round(value * 100);
  if (cents % 100 === 0) return String(cents / 100);
  return (cents / 100).toFixed(2);
}

function labelFromAmounts(amounts, fallback) {
  if (!amounts.length) return fallback;
  const low = Math.min(...amounts);
  const high = Math.max(...amounts);
  if (high === 0) return "Free";
  if (low === 0) return `Free or $${money(high)}`;
  if (low === high) return `$${money(low)}`;
  return `$${money(low)}–$${money(high)}`;
}

function priceLabel(info, tickets) {
  const text = String(info || "").trim();
  const fromTickets = Array.isArray(tickets)
    ? tickets.map((ticket) => Number(ticket.amount)).filter((amount) => Number.isFinite(amount))
    : [];
  if (fromTickets.length) return labelFromAmounts(fromTickets, text || "On Rubric");
  if (!text || /^free$/i.test(text)) return "Free";
  const fromText = [...text.matchAll(/\$(\d+(?:\.\d+)?)/g)].map((match) => Number(match[1]));
  return labelFromAmounts(fromText, text.replace(/\.00/g, ""));
}

function rubricUrl(value, fallback) {
  const backup = fallback || CLUB_PAGE;
  try {
    const url = new URL(String(value || backup));
    if (url.protocol !== "https:" || url.hostname !== "campus.hellorubric.com") return backup;
    url.searchParams.delete("fromsite");
    return url.toString();
  } catch (error) {
    return backup;
  }
}

function eventLink(value, eventId) {
  return rubricUrl(value, `https://campus.hellorubric.com/?eid=${encodeURIComponent(eventId)}`);
}

function imageUrl(value) {
  try {
    const url = new URL(String(value || ""));
    if (url.protocol !== "https:" || url.hostname !== "resources.hellorubric.com") return "";
    return url.toString();
  } catch (error) {
    return "";
  }
}

function roleRank(role) {
  const text = String(role || "").toLowerCase();
  if (text.includes("vice")) return 1;
  if (text.includes("president")) return 0;
  if (text.includes("treasurer") || text.includes("finance")) return 2;
  if (text.includes("community")) return 3;
  if (text.includes("training")) return 4;
  return 5;
}

function toMember(card, index) {
  const name = plainText(card && card.title);
  const role = plainText(card && card.subtitle);
  if (!name || !role) return null;
  return {
    id: `rubric-exec-${card.id || index}`,
    name,
    role,
    photo: imageUrl(card.image),
    href: CLUB_PAGE,
    order: index
  };
}

function toMerch(card) {
  const title = plainText(card && card.title);
  if (!title || !card.itemid) return null;
  const price = priceLabel(card.info);
  return {
    id: `rubric-merch-${card.itemid}`,
    title,
    summary: brief(String(card.subtitle || "").replace(/<\s*br\s*\/?>/gi, " · "), 320, title)
      .replace(/(?:\s*·\s*){2,}/g, " · ")
      .replace(/\s*·\s*-+\s*/g, " · ")
      .replace(/^·\s*/, "")
      .replace(/\s*·\s*$/, ""),
    price,
    image: imageUrl(card.image),
    href: rubricUrl(card.destination, `https://campus.hellorubric.com/merchandiseitem?item=${encodeURIComponent(card.itemid)}&merid=${SOCIETY_ID}`)
  };
}

function toPublicEvent(card, details) {
  const eventId = card.eventid;
  const info = details && details.eventDetails ? details.eventDetails : {};
  const when = dateParts(info.eventTime || card.formatteddate);
  if (!when || !eventId || !card.title) return null;
  const range = timeRange(info.eventTime || card.formatteddate, info.eventEndTime);
  const sortTime = clock(info.eventTime || card.formatteddate) || "12:00 AM";
  const [hourText, minuteText] = sortTime.match(/(\d{1,2}):(\d{2})/).slice(1);
  let hour = Number(hourText);
  const meridiem = /PM/i.test(sortTime) ? "PM" : "AM";
  if (meridiem === "PM" && hour < 12) hour += 12;
  if (meridiem === "AM" && hour === 12) hour = 0;
  const summary = brief(info.eventDescription, 280, card.title) || shortPlace(info.eventAddress || card.subtitle);
  const where = shortPlace(info.eventAddress || card.subtitle);
  const price = priceLabel(card.info, info.ticketTypeDetails);
  const href = eventLink(info.eventURL || card.destination, eventId);
  return {
    id: `rubric-${eventId}`,
    title: plainText(card.title),
    whenLabel: `${when.weekday} ${when.day} ${when.monthName}`,
    whenDetail: range,
    datetime: `${when.sort}T${String(hour).padStart(2, "0")}:${minuteText}`,
    where,
    summary,
    status: price,
    tone: price === "Free" ? "lime" : "cyan",
    past: false,
    href,
    ticket: {
      kicker: "On Rubric",
      big: `${when.day}<br>${when.monthName}`,
      time: range,
      place: where,
      blurb: summary,
      chips: [price]
    }
  };
}

async function rubricPost(endpoint, details) {
  const body = new URLSearchParams({
    endpoint,
    details: JSON.stringify({
      ...details,
      domain: "campus.hellorubric.com",
      device: "web_portal",
      version: 4,
      timestamp: Date.now(),
      currentUrl: CLUB_PAGE
    })
  });
  const response = await fetch(API, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      Accept: "application/json",
      "User-Agent": "unnatural-intelligence-site",
      Origin: "https://campus.hellorubric.com",
      Referer: CLUB_PAGE
    },
    body,
    signal: AbortSignal.timeout(8000)
  });
  if (!response.ok) throw new Error(`Rubric ${endpoint} returned ${response.status}`);
  const data = await response.json();
  if (!data || data.success === false) throw new Error(`Rubric ${endpoint} was not successful`);
  return data;
}

function sectionItems(sections, name) {
  const section = sections.find((item) => item && item.sectionname === name);
  return section && Array.isArray(section.array) ? section.array : [];
}

async function loadClub() {
  const landing = await rubricPost("getSocietyLandingPage", { societyid: SOCIETY_ID });
  const sections = Array.isArray(landing.sections) ? landing.sections : [];
  const cards = sectionItems(sections, "Events")
    .filter((card) => card && Number(card.upcoming) === 1 && card.eventid && card.title);

  const events = (await Promise.all(cards.map(async (card) => {
    try {
      const details = await rubricPost(DETAILS_ENDPOINT, { eventId: card.eventid });
      return toPublicEvent(card, details);
    } catch (error) {
      return toPublicEvent(card, null);
    }
  })))
    .filter(Boolean)
    .sort((left, right) => left.datetime.localeCompare(right.datetime) || left.title.localeCompare(right.title));

  const team = sectionItems(sections, "Committee")
    .map(toMember)
    .filter(Boolean)
    .sort((left, right) => roleRank(left.role) - roleRank(right.role) || left.order - right.order)
    .map((member) => {
      const copy = { ...member };
      delete copy.order;
      return copy;
    });

  const merchandise = sectionItems(sections, "Merchandise").map(toMerch).filter(Boolean);
  return { events, team, merchandise };
}

async function club() {
  if (cache.payload && Date.now() - cache.at < CACHE_MS) return { ...cache.payload, ok: true };
  try {
    const payload = await loadClub();
    cache = { at: Date.now(), payload };
    return { ...payload, ok: true };
  } catch (error) {
    if (cache.payload) return { ...cache.payload, ok: true };
    return { events: [], team: [], merchandise: [], ok: false };
  }
}

async function upcoming() {
  const result = await club();
  return { events: result.events, ok: result.ok };
}

module.exports = {
  upcoming,
  club,
  toPublicEvent,
  toMember,
  toMerch,
  brief,
  shortPlace,
  priceLabel,
  timeRange,
  CLUB_PAGE
};
