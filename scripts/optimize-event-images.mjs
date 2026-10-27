#!/usr/bin/env node
import { readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { isImage, optimizeImage } from "./event-media.mjs";

const here = fileURLToPath(new URL(".", import.meta.url));
const root = join(here, "..");

export function optimizeEventTree(base = root) {
  const eventsDir = join(base, "site/events");
  const results = [];
  for (const entry of readdirSync(eventsDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const dir = join(eventsDir, entry.name);
    const poster = join(dir, findPoster(dir));
    if (findPoster(dir)) {
      results.push({ event: entry.name, file: relative(base, poster), ...optimizeImage(poster, poster, { kind: "poster" }) });
    }
    for (const sub of ["recap", "posters"]) {
      const folder = join(dir, sub);
      let names = [];
      try {
        names = readdirSync(folder);
      } catch (error) {
        continue;
      }
      for (const name of names) {
        if (!isImage(name)) continue;
        const full = join(folder, name);
        try {
          if (!statSync(full).isFile()) continue;
        } catch (error) {
          continue;
        }
        const kind = sub === "recap" ? "photo" : "poster";
        results.push({ event: entry.name, file: relative(base, full), ...optimizeImage(full, full, { kind }) });
      }
    }
  }
  return results;
}

function findPoster(dir) {
  for (const name of ["poster.png", "poster.jpg", "poster.jpeg", "poster.webp"]) {
    try {
      if (statSync(join(dir, name)).isFile()) return name;
    } catch (error) {
      /* missing */
    }
  }
  return "";
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const results = optimizeEventTree(root);
  const changed = results.filter((item) => !item.skipped);
  console.log(`Checked ${results.length} event images. Wrote ${changed.length} web-sized copies.`);
  for (const item of changed) {
    console.log(`  ${item.file} → ${item.width}×${item.height}`);
  }
}
