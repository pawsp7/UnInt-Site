const session = require("../server/session");
const content = require("../server/desk-content");
const store = require("../server/event-store");
const log = require("../server/desk-log");

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
  const thread = await log.list();
  session.send(res, 200, { sections: content.sections, events, messages: thread.messages });
};
