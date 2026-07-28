import fs from "node:fs";
import path from "node:path";

const brandDir = path.join(process.cwd(), "public", "brand");

function jaggedEdge(x0, y0, x1, y1, segs, amp, seed) {
  const pts = [];
  let s = seed;
  const rand = () => {
    s = (s * 16807 + 7) % 2147483647;
    return (s % 1000) / 1000;
  };
  for (let i = 0; i <= segs; i++) {
    const t = i / segs;
    const bx = x0 + (x1 - x0) * t;
    const by = y0 + (y1 - y0) * t;
    const dx = x1 - x0;
    const dy = y1 - y0;
    const len = Math.hypot(dx, dy) || 1;
    // Outward normal for clockwise guide (tears chew silhouette, not photo)
    const nx = dy / len;
    const ny = -dx / len;
    // High-frequency ragged fiber + occasional deeper bite
    let j =
      (rand() - 0.35) * amp * 1.6 +
      Math.sin(t * Math.PI * (9 + (seed % 4))) * amp * 0.55 +
      Math.sin(t * Math.PI * 23 + seed) * amp * 0.35 +
      Math.sin(t * Math.PI * 47 + seed * 0.3) * amp * 0.22 +
      Math.sin(t * Math.PI * 71) * amp * 0.12;
    if (rand() > 0.82) j += (rand() * 0.7 + 0.2) * amp;
    // Clamp so we never eat more than ~amp inward from the guide line
    j = Math.max(-amp * 0.55, Math.min(amp * 1.35, j));
    pts.push([bx + nx * j, by + ny * j]);
  }
  return pts;
}

const inset = 14;
const W = 400;
const H = 520;
const top = jaggedEdge(inset, inset, W - inset, inset, 64, 8.5, 11);
const right = jaggedEdge(W - inset, inset, W - inset, H - inset, 78, 9, 29);
const bottom = jaggedEdge(W - inset, H - inset, inset, H - inset, 64, 8.5, 47);
const left = jaggedEdge(inset, H - inset, inset, inset, 78, 9, 73);

const all = [
  ...top,
  ...right.slice(1),
  ...bottom.slice(1),
  ...left.slice(1),
];

let d = `M${all[0][0].toFixed(2)} ${all[0][1].toFixed(2)}`;
for (let i = 1; i < all.length; i++) {
  const [x, y] = all[i];
  if (i % 3 === 0 && i + 1 < all.length) {
    const [x2, y2] = all[i + 1];
    d += ` Q${x.toFixed(2)} ${y.toFixed(2)} ${((x + x2) / 2).toFixed(2)} ${((y + y2) / 2).toFixed(2)}`;
    i += 1;
  } else {
    d += ` L${x.toFixed(2)} ${y.toFixed(2)}`;
  }
}
d += " Z";

const deckle = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
  <path fill="#fff" d="${d}"/>
</svg>
`;

fs.writeFileSync(path.join(brandDir, "polaroid-deckle-mask.svg"), deckle);

const twine = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 78" fill="none" aria-hidden="true">
  <defs>
    <linearGradient id="t1" x1="0" y1="0" x2="1" y2="0.2">
      <stop offset="0%" stop-color="#c4a882"/>
      <stop offset="35%" stop-color="#b8956a"/>
      <stop offset="70%" stop-color="#a8845c"/>
      <stop offset="100%" stop-color="#9a7650"/>
    </linearGradient>
    <linearGradient id="t2" x1="0" y1="0.25" x2="1" y2="0">
      <stop offset="0%" stop-color="#d8c4a4"/>
      <stop offset="50%" stop-color="#c4a882"/>
      <stop offset="100%" stop-color="#b09068"/>
    </linearGradient>
  </defs>
  <!-- Dual-strand wrap across top -->
  <path d="M8 40 C 28 22, 48 18, 72 30 C 96 42, 118 20, 148 28 C 178 36, 198 18, 228 26 C 258 34, 278 16, 308 24"
    stroke="url(#t1)" stroke-width="2.4" stroke-linecap="round" fill="none" opacity="0.95"/>
  <path d="M10 44 C 30 26, 52 22, 74 34 C 98 46, 120 24, 150 32 C 180 40, 200 22, 230 30 C 260 38, 280 20, 310 28"
    stroke="url(#t2)" stroke-width="1.9" stroke-linecap="round" fill="none" opacity="0.88"/>
  <path d="M6 48 C 36 36, 58 42, 82 36 C 110 28, 132 44, 162 38 C 192 32, 214 46, 246 40 C 272 36, 290 44, 314 38"
    stroke="url(#t1)" stroke-width="2.15" stroke-linecap="round" fill="none" opacity="0.9"/>
  <path d="M8 52 C 38 40, 60 46, 84 40 C 112 32, 134 48, 164 42 C 194 36, 216 50, 248 44 C 274 40, 292 48, 316 42"
    stroke="url(#t2)" stroke-width="1.7" stroke-linecap="round" fill="none" opacity="0.82"/>
  <!-- Left tuck under seal -->
  <path d="M12 42 C 4 50, 2 58, 8 66" stroke="url(#t1)" stroke-width="2.05" stroke-linecap="round" opacity="0.85"/>
  <path d="M18 46 C 10 54, 8 60, 14 68" stroke="url(#t2)" stroke-width="1.65" stroke-linecap="round" opacity="0.75"/>
  <!-- Right side droop -->
  <path d="M298 26 C 312 30, 316 42, 310 54 C 306 62, 312 68, 318 74" stroke="url(#t1)" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>
  <path d="M302 30 C 314 36, 318 46, 312 56 C 308 64, 314 70, 316 76" stroke="url(#t2)" stroke-width="1.75" stroke-linecap="round" opacity="0.8"/>
  <!-- Crossover loop near seal -->
  <path d="M48 32 C 58 18, 78 16, 90 30 C 96 38, 86 46, 72 44" stroke="url(#t1)" stroke-width="2.25" stroke-linecap="round" opacity="0.92"/>
  <path d="M52 36 C 60 24, 76 22, 86 34" stroke="url(#t2)" stroke-width="1.75" stroke-linecap="round" opacity="0.8"/>
</svg>
`;

