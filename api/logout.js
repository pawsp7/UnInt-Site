const session = require("../server/session");

module.exports = function handler(req, res) {
  if (req.method !== "POST") {
    session.send(res, 405, { error: "Use POST." });
    return;
  }
  res.setHeader("Set-Cookie", session.cookie("", req));
  session.send(res, 200, { ok: true });
};
