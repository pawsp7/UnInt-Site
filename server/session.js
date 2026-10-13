const crypto = require("crypto");

const COOKIE = "ui_desk";
const WEEK = 7 * 24 * 60 * 60 * 1000;

function password() {
  return process.env.ADMIN_PASSWORD || "";
}

function signingKey() {
  return crypto
    .createHash("sha256")
    .update(`unnatural-desk:${password()}:${process.env.ADMIN_SECRET || "club"}`)
    .digest();
}

function safeEqual(a, b) {
  const left = crypto.createHash("sha256").update(String(a)).digest();
  const right = crypto.createHash("sha256").update(String(b)).digest();
  return crypto.timingSafeEqual(left, right);
}

function readBody(req) {
  if (req.body && typeof req.body === "object") {
    return Promise.resolve(req.body);
  }
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf8");
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

function issueToken() {
  const body = Buffer.from(JSON.stringify({ exp: Date.now() + WEEK })).toString("base64url");
  const sig = crypto.createHmac("sha256", signingKey()).update(body).digest("base64url");
  return `${body}.${sig}`;
}

function tokenFromRequest(req) {
  const header = req.headers.cookie || "";
  const parts = header.split(";").map((part) => part.trim());
  const row = parts.find((part) => part.startsWith(`${COOKIE}=`));
  return row ? decodeURIComponent(row.slice(COOKIE.length + 1)) : "";
}

function verifyToken(token) {
  if (!password() || !token || !token.includes(".")) return false;
  const [body, sig] = token.split(".");
  const expected = crypto.createHmac("sha256", signingKey()).update(body).digest("base64url");
  const left = Buffer.from(sig);
  const right = Buffer.from(expected);
  if (left.length !== right.length || !crypto.timingSafeEqual(left, right)) return false;
  try {
    const payload = JSON.parse(Buffer.from(body, "base64url").toString("utf8"));
    return typeof payload.exp === "number" && payload.exp > Date.now();
  } catch (error) {
    return false;
  }
}

function cookie(token, req) {
  const proto = String(req.headers["x-forwarded-proto"] || "").split(",")[0].trim();
  const secure = proto === "https" ? "; Secure" : "";
  const value = token ? `${COOKIE}=${encodeURIComponent(token)}` : `${COOKIE}=`;
  const maxAge = token ? 60 * 60 * 24 * 7 : 0;
  return `${value}; HttpOnly; Path=/; SameSite=Lax; Max-Age=${maxAge}${secure}`;
}

function send(res, status, payload) {
  const body = JSON.stringify(payload);
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(body);
}

module.exports = {
  password,
  safeEqual,
  readBody,
  issueToken,
  tokenFromRequest,
  verifyToken,
  cookie,
  send
};
