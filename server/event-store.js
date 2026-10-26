const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const catalog = require("./events-catalog");
const rubric = require("./rubric-events");

const FILE = path.join(__dirname, "data", "event-visibility.json");
const TMP_FILE = "/tmp/unnatural-event-visibility.json";
const GITHUB_PATH = "server/data/event-visibility.json";
const MAX_CUSTOM = 40;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

let memory = null;

function token() {
  return process.env.EVENTS_GITHUB_TOKEN || process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";
}

function repo() {
  return process.env.GITHUB_REPOSITORY || "pawsp7/UnInt-Site";
}

function branch() {
  return process.env.EVENTS_BRANCH || process.env.VERCEL_GIT_COMMIT_REF || "main";
}

function ghHeaders(auth) {
  return {
    Authorization: `Bearer ${auth}`,
    Accept: "application/vnd.github+json",
    "User-Agent": "unnatural-intelligence-site",
    "X-GitHub-Api-Version": "2022-11-28"
  };
}

function emptyRecord() {
  return { visibility: {}, custom: [] };
}

function readJsonFile(file) {
  try {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
    return parsed;
  } catch (error) {
    return null;
  }
}

function normalize(raw) {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return emptyRecord();
  if (Object.prototype.hasOwnProperty.call(raw, "custom") || Object.prototype.hasOwnProperty.call(raw, "visibility")) {
    const visibility = {};
    const source = raw.visibility && typeof raw.visibility === "object" && !Array.isArray(raw.visibility) ? raw.visibility : {};
    for (const [key, value] of Object.entries(source)) {
      if (value === true && /^[a-z0-9-]{1,40}$/.test(key)) visibility[key] = true;
    }
    const custom = Array.isArray(raw.custom) ? raw.custom.map(storedCustom).filter(Boolean) : [];
    return { visibility, custom };
  }
  const visibility = {};
  for (const [key, value] of Object.entries(raw)) {
    if (value === true && /^[a-z0-9-]{1,40}$/.test(key)) visibility[key] = true;
  }
  return { visibility, custom: [] };
}

function readLocal() {
  return normalize(readJsonFile(TMP_FILE) || readJsonFile(FILE) || {});
}

function readRecord() {
  if (memory) return { visibility: { ...memory.visibility }, custom: memory.custom.map((event) => ({ ...event })) };
  memory = readLocal();
  return { visibility: { ...memory.visibility }, custom: memory.custom.map((event) => ({ ...event })) };
}

function writeLocal(record) {
  const text = `${JSON.stringify(record, null, 2)}\n`;
  memory = { visibility: { ...record.visibility }, custom: record.custom.map((event) => ({ ...event })) };
  let persisted = false;
  for (const file of [FILE, TMP_FILE]) {
    try {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, text);
      if (file === FILE) persisted = true;
    } catch (error) {
      /* read-only deploy filesystem */
    }
  }
  return persisted;
}

async function readRemote() {
  const auth = token();
  if (!auth) return null;
  const url = `https://api.github.com/repos/${repo()}/contents/${GITHUB_PATH}?ref=${encodeURIComponent(branch())}`;
  try {
    const response = await fetch(url, { headers: ghHeaders(auth) });
    if (response.status === 404) return { record: emptyRecord(), sha: null };
    if (!response.ok) return null;
    const data = await response.json();
    const record = normalize(JSON.parse(Buffer.from(data.content, "base64").toString("utf8")));
    return { record, sha: data.sha };
  } catch (error) {
    return null;
  }
}

