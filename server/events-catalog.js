/** Club nights. `visible` is not stored here.
 *  An upcoming night stays off the public site until an exec checks it.
 *  A past night stays on the Events page.
 */
module.exports = [
  {
    id: "fall-showcase",
    title: "Clubs Fall Showcase",
    whenLabel: "13–14 Oct 2026",
    whenDetail: "11:00–2:00",
    datetime: "2026-10-13",
    where: "Stan Grad Atrium · setup from 10:30 both days",
    summary: "Saitsa’s fall clubs expo. Our table is the easiest place to meet the execs, hear what the semester actually looks like, and join. Bring a friend from another program.",
    status: "Confirmed",
    tone: "lime",
    past: false,
    ticket: {
      kicker: "Showcase",
      big: "13–14<br>Oct",
      time: "11:00–2:00",
      place: "Confirmed · Stan Grad Atrium",
      blurb: "Two days at the Saitsa clubs expo. Come say hello, try a one-minute demo, and join if the room feels like yours. Open to every SAIT student.",
      chips: ["Free", "All programs", "No experience needed"]
    }
  },
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
    whenLabel: "Mondays · proposed",
    whenDetail: "6:00–8:00 PM",
    datetime: "",
    where: "SAIT campus · room TBA",
    summary: "One chessboard. One language model. The room plays as a single team: debate the move, vote, then hear the model explain itself. Bragging rights only. Free, on campus, no alcohol. Each night needs its own approval, so “Mondays” is the slot we are asking for, not a locked series.",
    status: "Proposed",
    tone: "ghost",
    past: false,
    ticket: {
      kicker: "Game night",
      big: "Mon<br>6–8",
      time: "Proposed",
      place: "Proposed · room TBA",
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
