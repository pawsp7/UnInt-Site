const session = require("../server/session");
const store = require("../server/event-store");
const rubric = require("../server/rubric-events");

module.exports = async function handler(req, res) {
  if (req.method !== "GET") {
    session.send(res, 405, { error: "Use GET." });
    return;
  }
  const listed = await store.listPublic();
  const club = await rubric.club();
  session.send(res, 200, {
    rubric: listed.rubricOk,
    events: listed.events,
    team: club.team,
    merchandise: club.merchandise
  });
};
