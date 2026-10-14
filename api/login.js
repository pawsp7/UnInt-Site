const session = require("../server/session");

const attempts = new Map();

function rateLimited(ip) {
  const now = Date.now();
  const windowMs = 10 * 60 * 1000;
  const recent = (attempts.get(ip) || []).filter((stamp) => now - stamp < windowMs);
  if (recent.length >= 8) {
    attempts.set(ip, recent);
    return true;
  }
  recent.push(now);
  attempts.set(ip, recent);
  return false;
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    session.send(res, 405, { error: "Use POST." });
    return;
  }
  const ip = String(req.headers["x-forwarded-for"] || req.socket?.remoteAddress || "local").split(",")[0].trim();
  if (rateLimited(ip)) {
    session.send(res, 429, { error: "Too many tries. Wait a few minutes." });
    return;
  }
  if (!session.password()) {
    session.send(res, 503, { error: "The desk password is not configured on this host yet." });
    return;
  }
  let body;
  try {
    body = await session.readBody(req);
  } catch (error) {
    session.send(res, 400, { error: "Send a password." });
    return;
  }
  if (!session.safeEqual(body.password || "", session.password())) {
    session.send(res, 401, { error: "That password did not open the desk." });
    return;
  }
  res.setHeader("Set-Cookie", session.cookie(session.issueToken(), req));
  session.send(res, 200, { ok: true });
};
