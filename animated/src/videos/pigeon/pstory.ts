// The Pigeon Escape: shot plan. Every shot starts on its narration line (SCENES from the Daniel narration) and every
// key action lands 2 frames before its word (KW). Cameras: smootherstep glides between keys, hard cuts where marked,
// and a slow creeping push-in on every hold.
import { SCENES, KW, TOTAL_S } from "./ptime";
export { KW };

export const FPS = 30;
export const TOTAL = Math.ceil(TOTAL_S * FPS) + 8;
export type V3 = [number, number, number];
export type Light = "morn" | "night" | "golden";
export const LEAD = 2 / FPS;
export const at = (w: keyof typeof KW) => KW[w] - LEAD;

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const t = clamp01(x); return t * t * t * (t * (t * 6 - 15) + 10); };
export const ease = (t: number, a: number, b: number) => smooth((t - a) / Math.max(1e-3, b - a));
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
export const lerp3 = (a: V3, b: V3, k: number): V3 => [lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp(a[2], b[2], k)];

const LIGHT: Light[] = ["morn", "morn", "morn", "morn", "morn", "morn", "night", "night", "morn", "morn", "morn", "morn", "golden"];
export const SHOTS = SCENES.map((s, i) => ({
  id: i + 1, t0: s, t1: i + 1 < SCENES.length ? SCENES[i + 1] : TOTAL / FPS,
  a: Math.round(s * FPS), b: i + 1 < SCENES.length ? Math.round(SCENES[i + 1] * FPS) : TOTAL, light: LIGHT[i],
}));
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];

// ---- the flock in the sky (shot 13) ----
export const FLOCK0: V3 = [992, 47, -18];
export const flockAt = (t: number): V3 => {
  const u = t - SCENES[12];
  return [FLOCK0[0] + 1.6 * u, FLOCK0[1] + 0.25 * Math.sin(u * 1.3), FLOCK0[2]];
};
export const PRISON: V3 = [1000, 0, -48];

// ---- cameras ----
export type Cam = { pos: V3; look: V3; fov: number; roll?: number };
type Key = { t: number; dur?: number; cut?: boolean; c: (t: number) => Cam };
const K = (t: number, c: Cam | ((t: number) => Cam), dur = 0.8, cut = false): Key => ({ t, dur, cut, c: typeof c === "function" ? c : () => c });

const CAMS: Key[][] = [
  // 1 hook: medium on the prisoner, punch in on "single breadcrumb"
  [K(0, { pos: [0.35, 1.55, 3.7], look: [-0.2, 1.35, 0.6], fov: 38 }), K(at("single") - 0.15, { pos: [0.05, 1.7, 2.15], look: [-0.15, 1.62, 0.6], fov: 34, roll: -0.04 }, 0.45)],
  // 2 morning routine: three-quarter view of the walk to the window
  [K(SCENES[1], { pos: [2.3, 1.45, 1.4], look: [-0.2, 1.2, -1.1], fov: 40 }), K(6.3, { pos: [1.7, 1.6, 0.2], look: [0.55, 1.5, -2.3], fov: 34 }, 1.0)],
  // 3 the first pigeon: close on the window from inside
  [K(SCENES[2], { pos: [0.35, 1.5, -1.05], look: [0.65, 1.72, -2.65], fov: 32 })],
  // 4 two, then a hard cut to the wide cell full of pigeons on "forty"
  [K(SCENES[3], { pos: [0.3, 1.5, -0.85], look: [0.68, 1.7, -2.65], fov: 34 }),
   K(at("forty") - 0.05, { pos: [1.75, 1.85, 2.3], look: [-0.25, 0.95, -0.7], fov: 46, roll: 0.03 }, 0, true)],
  // 5 guards seen from inside the cell, through the bars
  [K(SCENES[4], { pos: [-0.55, 1.5, 0.9], look: [1.1, 1.5, 4.1], fov: 40 })],
  // 6 the guards laugh: close, from the corridor
  [K(SCENES[5], { pos: [1.0, 1.62, 2.85], look: [1.1, 1.6, 4.2], fov: 36 }), K(at("laugh") - 0.1, { pos: [1.05, 1.66, 3.05], look: [1.1, 1.62, 4.2], fov: 33, roll: 0.03 }, 0.3)],
  // 7 night: the guard on his chair nods off
  [K(SCENES[6], { pos: [2.35, 1.35, 3.0], look: [3.45, 1.05, 5.25], fov: 38 }), K(at("asleep") - 0.2, { pos: [2.75, 1.25, 3.65], look: [3.45, 1.05, 5.25], fov: 34 }, 0.8)],
  // 8 night: strings to every bird, slow orbit
  [K(SCENES[7], { pos: [1.6, 1.45, 2.35], look: [-0.35, 0.8, -0.25], fov: 42 }), K(21.6, { pos: [-1.0, 1.75, 2.45], look: [-0.3, 0.85, -0.3], fov: 42 }, 2.4)],
  // 9 thirty days later: the warden marches down the corridor (camera pans with him)
  [K(SCENES[8], (t) => { const x = wardenX(t); return { pos: [x + 0.4, 1.5, 6.6], look: [x + 0.15, 1.3, 4.0], fov: 40 }; })],
  // 10 finds it empty: through the bars at the warden, punch in on "empty"
  [K(SCENES[9], { pos: [0.75, 1.55, 0.55], look: [1.1, 1.6, 3.2], fov: 38 }), K(at("empty") - 0.08, { pos: [0.95, 1.68, 1.75], look: [1.1, 1.7, 3.2], fov: 30, roll: -0.04 }, 0.25)],
  // 11 the bed is made, the blanket is gone
  [K(SCENES[10], { pos: [-0.35, 1.45, 0.75], look: [-1.5, 0.6, -1.25], fov: 40 }), K(at("blanket") - 0.1, { pos: [-0.75, 1.25, 0.1], look: [-1.5, 0.58, -1.2], fov: 36 }, 0.9)],
  // 12 one last breadcrumb on the pillow
  [K(SCENES[11], { pos: [-0.95, 1.2, -0.85], look: [-1.48, 0.7, -2.08], fov: 34 }), K(at("breadcrumb2") - 0.3, { pos: [-1.2, 1.02, -1.4], look: [-1.48, 0.7, -2.08], fov: 30 }, 0.7)],
  // 13 above the prison: look down at the prison, tilt up to the flock, pull wide across the sky
  [K(SCENES[12], (t) => { const F = flockAt(t); return { pos: [F[0] + 3, F[1] + 4, F[2] + 26], look: [PRISON[0], 2, PRISON[2]], fov: 44 }; }),
   K(36.7, (t) => { const F = flockAt(t); return { pos: [F[0] + 1.2, F[1] - 1.2, F[2] + 9.5], look: [F[0], F[1] - 1.7, F[2]], fov: 42 }; }, 1.4),
   K(at("sky") - 0.2, (t) => { const F = flockAt(t); return { pos: [F[0] - 3, F[1] + 1.5, F[2] + 21], look: [F[0] + 1.5, F[1] - 3, F[2]], fov: 46, roll: 0.03 }; }, 1.6)],
];

