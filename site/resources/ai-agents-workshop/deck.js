(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const W = 1600, H = 900;
  const stage = $('#stage');
  const slides = $$('.slide', stage);
  let cur = 0;
  let runToken = 0;

  /* ---------- scaling ---------- */
  function fit() {
    const s = Math.min(innerWidth / W, innerHeight / H);
    stage.style.transform = `translate(-50%, -50%) scale(${s})`;
  }
  addEventListener('resize', fit);
  fit();

  /* ---------- navigation ---------- */
  const frags = (sl) => $$('.f', sl);

  function markCurrent(sl) {
    const on = frags(sl).filter((f) => f.classList.contains('on'));
    $$('.f.cur', sl).forEach((f) => f.classList.remove('cur'));
    const last = on[on.length - 1];
    if (last) last.classList.add('cur');
    sl.classList.toggle('started', on.length > 0);
    const hook = hooks[sl.id];
    if (hook && hook.step) hook.step(sl, last, on.length);
    if (last && last.dataset.hook && hooks[last.dataset.hook]) hooks[last.dataset.hook](last);
  }

  function go(i, { allFrags = false } = {}) {
    if (i < 0 || i >= slides.length) return;
    const prevIdx = cur;
    cur = i;
    runToken++;
    slides.forEach((sl, k) => {
      sl.classList.toggle('active', k === cur);
      sl.classList.toggle('past', k < cur);
    });
    const sl = slides[cur];
    frags(sl).forEach((f) => f.classList.toggle('on', allFrags));
    $$('.flip.flipped', sl).forEach((f) => f.classList.remove('flipped'));
    markCurrent(sl);
    const hook = hooks[sl.id];
    if (hook && hook.enter) hook.enter(sl, runToken);
    if (sl.classList.contains('s-end') && prevIdx !== cur) setTimeout(() => burst(innerWidth * 0.3, innerHeight * 0.35, 70), 500);
    updateHud();
    history.replaceState(null, '', `#${cur + 1}`);
  }

  function next() {
    const sl = slides[cur];
    const pending = frags(sl).find((f) => !f.classList.contains('on'));
    if (pending) {
      pending.classList.add('on');
      markCurrent(sl);
      if (pending.classList.contains('res')) {
        const r = pending.getBoundingClientRect();
        burst(r.left + r.width / 2, r.top + r.height / 2, 46);
      }
      return;
    }
    go(cur + 1);
  }

  function prev() {
    const sl = slides[cur];
    const on = frags(sl).filter((f) => f.classList.contains('on'));
    if (on.length) {
      on[on.length - 1].classList.remove('on');
      markCurrent(sl);
      return;
    }
    go(cur - 1, { allFrags: true });
  }

  function updateHud() {
    const sl = slides[cur];
    $('#count').textContent = `${String(cur + 1).padStart(2, '0')} / ${slides.length}`;
    $('#sec-name').textContent = sl.dataset.section || '';
    $('#progress').style.width = `${((cur + 1) / slides.length) * 100}%`;
    const n = $('.notes', sl);
    $('#notes-body').textContent = n ? n.textContent : '—';
  }

  addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key;
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(k)) { e.preventDefault(); next(); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(k)) { e.preventDefault(); prev(); }
    else if (k === 'Home') go(0);
    else if (k === 'End') go(slides.length - 1, { allFrags: true });
    else if (k === 'f' || k === 'F') toggleFs();
    else if (k === 'n' || k === 'N') $('#notes-panel').classList.toggle('show');
    hideHelp();
  });

  const interactive = 'button, a, input, code, kbd, .flip, .panel, .prompt, .cmd, .credits, .tab, .notes-panel, .hud';
  stage.addEventListener('click', (e) => {
    if (e.target.closest(interactive)) return;
    if (String(getSelection())) return;
    if (e.clientX < innerWidth * 0.25) prev(); else next();
    hideHelp();
  });

  let tx = null, ty = null;
  addEventListener('touchstart', (e) => { tx = e.touches[0].clientX; ty = e.touches[0].clientY; }, { passive: true });
  addEventListener('touchend', (e) => {
    if (tx === null) return;
    const dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) (dx < 0 ? next : prev)();
    tx = null;
  });

  $('#next').addEventListener('click', next);
  $('#prev').addEventListener('click', prev);
  $('#fs').addEventListener('click', toggleFs);
  function toggleFs() {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen?.();
  }

  function hideHelp() { $('#help').classList.add('gone'); }
  setTimeout(hideHelp, 7000);

  let idleT;
  addEventListener('mousemove', () => {
    document.body.classList.remove('idle');
    clearTimeout(idleT);
    idleT = setTimeout(() => document.body.classList.add('idle'), 3000);
  });

  /* ---------- copy + tabs + flips ---------- */
  $$('.copy').forEach((b) => b.addEventListener('click', async () => {
    const host = b.closest('.cmd, .quest');
    const src = host && (host.querySelector('code') || host.querySelector('.prompt'));
    const text = src ? src.textContent.trim() : '';
    try { await navigator.clipboard.writeText(text); }
    catch {
      const ta = Object.assign(document.createElement('textarea'), { value: text });
      document.body.append(ta); ta.select(); document.execCommand('copy'); ta.remove();
    }
    const old = b.textContent;
    b.textContent = 'copied ✓'; b.classList.add('done');
    const r = b.getBoundingClientRect(); burst(r.left + r.width / 2, r.top, 14);
    setTimeout(() => { b.textContent = old; b.classList.remove('done'); }, 1400);
  }));

  $$('.tab').forEach((t) => t.addEventListener('click', () => {
    const box = t.closest('.slide');
    $$('.tab', box).forEach((x) => x.classList.toggle('sel', x === t));
    $$('.pane', box).forEach((p) => p.classList.toggle('sel', p.dataset.pane === t.dataset.pane));
  }));

  $$('.flip').forEach((f) => f.addEventListener('click', () => {
    if (f.classList.contains('on')) f.classList.toggle('flipped');
    else { f.classList.add('on'); markCurrent(f.closest('.slide')); }
  }));

  /* ---------- slide hooks ---------- */
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const hooks = {};

  // timeline track built from the eras
  const tl = $('#timeline');
  const eras = $$('.era', tl);
  const track = $('#track');
  eras.forEach((era, i) => {
    const t = document.createElement('div');
    t.className = 'tick';
    t.style.left = `${(i / (eras.length - 1)) * 100}%`;
    t.textContent = $('.year', era).textContent;
    track.append(t);
  });
  hooks.timeline = {
    step(sl, last, n) {
      const ticks = $$('.tick', track);
      ticks.forEach((t, i) => { t.classList.toggle('on', i < n); t.classList.toggle('cur', i === n - 1); });
      $('.fill', track).style.width = n ? `${((n - 1) / (eras.length - 1)) * 100}%` : '0';
    },
  };

  hooks.eliza = async (era) => {
    const box = $('#eliza');
    const token = runToken;
    const script = [
      ['u', 'Men are all alike.'], ['e', 'IN WHAT WAY?'],
      ['u', "They're always bugging us about something or other."], ['e', 'CAN YOU THINK OF A SPECIFIC EXAMPLE?'],
      ['u', 'Well, my boyfriend made me come here.'], ['e', 'YOUR BOYFRIEND MADE YOU COME HERE?'],
    ];
    box.innerHTML = '';
    for (const [who, text] of script) {
      const line = document.createElement('div');
      line.className = who === 'u' ? 'u' : '';
      box.append(line);
      const prefix = who === 'u' ? '> ' : '';
      for (let i = 0; i <= text.length; i++) {
        if (token !== runToken || !era.classList.contains('cur')) return;
        line.innerHTML = prefix + text.slice(0, i) + '<span class="cursor"></span>';
        await sleep(who === 'u' ? 32 : 18);
      }
      line.textContent = prefix + text;
      await sleep(who === 'u' ? 350 : 650);
    }
    box.insertAdjacentHTML('beforeend', '<div>&gt; <span class="cursor"></span></div>');
  };

  // chatbot vs agent
  hooks.versus = {
    async enter(sl, token) {
      const bot = $('#vs-bot'), ag = $('#vs-agent');
      bot.innerHTML = ''; ag.innerHTML = '';
      const ask = '<div class="msg me">My bike tire is flat and I have class at 9.</div>';
      bot.insertAdjacentHTML('beforeend', ask);
      ag.insertAdjacentHTML('beforeend', ask);
      await sleep(900); if (token !== runToken) return;

      const reply = document.createElement('div');
      reply.className = 'msg it';
      bot.append(reply);
      const text = "Oh no! Here's how to fix a flat:\n1. Remove the wheel\n2. Find the puncture\n3. Patch the tube\n4. Re-inflate to the right PSI\nGood luck! 🚲";
      (async () => {
        for (let i = 0; i <= text.length; i++) {
          if (token !== runToken) return;
          reply.textContent = text.slice(0, i);
          await sleep(26);
        }
        await sleep(400);
        if (token === runToken) bot.insertAdjacentHTML('beforeend', '<div class="small" style="margin-top:auto">…and now <b>you</b> still have to do all of it.</div>');
      })();

      const steps = [
        ['🔎', 'Search bike shops near SAIT', '3 found'],
        ['📅', 'Check your calendar', 'free 5–6 PM'],
        ['🛠️', 'Book a repair at Cycle Co.', '5:15 PM ✓'],
        ['🚌', 'Plan your bus to class', '8:12 AM ✓'],
      ];
      for (const [ico, label, res] of steps) {
        if (token !== runToken) return;
        const el = document.createElement('div');
        el.className = 'step spin';
        el.innerHTML = `<span class="ico">${ico}</span><span>${label}</span><span class="st">working</span>`;
        el.style.animation = 'rise .4s var(--ease) both';
        ag.append(el);
        await sleep(900); if (token !== runToken) return;
        el.classList.remove('spin');
        $('.st', el).textContent = res;
      }
      await sleep(300); if (token !== runToken) return;
      ag.insertAdjacentHTML('beforeend', '<div class="done-banner" style="animation:popin .5s var(--bounce) both">✓ Bike booked for 5:15. Bus at 8:12. You\'re not late.</div>');
    },
  };
  $('#versus .versus').addEventListener('click', () => { runToken++; hooks.versus.enter(null, runToken); });

  // loop: highlight node from story fragment
  hooks.loop = {
    step(sl, last) {
      $$('.node', sl).forEach((n) => n.classList.remove('hot'));
      if (last && last.dataset.node) $(`.node.${last.dataset.node}`, sl).classList.add('hot');
    },
  };

  // terminal simulation
  const simScript = [
    ['perceive', 'user', '› Turn @notes.md into a quiz page I can open in my browser'],
    ['perceive', 'tl', '→ <b>Read</b> notes.md  (48 lines)'],
    ['decide', 'think', '  12 key terms found. Plan: one quiz.html, 10 questions, a score.'],
    ['act', 'tl', '→ <b>Write</b> quiz.html  +118 lines'],
    ['check', 'tl', '→ <b>Bash</b> open quiz.html'],
    ['check', 'think', '  Hmm, question 7 has two correct answers. Fixing that.'],
    ['act', 'tl', '→ <b>Edit</b> quiz.html  +2 −2'],
    ['check', 'ok', '✓ All 10 questions have exactly one answer'],
    ['check', 'final', 'Done. Open quiz.html. Want a harder round?'],
  ];
  hooks.sim = {
    async enter(sl, token) {
      const out = $('#term-out');
      const phases = $$('.phase', sl);
      out.innerHTML = '';
      phases.forEach((p) => p.classList.remove('hot'));
      await sleep(700);
      for (const [phase, cls, html] of simScript) {
        if (token !== runToken) return;
        phases.forEach((p) => p.classList.toggle('hot', p.dataset.p === phase));
        const ln = document.createElement('div');
        ln.className = `ln ${cls}`;
        out.append(ln);
        if (cls === 'user') {
          for (let i = 0; i <= html.length; i++) {
            if (token !== runToken) return;
            ln.textContent = html.slice(0, i);
            await sleep(28);
          }
          await sleep(500);
        } else {
          ln.innerHTML = html;
          await sleep(cls === 'think' ? 1500 : 1050);
        }
      }
      phases.forEach((p) => p.classList.remove('hot'));
    },
  };
  $('#replay').addEventListener('click', () => { runToken++; hooks.sim.enter(slides[cur], runToken); });

  // compression timeline positions, to scale by date
  const ctl = $('#ctl');
  const evs = $$('.ev', ctl);
  const t0 = new Date('2022-11-30').getTime(), t1 = new Date('2026-09-29').getTime();
  evs.forEach((ev) => {
    const p = (new Date(ev.dataset.date).getTime() - t0) / (t1 - t0);
    ev.style.left = `${6 + p * 88}%`;
  });

  // "x days ago" badges
  const today = new Date(); today.setHours(0, 0, 0, 0);
  $$('[data-since]').forEach((el) => {
    const d = Math.round((today - new Date(el.dataset.since + 'T00:00:00')) / 86400000);
    el.textContent = d <= 0 ? 'today' : d === 1 ? 'yesterday' : d < 21 ? `${d} days ago` : `${Math.round(d / 7)} weeks ago`;
  });

  /* ---------- confetti burst ---------- */
  const colors = ['#BAF837', '#FA4A9E', '#7EC8FF', '#FFC857', '#F9F9FA'];
  function burst(x, y, n = 30) {
    for (let i = 0; i < n; i++) {
      const s = document.createElement('div');
      s.className = 'spark';
      s.style.left = `${x}px`; s.style.top = `${y}px`;
      s.style.background = colors[i % colors.length];
      const a = Math.random() * Math.PI * 2, d = 80 + Math.random() * 220;
      const size = 6 + Math.random() * 8;
      s.style.width = s.style.height = `${size}px`;
      if (Math.random() > 0.5) s.style.borderRadius = '2px';
      document.body.append(s);
      s.animate([
        { transform: 'translate(-50%,-50%) scale(1)', opacity: 1 },
        { transform: `translate(calc(-50% + ${Math.cos(a) * d}px), calc(-50% + ${Math.sin(a) * d + 120}px)) rotate(${Math.random() * 540}deg) scale(.4)`, opacity: 0 },
      ], { duration: 900 + Math.random() * 700, easing: 'cubic-bezier(.2,.8,.2,1)' }).onfinish = () => s.remove();
    }
  }

  /* ---------- plankton background ---------- */
  const cv = $('#bg'), cx = cv.getContext('2d');
  let parts = [];
  function sizeCanvas() {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    cv.width = innerWidth * dpr; cv.height = innerHeight * dpr;
    cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const count = Math.round((innerWidth * innerHeight) / 22000);
    parts = Array.from({ length: count }, () => ({
      x: Math.random() * innerWidth, y: Math.random() * innerHeight,
      r: 0.6 + Math.random() * 2.2, v: 0.12 + Math.random() * 0.4,
      ph: Math.random() * Math.PI * 2, c: colors[Math.floor(Math.random() * 3)],
    }));
  }
  sizeCanvas();
  addEventListener('resize', sizeCanvas);
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function tick(t) {
    cx.clearRect(0, 0, innerWidth, innerHeight);
    for (const p of parts) {
      p.y -= p.v; p.x += Math.sin(t / 1800 + p.ph) * 0.25;
      if (p.y < -10) { p.y = innerHeight + 10; p.x = Math.random() * innerWidth; }
      cx.globalAlpha = 0.25 + 0.35 * (0.5 + 0.5 * Math.sin(t / 900 + p.ph));
      cx.fillStyle = p.c;
      cx.beginPath(); cx.arc(p.x, p.y, p.r, 0, Math.PI * 2); cx.fill();
    }
    if (!still) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  /* ---------- start ---------- */
  const startAt = parseInt(location.hash.slice(1), 10);
  go(Number.isFinite(startAt) ? Math.min(Math.max(startAt - 1, 0), slides.length - 1) : 0);
})();
