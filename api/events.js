const session = require("../server/session");
const store = require("../server/event-store");

module.exports = async function handler(req, res) {
  if (req.method === "GET") {
    const events = await store.listPublic();
    session.send(res, 200, { events });
    return;
  }

  if (req.method !== "POST") {
    session.send(res, 405, { error: "Use GET or POST." });
    return;
  }

  if (!session.verifyToken(session.tokenFromRequest(req))) {
    session.send(res, 401, { error: "Sign in again." });
    return;
  }

  let body;
  try {
    body = await session.readBody(req);
  } catch (error) {
    session.send(res, 400, { error: "Send an event id." });
    return;
  }

  const id = typeof body.id === "string" ? body.id : "";
  if (!/^[a-z0-9-]{1,40}$/.test(id)) {
    session.send(res, 400, { error: "Unknown event." });
    return;
  }

  const result = await store.setVisible(id, body.visible === true);
  if (!result) {
    session.send(res, 404, { error: "Unknown event." });
    return;
  }

  session.send(res, 200, result);
};
