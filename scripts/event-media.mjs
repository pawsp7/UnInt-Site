import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readdirSync, readFileSync, renameSync, statSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, extname, join } from "node:path";

export const IMAGE_EXT = new Set([".jpg", ".jpeg", ".png", ".webp"]);
export const PHOTO_MAX = 1600;
export const POSTER_MAX = 1400;
export const JPEG_QUALITY = 5;

export function isImage(name) {
  return IMAGE_EXT.has(extname(name).toLowerCase());
}

export function walkImages(dir) {
  const found = [];
  let entries = [];
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch (error) {
    return found;
  }
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) found.push(...walkImages(full));
    else if (entry.isFile() && isImage(entry.name) && !entry.name.startsWith(".")) found.push(full);
  }
  return found;
}

export function imageSize(file) {
  const buf = readFileSync(file);
  if (buf.length >= 24 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47) {
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
  }
  if (buf.length > 4 && buf[0] === 0xff && buf[1] === 0xd8) {
    let offset = 2;
    while (offset + 9 < buf.length) {
      if (buf[offset] !== 0xff) break;
      const marker = buf[offset + 1];
      if (marker === 0xd9 || marker === 0xda) break;
      const length = buf.readUInt16BE(offset + 2);
      if ((marker >= 0xc0 && marker <= 0xc3) || (marker >= 0xc5 && marker <= 0xc7) || (marker >= 0xc9 && marker <= 0xcb)) {
        return { height: buf.readUInt16BE(offset + 5), width: buf.readUInt16BE(offset + 7) };
      }
      offset += 2 + length;
    }
  }
  if (buf.length > 30 && buf[0] === 0x52 && buf[8] === 0x57 && buf[12] === 0x56 && buf[15] === 0x50) {
    const vp8 = buf.slice(12, 16).toString("ascii");
    if (vp8 === "VP8 ") {
      return { width: buf.readUInt16LE(26) & 0x3fff, height: buf.readUInt16LE(28) & 0x3fff };
    }
  }
  return { width: 0, height: 0 };
}

function ffmpegAvailable() {
  const result = spawnSync("ffmpeg", ["-version"], { encoding: "utf8" });
  return result.status === 0;
}

function scaleFilter(maxEdge) {
  return `scale=w='if(gt(max(iw\\,ih)\\,${maxEdge}),if(gte(iw\\,ih),${maxEdge}\\,-2),iw)':h='if(gt(max(iw\\,ih)\\,${maxEdge}),if(gt(ih\\,iw),${maxEdge}\\,-2),ih)'`;
}

export function optimizeImage(src, dest, options = {}) {
  if (!src || !existsSync(src) || !statSync(src).isFile()) {
    return { dest, width: 0, height: 0, skipped: true, reason: "missing" };
  }
  const ext = extname(src).toLowerCase();
  const isPoster = options.kind === "poster" || ext === ".png";
  const maxEdge = options.maxEdge || (isPoster ? POSTER_MAX : PHOTO_MAX);
  const size = imageSize(src);
  const bytes = statSync(src).size;
  const alreadyFits = size.width && size.height && Math.max(size.width, size.height) <= maxEdge && bytes <= (isPoster ? 450000 : 280000);

  mkdirSync(dirname(dest), { recursive: true });

  if (alreadyFits && src !== dest) {
    copyFileSync(src, dest);
    return { dest, width: size.width, height: size.height, skipped: true };
  }
  if (alreadyFits) {
    return { dest, width: size.width, height: size.height, skipped: true };
  }
  if (!ffmpegAvailable()) {
    if (src !== dest) copyFileSync(src, dest);
    return { dest, width: size.width, height: size.height, skipped: true, reason: "no-ffmpeg" };
  }

  const tmp = dest + ".tmp" + ext;
  const args = ["-y", "-i", src, "-vf", scaleFilter(maxEdge)];
  if (ext === ".jpg" || ext === ".jpeg") {
    args.push("-q:v", String(options.quality || JPEG_QUALITY), "-pix_fmt", "yuvj420p");
  } else if (ext === ".png") {
    args.push("-compression_level", "9");
  } else if (ext === ".webp") {
    args.push("-quality", "80");
  }
  args.push(tmp);
  const result = spawnSync("ffmpeg", args, { encoding: "utf8" });
  if (result.status !== 0 || !tmpHasFile(tmp)) {
    try { unlinkSync(tmp); } catch (error) { /* ignore */ }
    if (src !== dest) copyFileSync(src, dest);
    return { dest, width: size.width, height: size.height, skipped: true, reason: "ffmpeg-failed" };
  }
  const optimizedBytes = statSync(tmp).size;
  if (optimizedBytes >= bytes && Math.max(size.width, size.height) <= maxEdge + 40) {
    unlinkSync(tmp);
    if (src !== dest) copyFileSync(src, dest);
    return { dest, width: size.width, height: size.height, skipped: true, reason: "no-gain" };
  }
  renameSync(tmp, dest);
  const next = imageSize(dest);
  return { dest, width: next.width || size.width, height: next.height || size.height, skipped: false, bytes: optimizedBytes };
}

function tmpHasFile(file) {
  try {
    return statSync(file).isFile() && statSync(file).size > 32;
  } catch (error) {
    return false;
  }
}

export function writeJson(file, value) {
  mkdirSync(join(file, ".."), { recursive: true });
  writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}