async function writeRemote(record, sha) {
  const auth = token();
  if (!auth) return false;
  const url = `https://api.github.com/repos/${repo()}/contents/${GITHUB_PATH}`;
  const body = {
    message: "Update club events from the exec desk",
    content: Buffer.from(`${JSON.stringify(record, null, 2)}\n`).toString("base64"),
    branch: branch()
  };
  if (sha) body.sha = sha;
  try {
    const response = await fetch(url, {
      method: "PUT",
      headers: { ...ghHeaders(auth), "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

async function currentRecord() {
  const remote = await readRemote();
  if (remote) {
    memory = { visibility: { ...remote.record.visibility }, custom: remote.record.custom.map((event) => ({ ...event })) };
    return { record: readRecord(), sha: remote.sha, remote: true };
  }
  return { record: readRecord(), sha: null, remote: false };
}

async function save(record, current) {
  const local = writeLocal(record);
  const remote = current.remote || token() ? await writeRemote(record, current.sha) : false;
  return { persisted: local || remote, events: decorate(record) };
}

function text(value, max) {
  return String(value == null ? "" : value).replace(/\s+/g, " ").trim().slice(0, max);
}

function dateParts(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value || "");
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

function httpsLink(value) {
  const raw = text(value, 300);
  if (!raw) return "";
  try {
    const url = new URL(raw);
    if (url.protocol !== "https:") return null;
    return url.toString();
  } catch (error) {
    return null;
  }
}

function storedCustom(raw) {
  if (!raw || typeof raw !== "object") return null;
  const id = text(raw.id, 40);
  const title = text(raw.title, 80);
  if (!/^custom-[a-z0-9-]{4,32}$/.test(id) || !title) return null;
  const when = dateParts(text(raw.date, 10));
  const link = httpsLink(raw.link);
  return {
    id,
    title,
    date: when ? when.iso : "",
    time: text(raw.time, 40),
    place: text(raw.place, 120),
    summary: text(raw.summary, 400),
    link: link || "",
    past: raw.past === true,
    visible: raw.visible !== false
  };
}

function presentCustom(item) {
  const when = dateParts(item.date);
  const where = item.place || "Place to be posted";
  const summary = item.summary || item.title;
  const time = item.time || (item.past ? "" : "Time TBA");
  return {
    id: item.id,
    title: item.title,
    whenLabel: when ? `${when.weekday} ${when.day} ${when.monthName}` : "Date TBA",
    whenDetail: item.time,
    datetime: when ? `${when.iso}T12:00` : "",
    where,
    summary,
    status: item.past ? "Past" : "Confirmed",
    tone: item.past ? "ghost" : "lime",
    past: item.past,
    custom: true,
    visible: item.visible === true,
    href: item.link,
    ticket: {
      kicker: item.past ? "Past" : "Club night",
      big: when ? `${when.day}<br>${when.monthName}` : "TBA",
      time,
      place: where,
      blurb: summary,
      chips: [item.past ? "Past" : "Club night"]
    }
  };
}

function knownCatalog(id) {
  return catalog.some((event) => event.id === id);
}

function decorate(record) {
  const custom = record.custom.map(presentCustom);
  const listed = catalog.map((event) => ({
    ...event,
    visible: record.visibility[event.id] === true
  }));
  return [...custom, ...listed];
}

function publicEvent(event) {
  const copy = { ...event };
  delete copy.visible;
  return copy;
}

function isClubExpo(event) {
  const title = String(event.title || "").toLowerCase();
  const id = String(event.id || "").toLowerCase();
  return id === "fall-showcase" || title.includes("club expo") || title.includes("clubs expo") || title.includes("fall showcase");
}

function hiddenForNow(event) {
  // The catalog row is an undated proposal. The booked Monday nights come from Rubric.
  return String(event.id || "").toLowerCase() === "unnatural-games";
}

function byWhen(left, right) {
  const a = left.datetime || "9999-99-99";
  const b = right.datetime || "9999-99-99";
  return a.localeCompare(b) || left.title.localeCompare(right.title);
}

async function listAll() {
  const { record } = await currentRecord();
  return decorate(record).filter((event) => !hiddenForNow(event));
}

async function listPublic() {
  const events = await listAll();
  const local = events.filter((event) => (event.custom ? event.visible : event.past || event.visible)).map(publicEvent);
  const fromRubric = await rubric.upcoming();
  const rubricTitles = new Set(fromRubric.events.map((event) => event.title.toLowerCase()));
  const upcoming = [
    ...fromRubric.events,
    ...local.filter((event) => !event.past && !rubricTitles.has(event.title.toLowerCase()))
  ].filter((event) => !isClubExpo(event) && !hiddenForNow(event)).sort(byWhen);
  const past = local.filter((event) => event.past && !isClubExpo(event) && !hiddenForNow(event)).sort(byWhen);
  return { events: [...upcoming, ...past], rubricOk: fromRubric.ok };
}

async function setVisible(id, visible) {
  const current = await currentRecord();
  const record = current.record;
  if (knownCatalog(id)) {
    if (visible) record.visibility[id] = true;
    else delete record.visibility[id];
    return save(record, current);
  }
  const custom = record.custom.find((event) => event.id === id);
  if (!custom) return null;
  custom.visible = visible === true;
  return save(record, current);
}

function draftCustom(input) {
  const title = text(input.title, 80);
  if (!title) return { error: "Give the night a title." };
  const dateText = text(input.date, 10);
  if (dateText && !dateParts(dateText)) return { error: "Use a real date, or leave the date blank." };
  const link = httpsLink(input.link);
  if (link === null) return { error: "Use an https link, or leave the link blank." };
  return {
    event: {
      id: `custom-${crypto.randomBytes(4).toString("hex")}`,
      title,
      date: dateText,
      time: text(input.time, 40),
      place: text(input.place, 120),
      summary: text(input.summary, 400),
      link,
      past: input.past === true,
      visible: true
    }
  };
}

async function createCustom(input) {
  const draft = draftCustom(input || {});
  if (draft.error) return draft;
  const current = await currentRecord();
  const record = current.record;
  if (record.custom.length >= MAX_CUSTOM) {
    return { error: "The desk already has 40 custom nights. Remove one before adding another." };
  }
  record.custom.unshift(draft.event);
  return save(record, current);
}

async function deleteCustom(id) {
  if (!/^custom-[a-z0-9-]{4,32}$/.test(id)) return null;
  const current = await currentRecord();
  const record = current.record;
  const next = record.custom.filter((event) => event.id !== id);
  if (next.length === record.custom.length) return null;
  record.custom = next;
  return save(record, current);
}

module.exports = {
  listAll,
  listPublic,
  setVisible,
  createCustom,
  deleteCustom
};
