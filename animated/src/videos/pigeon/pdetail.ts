// Set detail for The Pigeon Escape: painted grime / cracks / moss / rust textures, vine and sign decals, and the
// San Francisco bay for the escape (Alcatraz-style island prison, the Golden Gate, the city skyline).
import * as THREE from "three";
import { lam, boxGeo, Batch, V } from "../bridge/build";
import { ctex } from "../bridge/paint";

type R = () => number;
const pick = <T,>(r: R, a: T[]) => a[Math.floor(r() * a.length) % a.length];

/** random-walk crack with a couple of branches */
const crack = (g: CanvasRenderingContext2D, r: R, x: number, y: number, len: number, w: number) => {
  g.strokeStyle = "rgba(28,22,24,0.9)"; g.lineCap = "round"; g.lineJoin = "round";
  let a = r() * Math.PI * 2;
  const seg = (x0: number, y0: number, n: number, lw: number) => {
    g.lineWidth = lw; g.beginPath(); g.moveTo(x0, y0);
    let px = x0, py = y0;
    for (let i = 0; i < n; i++) {
      a += (r() - 0.5) * 1.1; px += Math.cos(a) * 14; py += Math.sin(a) * 14; g.lineTo(px, py);
      if (r() < 0.12 && lw > 1.2) { g.stroke(); const sa = a; a += (r() < 0.5 ? 1 : -1) * 0.9; seg(px, py, n / 3, lw * 0.6); a = sa; g.lineWidth = lw; g.beginPath(); g.moveTo(px, py); }
    }
    g.stroke();
  };
  seg(x, y, len, w);
};

/** stone blocks + vertical grime streaks + moss + cracks (1024 px tile, meant for ~2 m) */
export const wallTex = (key: string, cols: string[], mortar: string, moss = 0.35) => ctex(key, 1024, 1024, (g, r) => {
  g.fillStyle = mortar; g.fillRect(0, 0, 1024, 1024);
  const RH = 96;
  for (let row = 0; row < 1024 / RH + 1; row++) {
    let x = -(row % 2) * 95 - r() * 40;
    while (x < 1024) {
      const w = 150 + r() * 120;
      g.fillStyle = pick(r, cols); g.fillRect(x + 4, row * RH + 4, w - 8, RH - 8);
      g.fillStyle = "rgba(255,255,255,0.07)"; g.fillRect(x + 4, row * RH + 4, w - 8, 7);
      g.fillStyle = "rgba(0,0,0,0.13)"; g.fillRect(x + 4, row * RH + RH - 11, w - 8, 7);
      if (r() < 0.18) { g.fillStyle = mortar; g.beginPath(); g.arc(x + r() * w, row * RH + r() * RH, 6 + r() * 12, 0, 7); g.fill(); } // chipped corner
      x += w;
    }
  }
  for (let i = 0; i < 46; i++) { g.fillStyle = `rgba(38,32,28,${0.05 + r() * 0.12})`; g.fillRect(r() * 1024, r() * 1024, 3 + r() * 12, 120 + r() * 420); }
  for (let i = 0; i < 16; i++) {
    const x = r() * 1024, y = r() * 1024, rad = 40 + r() * 110, gr = g.createRadialGradient(x, y, 0, x, y, rad);
    gr.addColorStop(0, `rgba(72,112,52,${moss})`); gr.addColorStop(1, "rgba(72,112,52,0)"); g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2);
  }
  for (let i = 0; i < 9; i++) crack(g, r, r() * 1024, r() * 1024, 10 + r() * 22, 2.5 + r() * 2.5);
});

/** cracked, dirty floor slabs */
export const floorTex = () => ctex("pg_floorD", 1024, 1024, (g, r) => {
  g.fillStyle = "#4f4b48"; g.fillRect(0, 0, 1024, 1024);
  const S = 256;
  for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) {
    g.fillStyle = pick(r, ["#7d7873", "#76716c", "#86817b", "#6e6a66"]); g.fillRect(x * S + 5, y * S + 5, S - 10, S - 10);
    g.fillStyle = "rgba(0,0,0,0.08)"; g.fillRect(x * S + 5, y * S + S - 18, S - 10, 13);
  }
  for (let i = 0; i < 30; i++) { const x = r() * 1024, y = r() * 1024, rad = 30 + r() * 90, gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, "rgba(35,30,26,0.25)"); gr.addColorStop(1, "rgba(35,30,26,0)"); g.fillStyle = gr; g.fillRect(x - rad, y - rad, 2 * rad, 2 * rad); }
  for (let i = 0; i < 12; i++) crack(g, r, r() * 1024, r() * 1024, 12 + r() * 20, 2 + r() * 2.5);
});

