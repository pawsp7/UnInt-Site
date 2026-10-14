const fs = require("fs");
const path = require("path");
const catalog = require("./events-catalog");
const rubric = require("./rubric-events");

const FILE = path.join(__dirname, "data", "event-visibility.json");
const TMP_FILE = "/tmp/unnatural-event-visibility.json";
const GITHUB_PATH = "server/data/event-visibility.json";

let memory = null;

function token() {
  return process.env.EVENTS_GITHUB_TOKEN || process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";
}

function repo() {
  return process.env.GITHUB_REPOSITORY || "pawsp7/Unnatural-Intelligence";
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

function readJsonFile(file) {
  try {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8"));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
    return parsed;
  } catch (error) {
    return null;
  }
}

function readLocal() {
  return readJsonFile(TMP_FILE) || readJsonFile(FILE) || {};
}

function readMap() {
  if (memory) return { ...memory };
  memory = readLocal();
  return { ...memory };
}

function writeLocal(map) {
  const text = `${JSON.stringify(map, null, 2)}\n`;
  memory = { ...map };
  let persisted = false;
  for (const file of [FILE, TMP_FILE]) {
    try {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, text);
      persisted = file === FILE || persisted;
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
    if (response.status === 404) return { map: {}, sha: null };
    if (!response.ok) return null;
    const data = await response.json();
    const map = JSON.parse(Buffer.from(data.content, "base64").toString("utf8"));
    if (!map || typeof map !== "object" || Array.isArray(map)) return null;
    return { map, sha: data.sha };
  } catch (error) {
    return null;
  }
}

async function writeRemote(map, sha) {
  const auth = token();
  if (!auth) return false;
  const url = `https://api.github.com/repos/${repo()}/contents/${GITHUB_PATH}`;
  const body = {
    message: "Publish club events selected on the exec desk",
    content: Buffer.from(`${JSON.stringify(map, null, 2)}\n`).toString("base64"),
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

function known(id) {
  return catalog.some((event) => event.id === id);
}

function decorate(map) {
  return catalog.map((event) => ({
    ...event,
    visible: map[event.id] === true
  }));
}

function publicEvent(event) {
  const copy = { ...event };
  delete copy.visible;
  return copy;
}

async function currentMap() {
  const remote = await readRemote();
  if (remote) {
    memory = { ...remote.map };
    return { map: { ...remote.map }, sha: remote.sha, remote: true };
  }
  return { map: readMap(), sha: null, remote: false };
}

async function listAll() {
  const { map } = await currentMap();
  return decorate(map);
}

async function listPublic() {
  const events = await listAll();
  const local = events.filter((event) => event.past || event.visible).map(publicEvent);
  const fromRubric = await rubric.upcoming();
  const rubricTitles = new Set(fromRubric.events.map((event) => event.title.toLowerCase()));
  const upcoming = [
    ...fromRubric.events,
    ...local.filter((event) => !event.past && !rubricTitles.has(event.title.toLowerCase()))
  ].sort((left, right) => String(left.datetime).localeCompare(String(right.datetime)) || left.title.localeCompare(right.title));
  const past = local.filter((event) => event.past);
  return { events: [...upcoming, ...past], rubricOk: fromRubric.ok };
}

async function setVisible(id, visible) {
  if (!known(id)) return null;
  const current = await currentMap();
  const map = { ...current.map };
  if (visible) map[id] = true;
  else delete map[id];
  const local = writeLocal(map);
  const remote = current.remote || token() ? await writeRemote(map, current.sha) : false;
  return {
    persisted: local || remote,
    events: decorate(map)
  };
}

module.exports = {
  listAll,
  listPublic,
  setVisible
};
