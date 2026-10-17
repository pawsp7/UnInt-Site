import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const root = join(fileURLToPath(new URL(".", import.meta.url)), "..", "docs");
const login = require("../api/login.js");
const logout = require("../api/logout.js");
const desk = require("../api/desk.js");
const events = require("../api/events.js");
const club = require("../api/club.js");
const log = require("../api/log.js");

const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".ttf": "font/ttf",
  ".txt": "text/plain; charset=utf-8"
};

function fileFor(urlPath) {
  const clean = decodeURIComponent(urlPath.split("?")[0]).replace(/^\/+/, "");
  if (clean.split("/").includes("..")) return null;
  let target = join(root, clean);
  if (existsSync(target) && statSync(target).isDirectory()) {
    target = join(target, "index.html");
  }
  if (!existsSync(target)) return null;
  return target;
}

const port = Number(process.env.PORT || 4173);
const server = createServer((req, res) => {
  const path = (req.url || "/").split("?")[0];
  if (path === "/api/login") return login(req, res);
  if (path === "/api/logout") return logout(req, res);
  if (path === "/api/desk") return desk(req, res);
  if (path === "/api/events") return events(req, res);
  if (path === "/api/club") return club(req, res);
  if (path === "/api/log") return log(req, res);

  const file = fileFor(path);
  if (!file) {
    const missing = join(root, "404.html");
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    createReadStream(missing).pipe(res);
    return;
  }
  res.statusCode = 200;
  res.setHeader("Content-Type", types[extname(file)] || "application/octet-stream");
  createReadStream(file).pipe(res);
});

server.listen(port, () => {
  console.log(`Club site at http://127.0.0.1:${port}`);
});