/** rusty iron: dark metal with orange rust blotches and drip streaks */
export const rustTex = () => ctex("pg_rustT", 256, 256, (g, r) => {
  g.fillStyle = "#4a4448"; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 60; i++) { g.fillStyle = pick(r, ["rgba(150,82,40,0.55)", "rgba(184,112,48,0.5)", "rgba(110,60,34,0.6)"]); g.beginPath(); g.ellipse(r() * 256, r() * 256, 4 + r() * 18, 3 + r() * 10, r() * 3, 0, 7); g.fill(); }
  for (let i = 0; i < 20; i++) { g.fillStyle = "rgba(140,74,36,0.45)"; g.fillRect(r() * 256, r() * 256, 2 + r() * 3, 30 + r() * 80); }
});

/** hanging vines with leaves (transparent, 512 x 1024; hangs from the top edge) */
export const vineTex = (seed: number) => ctex("pg_vine" + seed, 512, 1024, (g, r) => {
  for (let s = 0; s < 4 + (seed % 3); s++) {
    let x = 60 + r() * 392, y = -10, a = Math.PI / 2;
    const len = 30 + r() * 40, pts: [number, number][] = [[x, y]];
    for (let i = 0; i < len; i++) { a += (r() - 0.5) * 0.5; a = Math.max(0.6, Math.min(2.5, a)); x += Math.cos(a) * 16; y += Math.sin(a) * 16; pts.push([x, y]); }
    g.strokeStyle = "#24361a"; g.lineWidth = 9; g.lineCap = "round"; g.beginPath(); pts.forEach(([px, py], i) => (i ? g.lineTo(px, py) : g.moveTo(px, py))); g.stroke();
    g.strokeStyle = "#456b2e"; g.lineWidth = 5; g.stroke();
    pts.forEach(([px, py], i) => {
      if (i % 2) return;
      for (const side of [-1, 1]) {
        if (r() < 0.25) continue;
        const la = side * (0.6 + r() * 0.7), L = 18 + r() * 16;
        g.save(); g.translate(px, py); g.rotate(la + Math.PI / 2 * side * 0.3);
        g.fillStyle = pick(r, ["#4f8a3a", "#3f7a30", "#67a048", "#5a9440"]); g.strokeStyle = "#24361a"; g.lineWidth = 2.5;
        g.beginPath(); g.ellipse(side * L * 0.6, 0, L * 0.6, L * 0.32, 0, 0, 7); g.fill(); g.stroke(); g.restore();
      }
    });
  }
});

/** scratched tally marks + the escape plan doodle (transparent, 512 x 512) */
export const tallyTex = () => ctex("pg_tally", 512, 512, (g, r) => {
  g.strokeStyle = "rgba(236,230,218,0.85)"; g.lineCap = "round"; g.lineWidth = 4;
  for (let row = 0; row < 5; row++) for (let grp = 0; grp < 6; grp++) {
    const x0 = 20 + grp * 80, y0 = 20 + row * 52;
    for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(x0 + k * 12 + r() * 2, y0); g.lineTo(x0 + k * 12 + r() * 3, y0 + 38); g.stroke(); }
    g.beginPath(); g.moveTo(x0 - 6, y0 + 32); g.lineTo(x0 + 46, y0 + 6); g.stroke();
  }
  // the plan: a pigeon doodle -> arrow -> stick man flying -> "PLAN"
  g.lineWidth = 5;
  g.beginPath(); g.ellipse(90, 400, 34, 22, 0, 0, 7); g.stroke(); g.beginPath(); g.arc(128, 382, 14, 0, 7); g.stroke();
  g.beginPath(); g.moveTo(140, 380); g.lineTo(158, 386); g.lineTo(140, 390); g.stroke(); g.beginPath(); g.moveTo(80, 392); g.lineTo(60, 360); g.lineTo(100, 388); g.stroke();
  g.beginPath(); g.moveTo(190, 400); g.lineTo(290, 400); g.lineTo(272, 388); g.moveTo(290, 400); g.lineTo(272, 412); g.stroke();
  g.beginPath(); g.arc(360, 360, 12, 0, 7); g.moveTo(360, 372); g.lineTo(360, 420); g.moveTo(360, 385); g.lineTo(340, 360); g.moveTo(360, 385); g.lineTo(382, 360);
  g.moveTo(360, 420); g.lineTo(345, 450); g.moveTo(360, 420); g.lineTo(375, 450); g.stroke();
  for (const dx of [-30, 0, 30]) { g.beginPath(); g.moveTo(360 + dx * 0.5, 345); g.lineTo(360 + dx, 300); g.stroke(); g.beginPath(); g.arc(360 + dx, 292, 8, 0, 7); g.stroke(); }
  g.font = "bold 46px Arial"; g.fillStyle = "rgba(236,230,218,0.85)"; g.fillText("PLAN", 400, 480);
});

