/** Club nights. `visible` is not stored here.
 *  An upcoming night stays off the public site until an exec checks it.
 *  A past night stays on the Events page.
 */
module.exports = [
  {
    id: "ai-agents",
    title: "Atelier: AI Agents",
    whenLabel: "Late October 2026",
    whenDetail: "Time confirming",
    datetime: "2026-10-28",
    where: "Campus classroom · room still with the SECC",
    summary: "A hands-on workshop on what an AI agent is, how the loop works, and how to use one for a real task — studying, a resume, a project. No prior experience. The booked day and room go up here and on Rubric once the SECC confirms them.",
    status: "Date confirming",
    tone: "cyan",
    past: false,
    ticket: {
      kicker: "Workshop",
      big: "Late<br>Oct",
      time: "Time confirming",
      place: "Date confirming · room with the SECC",
      blurb: "What an agent is, how the loop works, and a hands-on pass at a real task. No prior experience.",
      chips: ["All programs", "No experience needed"]
    }
  },
  {
    id: "unnatural-games",
    title: "Unnatural Games",
    whenLabel: "Mondays",
    whenDetail: "6:00–8:00 PM",
    datetime: "",
    where: "MB224",
    summary: "One chessboard. One language model. The room plays as a single team: debate the move, vote, then hear the model explain itself. Bragging rights only. Free, on campus, no alcohol.",
    status: "Game night",
    tone: "lime",
    past: false,
    ticket: {
      kicker: "Game night",
      big: "Mon<br>6–8",
      time: "6:00–8:00 PM",
      place: "Mondays · MB224",
      blurb: "The room plays one side. The model plays the other. Bragging rights only.",
      chips: ["Free", "No alcohol"]
    }
  },
  {
    id: "game-jam",
    title: "One-Day AI Game Jam",
    whenLabel: "Sat 14 Nov 2026",
    whenDetail: "proposed",
    datetime: "2026-11-14",
    where: "Campus classroom · with Game Development Club",
    summary: "A Saturday build with the Game Development Club: Godot, AI tools in the loop, and a short playtest at the end. Aimed at about 30–50 people. Still a proposal — do not block the day until a confirmed room is posted.",
    status: "Proposed",
    tone: "ghost",
    past: false,
    ticket: {
      kicker: "Jam",
      big: "14<br>Nov",
      time: "Proposed",
      place: "Proposed · with Game Development Club",
      blurb: "A one-day build. Godot, AI in the loop, and a short playtest. Room still to be booked.",
      chips: ["Proposed", "All programs"]
    }
  },
  {
    id: "halt-restart",
    title: "Halt & Restart",
    whenLabel: "18 Sep 2026",
    whenDetail: "4:00–7:00",
    datetime: "2026-09-18",
    where: "Heritage Hall AA128 · SECC-approved",
    summary: "A live prompting lab. Write it tight. If the model drifts, halt and restart. The point was a better result with less context, then a human finish — not a longer chat.",
    status: "Past",
    tone: "ghost",
    past: true,
    ticket: {
      kicker: "Live lab",
      big: "18<br>Sep",
      time: "4:00–7:00",
      place: "Heritage Hall AA128 · SECC-approved",
      blurb: "A live prompting lab. Write it tight. If the model drifts, halt and restart.",
      chips: ["Past", "All students"]
    }
  }
];
