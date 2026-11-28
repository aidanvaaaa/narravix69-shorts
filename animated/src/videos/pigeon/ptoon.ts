// Pigeon Escape cast drawings (same Pen ink style as the bridge characters): outfits, the pigeon, small props.
import { Pen, INK, SKIN, OFFICER, Outfit, mix } from "../bridge/toon";

type P2 = [number, number];

export const PRISONER: Outfit = { jacket: "#f08a2c", pants: "#e27a24", boots: "#5a3b2a", hat: "hair", hair: "#3a2a20", skin: SKIN, buttons: "#fbe7c8" };
export const GUARD_A: Outfit = { jacket: "#3a5a92", pants: "#26385e", boots: INK, hat: "cap", cap: "#22345a", belt: "#1b1b1f", buttons: "#e8c45a", skin: "#f5c9a0" };
export const GUARD_B: Outfit = { jacket: "#3a5a92", pants: "#26385e", boots: INK, hat: "cap", cap: "#22345a", belt: "#1b1b1f", buttons: "#e8c45a", skin: "#ecd0b6", build: "stout" };
export const WARDEN: Outfit = { ...OFFICER, jacket: "#4c6b45", pants: "#33482f", sash: "#c9a94a", sword: false, moustache: "#2a1a14", skin: "#f5c9a0" };

const BODY = "#9aa3b5", BODY_LO = "#7e889c", WING = "#7c8598", NECK_G = "#4fa58a", NECK_P = "#8a5aa6", BEAK = "#f0a43a", FEET = "#e48a8a";

/** a chubby cartoon pigeon in the 600 x 1000 card, feet on y = 975, facing screen-right.
 *  flap -1..1 (wing angle), peck 0..1 (head down), fly = legs tucked */
export const drawPigeon = (p: Pen, flap: number, peck: number, fly: boolean, tired = false) => {
  const cx = 300, cy = 860;
  p.ol = 9;
  // tail
  p.poly([[cx - 70, cy - 6], [cx - 150, cy - 30], [cx - 140, cy + 22]], BODY_LO);
  // legs
  if (!fly) for (const dx of [-14, 18]) { p.stroke([[cx + dx, cy + 50], [cx + dx, cy + 108]], 9, FEET); p.stroke([[cx + dx, cy + 108], [cx + dx + 22, cy + 112]], 8, FEET); }
  // body
  p.ell(cx, cy + 8, 98, 64, BODY);
  p.ell(cx + 10, cy + 30, 70, 34, mix(BODY, "#ffffff", 0.25), 0);
  // head + neck, pecking rotates them forward/down
  const a = peck * 0.9, hx = cx + 62 + 40 * Math.sin(a), hy = cy - 48 + 52 * Math.sin(a);
  p.poly([[cx + 30, cy - 10], [hx - 14, hy + 14], [hx + 18, hy + 22], [cx + 70, cy + 18]], NECK_G);
  p.ell(cx + 52, cy - 4, 26, 30, NECK_P, 0);
  p.ell(hx, hy, 38, 35, BODY);
  p.poly([[hx + 30, hy - 6], [hx + 66, hy + 6], [hx + 30, hy + 14]], BEAK, 6);
  if (tired) { p.arc(hx + 10, hy - 4, 10, 6, 200, 340, 6); p.dot(hx + 24, hy - 26, 7, "#9fd8ff"); }
  else { p.ell(hx + 10, hy - 6, 11, 11, "#fff6e0", 4); p.dot(hx + 12, hy - 6, 6); }
  // wing
  const w = flap;
  const base: P2 = [cx - 6, cy - 10];
  const tip: P2 = [cx - 110, cy - 10 - 120 * w];
  p.poly([[base[0] + 50, base[1]], [base[0] + 10, base[1] - 30 - 40 * w], tip, [base[0] - 70, base[1] + 30 - 30 * w], [base[0] + 40, base[1] + 26]], WING);
  p.stroke([[cx - 40, cy - 6 - 50 * w], [cx - 70, cy + 6 - 60 * w]], 5);
  p.ol = 12;
};

/** breadcrumb card (centred in a 200 x 200 canvas) */
export const drawCrumb = (p: Pen) => {
  p.ol = 7;
  p.poly([[40, 120], [70, 70], [140, 62], [168, 104], [150, 146], [70, 152]], "#d9a35a");
  p.poly([[62, 116], [84, 84], [134, 80], [150, 108], [136, 132], [80, 136]], "#f3d9a4", 0);
  for (const [x, y] of [[96, 100], [120, 112], [106, 124]] as P2[]) p.dot(x, y, 4, "#c48a3e");
  p.ol = 12;
};

/** "Z" for the snoring guard (200 x 200) */
export const drawZ = (p: Pen) => {
  p.ol = 0;
  p.line([[50, 50], [150, 50], [50, 150], [150, 150]], "#ffffff", 22);
  p.ol = 12;
};

/** soft additive glow (128 x 128): white centre to transparent */
export const drawGlow = (p: Pen) => {
  const g = p.g, gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, "rgba(255,240,200,0.9)"); gr.addColorStop(0.4, "rgba(255,220,150,0.35)"); gr.addColorStop(1, "rgba(255,200,120,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
};

/** window backdrop (512 x 640): night sky with a moon, or a warm morning sky with a sun */
export const drawSky = (g: CanvasRenderingContext2D, night: boolean) => {
  const gr = g.createLinearGradient(0, 0, 0, 640);
  if (night) { gr.addColorStop(0, "#0f1d3d"); gr.addColorStop(1, "#2d4f86"); } else { gr.addColorStop(0, "#9fd0ff"); gr.addColorStop(0.7, "#ffe2a8"); gr.addColorStop(1, "#ffc77a"); }
  g.fillStyle = gr; g.fillRect(0, 0, 512, 640);
  if (night) {
    g.fillStyle = "rgba(244,241,216,0.18)"; g.beginPath(); g.arc(340, 200, 120, 0, Math.PI * 2); g.fill();
    g.fillStyle = "#f4f1d8"; g.beginPath(); g.arc(340, 200, 64, 0, Math.PI * 2); g.fill();
    for (let i = 0; i < 40; i++) { g.fillStyle = "rgba(255,255,255,0.8)"; g.fillRect((i * 97) % 512, (i * 53) % 420, 4, 4); }
  } else {
    g.fillStyle = "rgba(255,255,255,0.9)"; g.beginPath(); g.arc(160, 230, 70, 0, Math.PI * 2); g.fill();
    g.fillStyle = "rgba(255,255,255,0.6)";
    for (const [x, y, s] of [[380, 160, 1], [120, 420, 0.8]]) { g.beginPath(); g.ellipse(x, y, 110 * s, 34 * s, 0, 0, Math.PI * 2); g.fill(); }
  }
};
