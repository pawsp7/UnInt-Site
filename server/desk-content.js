/** Exec-only links and notes. Returned by /api/desk after a valid session.
 *  Nothing here should be a bank number, receipt image, or personal phone.
 */
module.exports = {
  sections: [
    {
      kicker: "Rubric",
      title: "Portal and the club card",
      links: [
        {
          label: "Rubric club page",
          href: "https://campus.hellorubric.com/?s=16226",
          note: "Society 16226. Public membership card, news, and tickets. This is the link on the website."
        },
        {
          label: "Saitsa Clubs Portal",
          href: "https://portal.hellorubric.com",
          note: "File event proposals and exec paperwork. Unapproved events are uninsured."
        },
        {
          label: "Poster submission",
          href: "https://saitsa.com/Poster-Submission",
          note: "Tabloid 11×17, unaltered Saitsa Clubs logo, Saitsa boards only. Do not use the official SAIT logo."
        },
        {
          label: "SECC / clubs office",
          href: "mailto:saitsa.clubs@edu.sait.ca",
          note: "saitsa.clubs@edu.sait.ca — rooms, exec changes, and questions. The club does not book rooms itself."
        }
      ],
      notes: [
        "Meetings need a proposal at least two weeks ahead.",
        "If an exec changes, the President emails the SECC with the new name, role, and email.",
        "Execs cannot sign agreements in SAIT or Saitsa’s name, and cannot run unsanctioned alcohol events."
      ]
    },
    {
      kicker: "Money",
      title: "Ledger and grants",
      links: [
        {
          label: "Finance ledger (Google Sheet)",
          href: "https://docs.google.com/spreadsheets/d/1Br3Cm09hhayw2eaaRESMIr3UHT9eAlJeRMmqpgHJC_w/edit",
          note: "Companion to Finance/Ledger in the repo. Verify every amount against the receipt before an audit or a grant."
        }
      ],
      notes: [
        "Do not spend grant money before it is approved.",
        "Start-up reimbursement: up to $500 for a new club, $200 if returning. File the receipt within one month.",
        "Term grants can reach $5,000 and are prioritized for events over swag.",
        "Tell the SECC about any external monetary sponsorship. Unused grant funds are reclaimed after close-out.",
        "Clubs Expo candy-git booth was noted at about $120 and already in the running budget (schedule note, 13 Sep 2026)."
      ]
    },
    {
      kicker: "Documents",
      title: "Working files",
      links: [
        {
          label: "Club Google Doc",
          href: "https://docs.google.com/document/d/1p7wujyxIlXlJI_kkdtouZMRiO4umiaZbLAk66ExrO3Y/edit",
          note: "Original working document linked from the repo README."
        },
        {
          label: "GitHub repo",
          href: "https://github.com/pawsp7/Unnatural-Intelligence",
          note: "Charter, posters, vector kit, and the finance folder. The public site is built from site/ into docs/."
        },
        {
          label: "Expo table kit",
          href: "/expo/",
          note: "Staff page for the Clubs Expo booth (candy-git). Not linked from the public navigation."
        },
        {
          label: "Internal schedule",
          href: "https://cochon123.github.io/club-schedule/",
          note: "Includes exec-only meetings. The public Events page is a curated subset."
        }
      ]
    },
    {
      kicker: "Calendar",
      title: "Notes that stay off the homepage",
      notes: [
        "Tue 15 Sep 2026, 11:00, CA121 — Clubs Orientation. A signing exec had to be there for grants eligibility.",
        "Fri 18 Sep 2026, 16:00–19:00, Heritage Hall AA128 — Halt & Restart. SECC-approved. Pierre and Daniil as the models.",
        "Wed 23 Sep 2026, 14:00–15:00, E130C — Meeting: AI & Humans in Media. Damien, Hailey, Pierre, Logan.",
        "Thu 1 Oct 2026 was the date on the AI Agents proposal (MB202, 6–8pm, still marked proposed). The live schedule instead lists Atelier: AI Agents for 28 Oct with no room. Reconcile those before promoting a day.",
        "13–14 Oct 2026, Stan Grad Atrium — Fall Showcase. Public. Setup 10:30, event 11:00–14:00, takedown 14:00–14:30, both days.",
        "Sat 14 Nov 2026 — One-Day AI Game Jam with Game Development Club. Proposal only.",
        "Unnatural Games: proposed Mondays 6–8pm. Not a locked weekly series until each night (or a repeat format) is approved.",
        "Saitsa year markers: 13 Jan 2027 orientation, 27–28 Jan 2027 winter showcase, 11 Mar 2027 clubs council, 11 Apr 2027 reports and transition docs, 30 Jun 2027 fiscal year end."
      ]
    },
    {
      kicker: "Roster",
      title: "How the names are filed",
      notes: [
        "Public site: Hailey (President), Pierre (Vice President), Alexander / Alex (VP Finance), Logan (Media), Deema (Social, he/him).",
        "Proposal paperwork names Pierre Tchio as Vice President and primary event organizer, and Hailey as President (some drafts spell Haely).",
        "Name tags also list Daniil with type AI. Engraved plates omit Daniil. Keep Daniil off the public exec row unless the team decides otherwise.",
        "Three signing authorities must stay filled: President, VP Operations, VP Finance. One person, one executive title. Current SAIT students in good standing who have paid the Saitsa fee, only."
      ]
    },
    {
      kicker: "Channels",
      title: "Inboxes and invites",
      links: [
        {
          label: "Club email",
          href: "mailto:unnaturalintelligencesait@gmail.com",
          note: "unnaturalintelligencesait@gmail.com — the only address on the public site."
        },
        {
          label: "Discord invite on most posters",
          href: "https://discord.gg/hcsQFRNUEa",
          note: "Printed on the AI Agents posters and Unnatural Games. This is the public website link."
        },
        {
          label: "Discord invite on the podcast posters",
          href: "https://discord.gg/nYeCuXGa47",
          note: "Different code. Confirm which server is current before the next print run."
        },
        {
          label: "Instagram",
          href: "https://instagram.com/unnaturalintelligence",
          note: "@unnaturalintelligence"
        }
      ]
    }
  ]
};
