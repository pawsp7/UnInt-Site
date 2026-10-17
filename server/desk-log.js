const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const FILE = path.join(__dirname, "data", "desk-log.json");
const TMP_FILE = "/tmp/unnatural-desk-log.json";
const GITHUB_PATH = "server/data/desk-log.json";
const MAX_MESSAGES = 200;
const MAX_NAME = 40;
const MAX_TEXT = 1000;

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

function asMessages(value) {
  const list = Array.isArray(value) ? value : value && Array.isArray(value.messages) ? value.messages : null;
  if (!list) return [];
  return list
    .filter((item) => item && typeof item.id === "string" && typeof item.text === "string")
    .map((item) => ({
      id: item.id,
      name: typeof item.name === "string" ? item.name : "Exec",
      text: item.text,
      at: typeof item.at === "string" ? item.at : ""
    }))
    .slice(-MAX_MESSAGES);
}

function readJsonFile(file) {
  try {
    return asMessages(JSON.parse(fs.readFileSync(file, "utf8")));
  } catch (error) {
    return null;
  }
}

function readLocal() {
  if (memory) return memory.map((item) => ({ ...item }));
  memory = readJsonFile(TMP_FILE) || readJsonFile(FILE) || [];
  return memory.map((item) => ({ ...item }));
}

function writeLocal(messages) {
  const text = `${JSON.stringify({ messages }, null, 2)}\n`;
  memory = messages.map((item) => ({ ...item }));
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
    if (response.status === 404) return { messages: [], sha: null };
    if (!response.ok) return null;
    const data = await response.json();
    const parsed = JSON.parse(Buffer.from(data.content, "base64").toString("utf8"));
    return { messages: asMessages(parsed), sha: data.sha };
  } catch (error) {
    return null;
  }
}

async function writeRemote(messages, sha) {
  const auth = token();
  if (!auth) return false;
  const url = `https://api.github.com/repos/${repo()}/contents/${GITHUB_PATH}`;
  const body = {
    message: "Update the exec desk log",
    content: Buffer.from(`${JSON.stringify({ messages }, null, 2)}\n`).toString("base64"),
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

async function load() {
  const remote = await readRemote();
  if (remote) {
    memory = remote.messages.map((item) => ({ ...item }));
    return { messages: remote.messages.map((item) => ({ ...item })), sha: remote.sha };
  }
  return { messages: readLocal(), sha: null };
}

function publicMessages(messages) {
  return messages.map((item) => ({
    id: item.id,
    name: item.name,
    text: item.text,
    at: item.at
  }));
}

function cleanName(value) {
  const name = String(value || "")
    .replace(/[\u0000-\u001F\u007F]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!name) return "";
  return name.slice(0, MAX_NAME);
}

function cleanText(value) {
  const text = String(value || "")
    .replace(/\r\n/g, "\n")
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "")
    .trim();
  if (!text) return { error: "Write a note for the log." };
  if (text.length > MAX_TEXT) return { error: "Keep the note under 1000 characters." };
  return { text };
}

async function persist(messages, sha) {
  const local = writeLocal(messages);
  if (!token()) return local;
  const remote = await writeRemote(messages, sha);
  return local || remote;
}

async function list() {
  const current = await load();
  return { messages: publicMessages(current.messages) };
}

async function append(name, text) {
  const person = cleanName(name);
  if (!person) return { error: "Add your name so the log shows who wrote it." };
  const note = cleanText(text);
  if (note.error) return note;
  const entry = {
    id: `log-${crypto.randomBytes(4).toString("hex")}`,
    name: person,
    text: note.text,
    at: new Date().toISOString()
  };
  let persisted = false;
  let messages = [];
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const current = await load();
    messages = current.messages.some((item) => item.id === entry.id)
      ? current.messages
      : [...current.messages, entry].slice(-MAX_MESSAGES);
    persisted = await persist(messages, current.sha);
    if (persisted || !token()) break;
  }
  return { persisted, message: publicMessages([entry])[0], messages: publicMessages(messages) };
}

async function remove(id) {
  if (!/^log-[a-f0-9]{8}$/.test(id)) return { error: "That note is not in the log.", status: 404 };
  let persisted = false;
  let messages = [];
  let found = false;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const current = await load();
    found = current.messages.some((item) => item.id === id);
    if (!found) return { error: "That note is not in the log.", status: 404 };
    messages = current.messages.filter((item) => item.id !== id);
    persisted = await persist(messages, current.sha);
    if (persisted || !token()) break;
  }
  return { persisted, messages: publicMessages(messages) };
}

module.exports = {
  list,
  append,
  remove
};