export const webTex = () => ctex("pg_web", 256, 256, (g) => {
  g.strokeStyle = "rgba(240,240,240,0.7)"; g.lineWidth = 1.6;
  for (let i = 0; i < 9; i++) { const a = (i / 8) * Math.PI / 2; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * 250, Math.sin(a) * 250); g.stroke(); }
  for (let k = 1; k < 9; k++) { g.beginPath(); for (let i = 0; i <= 8; i++) { const a = (i / 8) * Math.PI / 2, rr = k * 27 + (i % 2) * 4; i ? g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : g.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); } g.stroke(); }
});

export const puddleTex = () => ctex("pg_puddle", 256, 256, (g) => {
  const gr = g.createRadialGradient(128, 128, 20, 128, 128, 124);
  gr.addColorStop(0, "rgba(70,84,104,0.85)"); gr.addColorStop(0.8, "rgba(60,70,88,0.7)"); gr.addColorStop(1, "rgba(60,70,88,0)");
  g.fillStyle = gr; g.beginPath(); g.ellipse(128, 128, 124, 90, 0.3, 0, 7); g.fill();
  g.fillStyle = "rgba(220,230,245,0.45)"; g.beginPath(); g.ellipse(100, 108, 40, 9, 0.3, 0, 7); g.fill();
});

/** signs: white board, red border, black text; optional crossed-out pigeon */
export const signTex = (key: string, lines: [string, number][], noPigeon = false) => ctex(key, 512, 320, (g) => {
  g.fillStyle = "#f2ede0"; g.fillRect(0, 0, 512, 320);
  g.strokeStyle = "#b8302c"; g.lineWidth = 18; g.strokeRect(9, 9, 494, 302);
  g.fillStyle = "rgba(90,60,30,0.25)"; for (let i = 0; i < 6; i++) g.fillRect(20 + i * 80, 20, 8, 280); // weathering
  g.fillStyle = "#1c1a1e"; g.textAlign = "center";
  let y = noPigeon ? 92 : 80;
  for (const [t, s] of lines) { g.font = `900 ${s}px Arial Black, Arial`; g.fillText(t, noPigeon ? 330 : 256, y + s * 0.35); y += s * 1.15; }
  if (noPigeon) {
    g.fillStyle = "#6c7486"; g.beginPath(); g.ellipse(120, 180, 56, 38, 0, 0, 7); g.fill(); g.beginPath(); g.arc(172, 146, 24, 0, 7); g.fill();
    g.fillStyle = "#f0a43a"; g.beginPath(); g.moveTo(192, 142); g.lineTo(214, 150); g.lineTo(192, 156); g.fill();
    g.strokeStyle = "#d8322f"; g.lineWidth = 16; g.beginPath(); g.arc(140, 170, 92, 0, 7); g.stroke(); g.beginPath(); g.moveTo(75, 105); g.lineTo(205, 235); g.stroke();
  }
});

/** skyscraper facade: window grid, some lit */
const facadeTex = (k: number) => ctex("pg_tower" + k, 256, 256, (g, r) => {
  const wall = ["#c9b8a0", "#9aa3b0", "#b49a84", "#d8d0c0", "#7f8a98"][k % 5];
  g.fillStyle = wall; g.fillRect(0, 0, 256, 256);
  for (let y = 8; y < 256; y += 32) for (let x = 8; x < 256; x += 24) {
    g.fillStyle = r() < 0.22 ? "#ffd98a" : pick(r, ["#2e3b52", "#3a4a66", "#45577a"]); g.fillRect(x, y, 14, 20);
  }
});

