const session = require("../server/session");
const content = require("../server/desk-content");
const store = require("../server/event-store");

module.exports = async function handler(req, res) {
  if (req.method !== "GET") {
    session.send(res, 405, { error: "Use GET." });
    return;
  }
  if (!session.verifyToken(session.tokenFromRequest(req))) {
    session.send(res, 401, { error: "Sign in again." });
    return;
  }
  const events = await store.listAll();
  session.send(res, 200, { sections: content.sections, events });
};
