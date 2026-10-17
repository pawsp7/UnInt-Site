const session = require("../server/session");
const store = require("../server/event-store");

module.exports = async function handler(req, res) {
  if (req.method === "GET") {
    const listed = await store.listPublic();
    session.send(res, 200, { events: listed.events, rubric: listed.rubricOk });
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

  if (body.action === "create") {
    const created = await store.createCustom(body);
    if (created.error) {
      session.send(res, 400, { error: created.error });
      return;
    }
    session.send(res, 200, created);
    return;
  }

  const id = typeof body.id === "string" ? body.id : "";
  if (!/^[a-z0-9-]{1,40}$/.test(id)) {
    session.send(res, 400, { error: "Unknown event." });
    return;
  }

  if (body.action === "delete") {
    const removed = await store.deleteCustom(id);
    if (!removed) {
      session.send(res, 404, { error: "That night is not one the desk created." });
      return;
    }
    session.send(res, 200, removed);
    return;
  }

  const result = await store.setVisible(id, body.visible === true);
  if (!result) {
    session.send(res, 404, { error: "Unknown event." });
    return;
  }

  session.send(res, 200, result);
};
