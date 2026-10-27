import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const out = join(root, "docs");

const pages = [
  {
    file: "home.html",
    dest: "index.html",
    page: "home",
    title: "Unnatural Intelligence — SAITSA Student Club",
    description: "A SAITSA student club exploring AI beyond the ordinary. Events, workshops, a podcast, and an open room for every SAIT program."
  },
  {
    file: "events.html",
    dest: "events/index.html",
    page: "events",
    title: "Events — Unnatural Intelligence",
    description: "Workshops, labs, and campus nights from the club Rubric page. Earlier nights stay listed."
  },
  {
    file: "media.html",
    dest: "media/index.html",
    page: "media",
    title: "Media — Unnatural Intelligence",
    description: "Pictures and posters from nights that already ran, and the talks still being cut."
  },
  {
    file: "podcast.html",
    dest: "podcast/index.html",
    page: "podcast",
    title: "Podcast — Unnatural Intelligence",
    description: "Season 1 of I hate it but it’s so useful. Three episodes in production, with the posters."
  },
  {
    file: "team.html",
    dest: "team/index.html",
    page: "team",
    title: "Team — Unnatural Intelligence",
    description: "The 2026–27 exec team, with names, roles, and photos from the club Rubric page."
  },
  {
    file: "shop.html",
    dest: "shop/index.html",
    page: "shop",
    title: "Shop — Unnatural Intelligence",
    description: "Club stickers and lanyards. Checkout is on the Rubric page."
  },
  {
    file: "connect.html",
    dest: "connect/index.html",
    page: "connect",
    title: "Connect — Unnatural Intelligence",
    description: "Join on Rubric, Discord, Instagram, and the club email. Open to all SAIT students."
  },
  {
    file: "about.html",
    dest: "about/index.html",
    page: "about",
    title: "About — Unnatural Intelligence",
    description: "Mission, who the club is for, and how AI use on campus actually works."
  },
  {
    file: "admin.html",
    dest: "admin/index.html",
    page: "admin",
    title: "Exec desk — Unnatural Intelligence",
    description: "Private exec sign-in.",
    robots: "noindex, nofollow",
    scripts: ["/js/admin.js"]
  },
  {
    file: "desk.html",
    dest: "admin/desk/index.html",
    page: "admin",
    title: "Exec desk — Unnatural Intelligence",
    description: "Private exec links.",
    robots: "noindex, nofollow",
    scripts: ["/js/admin.js"]
  },
  {
    file: "404.html",
    dest: "404.html",
    page: "home",
    title: "Page not found — Unnatural Intelligence",
    description: "That address is not on the club site.",
    robots: "noindex"
  }
];

const nav = [
  ["events", "Events", "/events/"],
  ["media", "Media", "/media/"],
  ["podcast", "Podcast", "/podcast/"],
  ["team", "Team", "/team/"],
  ["shop", "Shop", "/shop/"],
  ["connect", "Connect", "/connect/"]
];

