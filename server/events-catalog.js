/** Club nights. `visible` is not stored here.
 *  Source of truth: site/events/events.json
 *  An upcoming night stays off the public site until an exec checks it.
 *  A past night stays on the Events page.
 */
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const raw = require("../site/events/events.json");

function dateParts(value) {
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
    monthName: MONTHS[month - 1]
  };
}

function toCatalog(item) {
  const when = dateParts(item.date);
  const past = item.past === true;
  return {
    id: item.id,
    title: item.title,
    whenLabel: when ? `${when.day} ${when.monthName}` : (item.whenLabel || "Date TBA"),
    whenDetail: item.time || "",
    datetime: when ? when.iso : "",
    where: item.place || "",
    summary: item.summary || "",
    status: past ? "Past" : (item.statusLabel || "Upcoming"),
    tone: item.tone || (past ? "ghost" : "cyan"),
    past,
    ticket: {
      kicker: item.kicker || (past ? "Past" : "Club night"),
      big: when ? `${when.day}<br>${when.monthName}` : (item.ticketBig || "TBA"),
      time: item.time || (past ? "" : "Time TBA"),
      place: item.place || "Place to be posted",
      blurb: item.blurb || item.summary || "",
      chips: [...(past ? ["Past"] : []), ...(Array.isArray(item.chips) ? item.chips : [])]
    }
  };
}

function load() {
  const events = Array.isArray(raw.events) ? raw.events : [];
  return events.filter((item) => item && item.id && item.listed !== false).map(toCatalog);
}

module.exports = load();
