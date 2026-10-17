const session = require("../server/session");
const log = require("../server/desk-log");

const posts = new Map();

function clientIp(req) {
  return String(req.headers["x-forwarded-for"] || req.socket?.remoteAddress || "local").split(",")[0].trim();
}

function rateLimited(ip) {
  const now = Date.now();
  const windowMs = 10 * 60 * 1000;
  const recent = (posts.get(ip) || []).filter((stamp) => now - stamp < windowMs);
  if (recent.length >= 30) {
    posts.set(ip, recent);
    return true;
  }
  recent.push(now);
  posts.set(ip, recent);
  return false;
}

module.exports = async function handler(req, res) {
  if (!session.verifyToken(session.tokenFromRequest(req))) {
    session.send(res, 401, { error: "Sign in again." });
    return;
  }

  if (req.method === "GET") {
    session.send(res, 200, await log.list());
    return;
  }

  if (req.method !== "POST") {
    session.send(res, 405, { error: "Use GET or POST." });
    return;
  }

  if (rateLimited(clientIp(req))) {
    session.send(res, 429, { error: "The log is getting notes too quickly. Wait a few minutes." });
    return;
  }

  const length = Number(req.headers["content-length"] || 0);
  if (length > 8000) {
    session.send(res, 413, { error: "That note is too long." });
    return;
  }

  let body;
  try {
    body = await session.readBody(req);
  } catch (error) {
    session.send(res, 400, { error: "Send a name and a note." });
    return;
  }

  if (body.action === "delete") {
    const result = await log.remove(typeof body.id === "string" ? body.id : "");
    if (result.error) {
      session.send(res, result.status || 400, { error: result.error });
      return;
    }
    session.send(res, 200, result);
    return;
  }

  const result = await log.append(body.name, body.text);
  if (result.error) {
    session.send(res, 400, { error: result.error });
    return;
  }
  session.send(res, 200, result);
};