function layout(page) {
  const body = readFileSync(join(root, "site/content", page.file), "utf8");
  const links = nav
    .map(([id, label, href]) => {
      const current = page.page === id ? ' aria-current="page"' : "";
      return `<a href="${href}"${current}>${label}</a>`;
    })
    .join("");
  const aboutCurrent = page.page === "about" ? ' aria-current="page"' : "";
  const robots = page.robots ? `\n<meta name="robots" content="${page.robots}">` : "";
  const extraScripts = (page.scripts || []).map((src) => `<script src="${src}" defer></script>`).join("");
  const jsonLd = page.page === "home" ? `<script type="application/ld+json">${JSON.stringify({
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Unnatural Intelligence",
    url: "https://unnaturalintelligence.club",
    email: "unnaturalintelligencesait@gmail.com",
    description: "A Saitsa student club at SAIT for learning and integrating AI, open to every program.",
    sameAs: [
      "https://instagram.com/unnaturalintelligence",
      "https://campus.hellorubric.com/?s=16226"
    ]
  })}</script>` : "";

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${page.title}</title>
<meta name="description" content="${page.description}">${robots}
<meta property="og:title" content="${page.title}">
<meta property="og:description" content="${page.description}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://unnaturalintelligence.club">
<meta property="og:image" content="https://unnaturalintelligence.club/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/site.css">
${jsonLd}
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">
      <img src="/assets/mark.svg" alt="">
      <span class="brand-name">Unnatural<span>Intelligence</span></span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="nav" id="site-nav">
      ${links}
      <a href="/about/"${aboutCurrent}>About</a>
    </nav>
    <div class="header-actions">
      <a class="btn btn-lime btn-small" href="/connect/#join">Join us</a>
    </div>
  </div>
</header>
<main id="content">
${body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div>
      <img class="saitsa" src="/assets/saitsa.svg" alt="Saitsa Student Clubs">
      <p>Unnatural Intelligence is a Saitsa student club at SAIT. Generated by AI · perfected by humans.</p>
    </div>
    <div>
      <h2>On this site</h2>
      <ul>
        <li><a href="/events/">Events</a></li>
        <li><a href="/media/">Media</a></li>
        <li><a href="/podcast/">Podcast</a></li>
        <li><a href="/team/">Team</a></li>
        <li><a href="/shop/">Shop</a></li>
        <li><a href="/connect/">Connect</a></li>
        <li><a href="/about/">About</a></li>
      </ul>
    </div>
    <div>
      <h2>Off this site</h2>
      <ul>
        <li><a class="with-icon" href="https://campus.hellorubric.com/?s=16226"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3.5" y="7" width="17" height="10" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M9.5 7v10" stroke="#FA4A9E" stroke-width="1.8" stroke-dasharray="1.6 2"/><circle cx="6.5" cy="12" r="1" fill="currentColor"/></svg>Join on Rubric</a></li>
        <li><a class="with-icon" href="https://instagram.com/unnaturalintelligence"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="5" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="3.6" stroke="currentColor" stroke-width="1.8"/><circle cx="17.1" cy="6.9" r="1" fill="#FA4A9E"/></svg>Instagram</a></li>
        <li><a class="with-icon" href="https://discord.gg/hcsQFRNUEa"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12.5a7 7 0 0 1 14 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><rect x="3.4" y="12" width="3.6" height="6.2" rx="1.5" stroke="currentColor" stroke-width="1.8"/><rect x="17" y="12" width="3.6" height="6.2" rx="1.5" stroke="currentColor" stroke-width="1.8"/><path d="M17.2 18.4c0 1.5-1.5 2.6-3.3 2.6H12" stroke="#FA4A9E" stroke-width="1.8" stroke-linecap="round"/></svg>Discord</a></li>
        <li><a class="with-icon" href="mailto:unnaturalintelligencesait@gmail.com"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3.5" y="5.5" width="17" height="13" rx="2.5" stroke="currentColor" stroke-width="1.8"/><path d="M4.5 7.5 12 13l7.5-5.5" stroke="#FA4A9E" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>Email the execs</a></li>
        <li><a href="/admin/">Exec desk</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap colophon">
    <span>© 2026 Unnatural Intelligence</span>
    <span>unnaturalintelligence.club</span>
  </div>
</footer>
<script src="/js/site.js" defer></script>
<script src="/js/events.js" defer></script>
${extraScripts}
</body>
</html>
`;
}

rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

for (const page of pages) {
  const dest = join(out, page.dest);
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, layout(page));
}

const assetDir = join(out, "assets");
mkdirSync(assetDir, { recursive: true });
const copies = [
  ["Branding/Vector Kit/marks/favicon.svg", "favicon.svg"],
  ["Branding/Vector Kit/marks/jellyfish-mini-gradient.svg", "assets/mark.svg"],
  ["Branding/Vector Kit/marks/jellyfish-gradient.svg", "assets/jellyfish.svg"],
  ["Branding/Jelly/jelly-wink.svg", "assets/jelly-wink.svg"],
  ["Branding/Jelly/jelly-happy.svg", "assets/jelly-happy.svg"],
  ["Branding/Jelly/jelly-party.svg", "assets/jelly-party.svg"],
  ["Branding/Jelly/jelly-side-eye.svg", "assets/jelly-side-eye.svg"],
  ["Branding/Jelly/jelly-glitch.svg", "assets/jelly-glitch.svg"],
  ["Branding/Jelly/jelly-sparkle.svg", "assets/jelly-sparkle.svg"],
  ["Branding/Jelly/jelly-hearts.svg", "assets/jelly-hearts.svg"],
  ["Branding/Jelly/jelly-tunes.svg", "assets/jelly-tunes.svg"],
  ["Branding/Jelly/jelly-whoa.svg", "assets/jelly-whoa.svg"],
  ["Branding/Vector Kit/icons/spark-plain.svg", "assets/spark-plain.svg"],
  ["Branding/Vector Kit/icons/workflow-plain.svg", "assets/workflow-plain.svg"],
  ["Branding/Vector Kit/icons/mask-plain.svg", "assets/mask-plain.svg"],
  ["Branding/Vector Kit/icons/halt-plain.svg", "assets/halt-plain.svg"],
  ["Branding/Vector Kit/icons/prompt-plain.svg", "assets/prompt-plain.svg"],
  ["Branding/Vector Kit/patterns/tentacle-flourish.svg", "assets/flourish.svg"],
  ["charter/assets/revamp/header-squiggle.svg", "assets/header-squiggle.svg"],
  ["Events/Podcast/assets/audio-bars.svg", "assets/audio-bars.svg"],
  ["Events/Podcast/Podcast Poster E01 I Hate It (11x17).png", "assets/podcast/e01.png"],
  ["Events/Podcast/Podcast Poster E02 So Useful (11x17).png", "assets/podcast/e02.png"],
  ["Events/Podcast/Podcast Poster E03 Human Finish (11x17).png", "assets/podcast/e03.png"],
  ["Branding/SaitsaStudentClubsPrimaryLogo.svg", "assets/saitsa.svg"],
  ["Branding/Vector Kit/png/social/og-1200x630.png", "assets/og.png"]
];
for (const [from, to] of copies) {
  const dest = join(out, to);
  mkdirSync(dirname(dest), { recursive: true });
  cpSync(join(root, from), dest);
}
cpSync(join(root, "site/assets/events"), join(out, "assets/events"), { recursive: true });
cpSync(join(root, "site/css"), join(out, "css"), { recursive: true });
cpSync(join(root, "site/js"), join(out, "js"), { recursive: true });

const fontDir = join(out, "fonts");
mkdirSync(fontDir, { recursive: true });
for (const font of [
  "Inter-Regular.ttf",
  "Inter-Medium.ttf",
  "Inter-SemiBold.ttf",
  "Inter-Bold.ttf",
  "InterDisplay-Bold.ttf",
  "JetBrainsMono-Regular.ttf",
  "JetBrainsMono-Bold.ttf",
  "LICENSE.txt"
]) {
  cpSync(join(root, "charter/fonts", font), join(fontDir, font));
}

writeFileSync(join(out, ".nojekyll"), "");

const expo = spawnSync("bash", [join(root, "scripts/build-clubs-expo-site.sh"), join(out, "expo")], {
  stdio: "inherit"
});
if (expo.status !== 0) {
  process.exit(expo.status || 1);
}

console.log("Wrote club site to docs/");