/** San Francisco bay seen from the flock: water, island prison, Golden Gate, skyline, hills */
export const buildBay = (root: THREE.Object3D, wall: THREE.Material, roof: THREE.Material, prison: [number, number, number]) => {
  const b = new Batch();
  const box = (m: THREE.Material, x0: number, y0: number, z0: number, x1: number, y1: number, z1: number, tile = 0) => b.add(boxGeo(V(x0, y0, z0), V(x1, y1, z1), tile), m);
  // water (unlit gradient-ish blue, fog tints it into the haze)
  const water = new THREE.Mesh(new THREE.PlaneGeometry(2400, 2400), new THREE.MeshBasicMaterial({ color: "#3f6f9c" }));
  water.rotation.x = -Math.PI / 2; water.position.set(1000, -0.3, -400); root.add(water);
  const white = lam("pg_white", () => ({ color: "#ece6da" }));
  const [px, , pz] = prison;
  // the Golden Gate (spans the view behind the island)
  const red = lam("pg_gg", () => ({ color: "#c4412f" }));
  const Z = pz - 330, D = 30, X0 = px - 170, X1 = px + 190, T0 = px - 70, T1 = px + 90, TH = 112;
  box(red, X0, D - 2, Z - 12, X1, D, Z + 12);
  for (const tx of [T0, T1]) {
    for (const s of [-1, 1]) box(red, tx - 3, -0.3, Z + s * 11 - 3, tx + 3, TH, Z + s * 11 + 3);
    for (const h of [D + 12, 60, 85, TH - 4]) box(red, tx - 2.5, h, Z - 11, tx + 2.5, h + 4, Z + 11);
  }
  const cable = (xa: number, ya: number, xb: number, yb: number, sag: number) => {
    for (const s of [-1, 1]) for (let i = 0; i < 24; i++) {
      const u0 = i / 24, u1 = (i + 1) / 24, y = (u: number) => ya + (yb - ya) * u - sag * 4 * u * (1 - u);
      const a = V(xa + (xb - xa) * u0, y(u0), Z + s * 11), c = V(xa + (xb - xa) * u1, y(u1), Z + s * 11), len = a.distanceTo(c);
      const g = new THREE.BoxGeometry(len, 1.1, 1.1); const m = new THREE.Matrix4().compose(a.clone().add(c).multiplyScalar(0.5), new THREE.Quaternion().setFromUnitVectors(V(1, 0, 0), c.clone().sub(a).normalize()), V(1, 1, 1));
      b.add(g, red, m);
      if (i % 2 === 0) b.add(new THREE.BoxGeometry(0.5, Math.max(0.5, y(u0) - D), 0.5).translate(a.x, (y(u0) + D) / 2, a.z), red);
    }
  };
  cable(T0, TH, T1, TH, TH - D - 6); cable(X0, D + 2, T0, TH, 18); cable(T1, TH, X1, D + 2, 18);
  // skyline behind the bridge: towers with lit windows, the pyramid, a hill with a round tower
  const fac = [0, 1, 2, 3, 4].map((k) => lam("pg_towerM" + k, () => ({ map: facadeTex(k) })));
  const rnd = (i: number, s: number) => { const v = Math.sin(i * 91.7 + s * 47.3) * 43758.5453; return v - Math.floor(v); };
  for (let i = 0; i < 520; i++) {
    const gx = i % 40, gz = Math.floor(i / 40), x = px - 360 + gx * 18 + rnd(i, 1) * 6, z = pz - 440 - gz * 20 - rnd(i, 2) * 6;
    const centre = Math.exp(-(((x - px - 30) / 150) ** 2)) + 0.6 * Math.exp(-(((x - px + 230) / 70) ** 2)), h = 14 + rnd(i, 3) * 45 + centre * (60 + rnd(i, 4) * 110), w = 9 + rnd(i, 5) * 8;
    box(fac[i % 5], x - w / 2, -0.3, z - w / 2, x + w / 2, h, z + w / 2, 16);
    if (h > 110 && rnd(i, 6) < 0.5) box(white, x - 1, h, z - 1, x + 1, h + 18, z + 1);
  }
  b.add(new THREE.ConeGeometry(14, 190, 4).rotateY(Math.PI / 4).translate(px + 30, 95, pz - 520), white);
  const hill = lam("pg_hill", () => ({ color: "#7f8f5a" })), hill2 = lam("pg_hill2", () => ({ color: "#8c7f62" }));
  b.add(new THREE.SphereGeometry(1, 16, 10).scale(140, 60, 60).translate(px - 160, -10, pz - 520), hill);
  b.add(new THREE.SphereGeometry(1, 16, 10).scale(220, 110, 90).translate(px + 60, -30, pz - 690), hill2);
  b.add(new THREE.SphereGeometry(1, 16, 10).scale(260, 130, 100).translate(px - 300, -20, pz - 420), hill);
  b.add(new THREE.CylinderGeometry(4, 4.5, 34, 12).translate(px - 160, 66, pz - 520), white);
  b.build(root, false);
};