/** creeping push-in on every hold: the lens moves toward the look point by `rate` of the distance per second */
const CREEP = 0.05;
export const camAt = (f: number): Cam => {
  const t = f / FPS, s = shotAt(f), keys = CAMS[s.id - 1];
  let i = 0;
  for (let k = 0; k < keys.length; k++) if (t >= keys[k].t) i = k;
  let c = keys[i].c(t);
  if (i > 0 && !keys[i].cut) {
    const k = smooth((t - keys[i].t) / (keys[i].dur ?? 0.8)), p = keys[i - 1].c(t);
    c = { pos: lerp3(p.pos, c.pos, k), look: lerp3(p.look, c.look, k), fov: lerp(p.fov, c.fov, k), roll: lerp(p.roll ?? 0, c.roll ?? 0, k) };
  }
  const hold = t - keys[i].t, d = Math.min(0.12, CREEP * hold);
  return { ...c, pos: lerp3(c.pos, c.look, d) };
};

// ---- character paths ----
/** shot 9: the warden marches from the far end of the corridor to the cell door */
export const wardenX = (t: number) => lerp(-4.8, 0.95, ease(t, KW.warden - 0.6, KW.cell - 0.1));
/** shot 2: prisoner walks from mid-cell to the window */
export const P_WALK: [V3, V3] = [[-1.0, 0, 0.1], [0.45, 0, -1.95]];
export const walkK = (t: number) => clamp01((t - 4.35) / 2.0);

/** the forty pigeons: home spots in the cell (shots 4-6), deterministic */
const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
export const CELL_SPOTS: { p: V3; mirror: boolean; ph: number }[] = Array.from({ length: 40 }, (_, i) => {
  if (i === 0) return { p: [0.5, 1.55, -2.68], mirror: false, ph: 0 };          // first pigeon on the sill
  if (i === 1) return { p: [0.86, 1.55, -2.66], mirror: true, ph: 0.4 };        // second pigeon on the sill
  if (i === 2) return { p: [-0.32, 2.02, 0.62], mirror: false, ph: 0.2 };       // on the prisoner's head
  if (i < 9) return { p: [-1.85 + 0.13 * (i - 3), 0.62, -1.9 + 0.3 * (i - 3)], mirror: i % 2 === 0, ph: hh(i, 2) }; // on the bunk
  const a = hh(i, 1) * Math.PI * 2, r = 0.55 + hh(i, 3) * 1.25;
  return { p: [Math.max(-1.75, Math.min(1.75, -0.2 + Math.cos(a) * r)), 0.0, Math.max(-2.2, Math.min(2.2, 0.4 + Math.sin(a) * r * 0.9))], mirror: hh(i, 4) > 0.5, ph: hh(i, 5) };
});
/** when each of the forty lands (shot 4 "forty" burst) */
export const landT = (i: number) => (i === 0 ? at("pigeon") : i === 1 ? at("two") : at("forty") - 0.25 + 0.6 * hh(i, 6));
export const WINDOW: V3 = [0.65, 1.95, -2.7];
/** flock offsets above the man in the sky (shot 13) */
export const FLOCK_SPOTS: V3[] = Array.from({ length: 40 }, (_, i) => [(hh(i, 7) - 0.5) * 4.6, 0.3 + hh(i, 8) * 1.7, (hh(i, 9) - 0.5) * 2.2]);
/** shot 8: the pigeons ring the prisoner on the cell floor; strings appear one by one */
export const RING_SPOTS: V3[] = Array.from({ length: 40 }, (_, i) => {
  const a = (i / 40) * Math.PI * 2 + hh(i, 10) * 0.2, r = 0.85 + (i % 3) * 0.32;
  return [Math.max(-1.8, Math.min(1.8, -0.3 + Math.cos(a) * r)), 0, Math.max(-2.2, Math.min(2.2, 0.15 + Math.sin(a) * r * 0.8))];
});
export const stringsK = (t: number) => clamp01((t - at("ties")) / (KW.bird - KW.ties));
