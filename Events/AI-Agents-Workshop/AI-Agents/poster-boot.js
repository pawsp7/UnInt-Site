const QR = (() => {
  const EXP = new Uint8Array(512), LOG = new Uint8Array(256);
  for (let i = 0, x = 1; i < 255; i++) { EXP[i] = x; LOG[x] = i; x = (x << 1) ^ (x & 0x80 ? 0x11d : 0); }
  for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
  const mul = (a, b) => (a && b) ? EXP[LOG[a] + LOG[b]] : 0;
  function rsGenerator(deg) {
    let g = [1];
    for (let i = 0; i < deg; i++) {
      const ng = new Array(g.length + 1).fill(0);
      for (let j = 0; j < g.length; j++) { ng[j] ^= g[j]; ng[j + 1] ^= mul(g[j], EXP[i]); }
      g = ng;
    }
    return g;
  }
  function rsRemainder(data, gen) {
    const res = new Array(gen.length - 1).fill(0);
    for (const b of data) {
      const f = b ^ res.shift(); res.push(0);
      for (let i = 0; i < res.length; i++) res[i] ^= mul(gen[i + 1], f);
    }
    return res;
  }
  const ECC_PER_BLOCK = [10, 16, 26, 18, 24, 16, 18, 22, 22, 26];
  const NUM_BLOCKS    = [ 1,  1,  1,  2,  2,  4,  4,  4,  5,  5];
  function rawDataModules(ver) {
    let r = (16 * ver + 128) * ver + 64;
    if (ver >= 2) {
      const n = Math.floor(ver / 7) + 2;
      r -= (25 * n - 10) * n - 55;
      if (ver >= 7) r -= 36;
    }
    return r;
  }
  const totalCodewords = ver => Math.floor(rawDataModules(ver) / 8);
  const dataCodewords = ver => totalCodewords(ver) - ECC_PER_BLOCK[ver - 1] * NUM_BLOCKS[ver - 1];
  function alignPositions(ver) {
    if (ver === 1) return [];
    const n = Math.floor(ver / 7) + 2, size = ver * 4 + 17;
    const step = Math.ceil((ver * 4 + 4) / (n * 2 - 2)) * 2;
    const res = [6];
    for (let p = size - 7; res.length < n; p -= step) res.splice(1, 0, p);
    return res;
  }
  function encode(text) {
    const bytes = [...new TextEncoder().encode(text)];
    let ver = 1;
    while (ver <= 10) {
      const countBits = ver < 10 ? 8 : 16;
      if (4 + countBits + bytes.length * 8 <= dataCodewords(ver) * 8) break;
      ver++;
    }
    if (ver > 10) throw new Error("Text too long for this mini QR encoder");
    const countBits = ver < 10 ? 8 : 16;
    const capBits = dataCodewords(ver) * 8;
    const bits = [];
    const push = (val, n) => { for (let i = n - 1; i >= 0; i--) bits.push((val >>> i) & 1); };
    push(4, 4); push(bytes.length, countBits);
    bytes.forEach(b => push(b, 8));
    push(0, Math.min(4, capBits - bits.length));
    while (bits.length % 8) bits.push(0);
    for (let pad = 0xEC; bits.length < capBits; pad ^= 0xEC ^ 0x11) push(pad, 8);
    const data = [];
    for (let i = 0; i < bits.length; i += 8) data.push(parseInt(bits.slice(i, i + 8).join(""), 2));
    const nb = NUM_BLOCKS[ver - 1], ecc = ECC_PER_BLOCK[ver - 1], raw = totalCodewords(ver);
    const shortBlocks = nb - raw % nb, shortLen = Math.floor(raw / nb);
    const gen = rsGenerator(ecc);
    const blocks = [];
    for (let i = 0, k = 0; i < nb; i++) {
      const len = shortLen - ecc + (i < shortBlocks ? 0 : 1);
      const dat = data.slice(k, k + len); k += len;
      const e = rsRemainder(dat, gen);
      if (i < shortBlocks) dat.push(0);
      blocks.push(dat.concat(e));
    }
    const out = [];
    for (let i = 0; i < blocks[0].length; i++)
      blocks.forEach((blk, j) => { if (i !== shortLen - ecc || j >= shortBlocks) out.push(blk[i]); });
    const size = ver * 4 + 17;
    const mod = Array.from({ length: size }, () => new Array(size).fill(false));
    const fn  = Array.from({ length: size }, () => new Array(size).fill(false));
    const set = (x, y, d) => { mod[y][x] = d; fn[y][x] = true; };
    for (let i = 0; i < size; i++) { set(6, i, i % 2 === 0); set(i, 6, i % 2 === 0); }
    const finder = (cx, cy) => {
      for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) {
        const x = cx + dx, y = cy + dy;
        if (x < 0 || y < 0 || x >= size || y >= size) continue;
        const d = Math.max(Math.abs(dx), Math.abs(dy));
        set(x, y, d !== 2 && d !== 4);
      }
    };
    finder(3, 3); finder(size - 4, 3); finder(3, size - 4);
    const ap = alignPositions(ver);
    for (let i = 0; i < ap.length; i++) for (let j = 0; j < ap.length; j++) {
      if ((i === 0 && j === 0) || (i === 0 && j === ap.length - 1) || (i === ap.length - 1 && j === 0)) continue;
      for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++)
        set(ap[i] + dx, ap[j] + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
    }
    function formatBits(mask) {
      const data = (0 << 3) | mask;
      let rem = data;
      for (let i = 0; i < 10; i++) rem = (rem << 1) ^ ((rem >>> 9) * 0x537);
      const b = ((data << 10) | rem) ^ 0x5412;
      const bit = i => ((b >>> i) & 1) === 1;
      for (let i = 0; i <= 5; i++) set(8, i, bit(i));
      set(8, 7, bit(6)); set(8, 8, bit(7)); set(7, 8, bit(8));
      for (let i = 9; i < 15; i++) set(14 - i, 8, bit(i));
      for (let i = 0; i < 8; i++) set(size - 1 - i, 8, bit(i));
      for (let i = 8; i < 15; i++) set(8, size - 15 + i, bit(i));
      set(8, size - 8, true);
    }
    formatBits(0);
    if (ver >= 7) {
      let rem = ver;
      for (let i = 0; i < 12; i++) rem = (rem << 1) ^ ((rem >>> 11) * 0x1F25);
      const b = (ver << 12) | rem;
      for (let i = 0; i < 18; i++) {
        const bit = ((b >>> i) & 1) === 1, a = size - 11 + (i % 3), c = Math.floor(i / 3);
        set(a, c, bit); set(c, a, bit);
      }
    }
    let i = 0;
    for (let right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;
      for (let v = 0; v < size; v++) for (let j = 0; j < 2; j++) {
        const x = right - j, up = ((right + 1) & 2) === 0, y = up ? size - 1 - v : v;
        if (!fn[y][x] && i < out.length * 8) { mod[y][x] = ((out[i >>> 3] >>> (7 - (i & 7))) & 1) === 1; i++; }
      }
    }
    const MASKS = [
      (x, y) => (x + y) % 2 === 0, (x, y) => y % 2 === 0, (x, y) => x % 3 === 0, (x, y) => (x + y) % 3 === 0,
      (x, y) => (Math.floor(x / 3) + Math.floor(y / 2)) % 2 === 0, (x, y) => (x * y) % 2 + (x * y) % 3 === 0,
      (x, y) => ((x * y) % 2 + (x * y) % 3) % 2 === 0, (x, y) => ((x + y) % 2 + (x * y) % 3) % 2 === 0
    ];
    const applyMask = m => { for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) if (!fn[y][x] && MASKS[m](x, y)) mod[y][x] = !mod[y][x]; };
    const penalty = () => {
      let p = 0;
      for (let y = 0; y < size; y++) {
        for (let x = 0, run = 0, c = null; x <= size; x++) {
          const v = x < size ? mod[y][x] : null;
          if (v === c) run++; else { if (run >= 5) p += 3 + (run - 5); run = 1; c = v; }
        }
      }
      for (let x = 0; x < size; x++) {
        for (let y = 0, run = 0, c = null; y <= size; y++) {
          const v = y < size ? mod[y][x] : null;
          if (v === c) run++; else { if (run >= 5) p += 3 + (run - 5); run = 1; c = v; }
        }
      }
      for (let y = 0; y < size - 1; y++) for (let x = 0; x < size - 1; x++) {
        const c = mod[y][x];
        if (c === mod[y][x + 1] && c === mod[y + 1][x] && c === mod[y + 1][x + 1]) p += 3;
      }
      let dark = 0; mod.forEach(r => r.forEach(v => { if (v) dark++; }));
      const k = Math.ceil(Math.abs(dark * 20 - size * size * 10) / (size * size)) - 1;
      return p + k * 10;
    };
    let best = 0, bestP = Infinity;
    for (let m = 0; m < 8; m++) { applyMask(m); formatBits(m); const p = penalty(); if (p < bestP) { bestP = p; best = m; } applyMask(m); }
    applyMask(best); formatBits(best);
    return { size, modules: mod };
  }
  function toSVG(text) {
    const { size, modules } = encode(text);
    const q = 4, dim = size + q * 2;
    let d = "";
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) if (modules[y][x]) d += `M${x + q} ${y + q}h1v1h-1z`;
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${dim} ${dim}" shape-rendering="crispEdges"><rect width="${dim}" height="${dim}" fill="#fff"/><path d="${d}" fill="#030205"/></svg>`;
  }
  return { toSVG };
})();


window.UNIPoster = {
  boot(cfg) {
    const email = document.getElementById("contact-email");
    const discord = document.getElementById("contact-discord");
    const qrBox = document.getElementById("qr");
    if (email) email.textContent = cfg.contactEmail;
    if (discord) discord.textContent = cfg.contactDiscord;
    if (qrBox) qrBox.innerHTML = QR.toSVG(cfg.qrUrl);
    const stage = document.getElementById("stage");
    if (!stage) return;
    const W = 11 * 96, H = 17 * 96;
    function apply() {
      const pad = 48;
      const s = Math.min(1, (window.innerWidth - pad) / W);
      stage.style.transform = "scale(" + s + ")";
      stage.style.marginBottom = ((s - 1) * H) + "px";
    }
    apply();
    window.addEventListener("resize", apply);
    window.addEventListener("beforeprint", () => {
      stage.style.transform = "none";
      stage.style.marginBottom = "0";
    });
    window.addEventListener("afterprint", apply);
  }
};