fs.writeFileSync(path.join(brandDir, "twine-wrap.svg"), twine);

const fiber = `<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 180 180">
  <filter id="n">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 0.52  0 0 0 0 0.46  0 0 0 0 0.36  0 0 0 0.2 0"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#n)"/>
</svg>
`;

fs.writeFileSync(path.join(brandDir, "paper-fiber.svg"), fiber);

// Improved wax seal — darker chocolate, stronger emboss
const seal = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72" fill="none" aria-hidden="true">
  <defs>
    <radialGradient id="waxBody" cx="36%" cy="30%" r="72%">
      <stop offset="0%" stop-color="#6a4532"/>
      <stop offset="40%" stop-color="#3f2a1c"/>
      <stop offset="78%" stop-color="#2a1a12"/>
      <stop offset="100%" stop-color="#1a100a"/>
    </radialGradient>
    <radialGradient id="waxSheen" cx="32%" cy="26%" r="50%">
      <stop offset="0%" stop-color="#a07a58" stop-opacity="0.5"/>
      <stop offset="55%" stop-color="#5c4030" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#2a1a12" stop-opacity="0"/>
    </radialGradient>
    <filter id="innerEmboss" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0.4" dy="0.6" stdDeviation="0.5" flood-color="#120c08" flood-opacity="0.55"/>
    </filter>
  </defs>
  <ellipse cx="36" cy="40" rx="28" ry="5.5" fill="#1a100a" opacity="0.28"/>
  <path fill="url(#waxBody)" d="M36.2 5.2c7.4-.7 13.6 3 18 8.4 3.4 4.2 7.4 5.6 10 10.2 2.8 5 2 11.2-.4 16.2-1.8 3.8-1.4 7.4-3.8 11.2-3 4.8-8.4 9-14 10.6-4.6 1.4-7.8 3.8-12.6 3.2-5.6-.8-10.8-4-14.6-8.6-3-3.8-6.8-5.4-9-9.6C6.2 41.2 5.8 35 7.8 29.4c1.6-4.4 1.2-8.6 4-12.6C16 11.4 21.6 7.2 28 5.8c2.8-.6 5.4-.6 8.2-.6Z"/>
  <path fill="url(#waxSheen)" d="M20 16c9-9 24-9 33 2 4.4 5.5 5.4 13 2.2 19.5-6.6 11-22 15.4-33 8.8-8.8-5.5-11-17.5-2.2-30.3Z" opacity="0.65"/>
  <g stroke="#f0e6d8" stroke-opacity="0.78" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#innerEmboss)">
    <circle cx="36" cy="35" r="16" stroke-width="1.2" opacity="0.5"/>
    <circle cx="36" cy="35" r="12.5" stroke-width="0.7" opacity="0.35"/>
    <path stroke-width="1.25" d="M36 21.5c2 4 2 8 0 12-2-4-2-8 0-12Z"/>
    <path stroke-width="1.2" d="M36 23.5c3.8 1.8 6.8 4.6 8.6 8.4-3.8-1.6-7.6-1.6-11.4 0 1.6-3.6 1.4-6.2 2.8-8.4Z"/>
    <path stroke-width="1.2" d="M36 23.5c-3.8 1.8-6.8 4.6-8.6 8.4 3.8-1.6 7.6-1.6 11.4 0-1.6-3.6-1.4-6.2-2.8-8.4Z"/>
    <path stroke-width="1.1" d="M27 38c2.6 1.2 5.6 1.8 9 1.8s6.4-.6 9-1.8"/>
    <path stroke-width="1.05" d="M28.5 42c2.4 1.3 4.8 1.9 7.5 1.9s5.1-.6 7.5-1.9"/>
    <circle cx="36" cy="37" r="1.8" fill="#f0e6d8" fill-opacity="0.6" stroke="none"/>
  </g>
</svg>
`;

fs.writeFileSync(path.join(brandDir, "wax-seal.svg"), seal);

console.log("Wrote polaroid-deckle-mask.svg, twine-wrap.svg, paper-fiber.svg, wax-seal.svg");
