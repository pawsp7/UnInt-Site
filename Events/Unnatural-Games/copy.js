/* Unnatural Games — shared poster copy.
   Edit the strings below, save, and reload any poster HTML.

   Before a Saitsa poster submission, set `date` to the booked calendar
   day (for example "Mon Oct 19") and `room` to the SECC room. Approval
   covers one night. "Mondays" is the proposed slot, not a locked series.
   Each repeat needs its own proposal or a repeat-format approval. */
window.GAMES_COPY = {
  date: "Mondays",
  time: "6:00 – 8:00 PM",
  place: "SAIT campus",
  room: "Room TBA",
  type: "Student club",
  typeDetail: "Social game night · live AI demo",
  who: "All SAIT students",
  whoDetail: "Every program · beginners welcome",
  purpose: "One chessboard. One language model. The whole room plays as a single team — debate the move, vote, and hear the model explain itself. A live look at what current AI can do, and where beginners can still out-plan it.",
  cost: "Free · on campus · no alcohol",
  stakes: "Bragging rights only. No prizes.",
  stakesWin: "Smarter than ChatGPT",
  stakesLose: "Homework",
  email: "unnaturalintelligencesait@gmail.com",
  discord: "discord.gg/hcsQFRNUEa",
  discordUrl: "https://discord.gg/hcsQFRNUEa",
  url: "unnaturalintelligence.club",
  pillar: "Build pillar",
  welcome: "Welcome, sign-ups, and the rules of the vote.",
  match: "Argue, vote, then hear the model explain its move.",
  debrief: "What it did well, where it collapsed, what’s next."
};

(function applyGamesCopy() {
  const copy = window.GAMES_COPY;
  document.querySelectorAll("[data-field]").forEach((el) => {
    const value = copy[el.dataset.field];
    if (value != null) el.textContent = value;
  });
})();
