// The Pigeon Escape world: one prison cell + corridor set, and a sky set over a small prison far away.
// Same look rules as the bridge engine: two-tone world materials (shade.ts), painted textures (paint.ts), lit
// camera-facing character cards (cast.ts Actor + cardShade), unlit ink effect cards (Fx) on the NOINK layer.
import * as THREE from "three";
import { Pen, bodyFront, bodySide, fxBurst, fxCloud, fxContact, Expr, Outfit } from "../bridge/toon";
import { Pool, Actor, Fx } from "../bridge/cast";
import { lam, boxGeo, Batch, V } from "../bridge/build";
import { stoneHD, planksHD, cloudHD, grassHD, roofHD, CLOUD_GOLD, ctex } from "../bridge/paint";
import { TONE, CHAR } from "../bridge/shade";
import { LIGHTS, LOOK } from "../bridge/lights";
import { NOINK } from "../bridge/ink";
import { wallTex, floorTex, rustTex, vineTex, tallyTex, webTex, puddleTex, signTex, buildBay } from "./pdetail";
import { INMATES, haTex, plateTex } from "./pextra";
import { PRISONER, GUARD_A, GUARD_B, WARDEN, drawPigeon, drawCrumb, drawZ, drawGlow, drawSky } from "./ptoon";
import {
  FPS, KW, V3, Light, SHOTS, shotAt, camAt, at, ease, smooth, clamp01, lerp, lerp3, wardenX, P_WALK, walkK, CELL_SPOTS, landT, WINDOW,
  FLOCK_SPOTS, RING_SPOTS, stringsK, flockAt, PRISON,
} from "./pstory";

type C3 = [number, number, number];
type Preset = typeof LIGHTS.day & { sunDir: C3; skyC: string[]; skyE: number[] };
const PRESETS: Record<Light, Preset> = {
  morn: { ...LIGHTS.day, lit: [1.45, 1.33, 1.12], shade: [0.5, 0.47, 0.6], lift: [0.05, 0.05, 0.09], term: 0.2,
    charTint: [1.0, 0.95, 0.9], fog: "#b8d0ec", fogNear: 40, fogFar: 300, sunDir: [0.32, 0.8, -0.5], skyC: LOOK.day.sky.c, skyE: LOOK.day.sky.e },
  night: { ...LIGHTS.day, lit: [0.5, 0.6, 0.95], shade: [0.14, 0.16, 0.3], lift: [0.03, 0.04, 0.09], term: 0.2,
    charTint: [0.6, 0.68, 1.0], charShade: 0.84, sideTint: [0.8, 0.85, 1.0], fog: "#16224a", fogNear: 40, fogFar: 300, sunDir: [0.32, 0.8, -0.5],
    skyC: ["#2d4f86", "#22406f", "#1a3360", "#142850", "#0f1d3d"], skyE: [0, 3, 8, 16, 40] },
  golden: { ...LIGHTS.golden, actorShadow: false, sunDir: [-0.42, 0.3, 0.86], skyC: LOOK.golden.sky.c, skyE: LOOK.golden.sky.e, fogNear: 180, fogFar: 1400 },
};
const srgb = (hex: string, out: THREE.Color) => out.set(hex).convertLinearToSRGB();

const tier = (d: number): [number, number, number] => (d < 2.2 ? [1800, 3000, 3.0] : d < 4.5 ? [1080, 1800, 1.8] : d < 12 ? [600, 1000, 1.0] : [300, 500, 0.5]);
const q = (v: number, n = 12) => Math.round(v * n) / n;
const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
/** blinks: closed for 3 frames every 1.6-3.0 s, different per character */
const blinkAt = (t: number, seed: number) => { const P = 1.6 + 1.4 * hh(seed, 11), u = (t + hh(seed, 12) * P) % P; return u < 0.1; };

type Card = { key: string; draw: (p: Pen) => void; at: V3; scale?: number; mirror?: boolean; roll?: number; big?: boolean };
type FxCard = { key: string; cw: number; ch: number; draw: (p: Pen) => void; at: V3; w: number; h: number; flat?: boolean; rot?: number; soft?: boolean };

export class PWorld {
  root = new THREE.Group();
  private pool = new Pool();
  private actors: Actor[] = [];
  private fxs: Fx[] = [];
  private sun: THREE.DirectionalLight; private hemi: THREE.HemisphereLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#b8d0ec", 40, 300);
  private winSky: THREE.MeshBasicMaterial; private winDay: THREE.Texture; private winNight: THREE.Texture;
  private blanket: THREE.Mesh; private door = new THREE.Group();
  private strings: THREE.Mesh[] = []; private strMat = new THREE.MeshBasicMaterial({ color: "#cfc8b8" });
  private glow: THREE.Sprite;
  private clouds: THREE.Mesh[] = [];
  private counter!: THREE.Mesh; private count0!: THREE.Texture; private countA!: THREE.Texture;
  private v = new THREE.Vector3();

  constructor() {
    const R = this.root;
    // ---- sky dome (5 stops by elevation; written straight as display colours, the shader is not tone mapped) ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() }, c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el)); c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el)); c = mix(c, c4, smoothstep(e.z, e.w, el));
          gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(1100, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK);
    R.add(this.sky);
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 0.5);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6);
    this.sun.castShadow = true; this.sun.shadow.mapSize.set(2048, 2048);
    R.add(this.hemi, this.sun, this.sun.target);

    // ---- materials ----
    const wall = lam("pg_wallD", () => ({ map: wallTex("pg_wallT", ["#a9a093", "#9e9586", "#b3aa9d", "#968d80"], "#6f675d", 0.35) }));
    const wallDark = lam("pg_wallD2", () => ({ map: wallTex("pg_wallT2", ["#8c847b", "#817a72", "#968e85", "#7a736b"], "#5a544e", 0.45) }));
    const floor = lam("pg_floorD", () => ({ map: floorTex() }));
    const wood = lam("pg_wood", () => ({ map: planksHD() }));
    const iron = lam("pg_rust", () => ({ map: rustTex() }));
    const mattress = lam("pg_mattress", () => ({ map: ctex("pg_ticking", 256, 256, (g) => { g.fillStyle = "#ece6d8"; g.fillRect(0, 0, 256, 256); g.fillStyle = "#6f86b8"; for (let x = 8; x < 256; x += 32) g.fillRect(x, 0, 9, 256); g.fillStyle = "#9fb0d4"; for (let x = 22; x < 256; x += 32) g.fillRect(x, 0, 3, 256); }) }));
    const pillow = lam("pg_pillow", () => ({ color: "#f3efe6" }));
    const red = lam("pg_blanket", () => ({ color: "#c0353a" }));
    const desk = lam("pg_desk", () => ({ color: "#8a5a3c" }));
    const b = new Batch();
    const box = (m: THREE.Material, x0: number, y0: number, z0: number, x1: number, y1: number, z1: number, tile = 2.0) => b.add(boxGeo(V(x0, y0, z0), V(x1, y1, z1), tile), m);

    // ---- cell (x -2..2, z -2.5..2.5) + corridor (z 2.5..7.2) ----
    box(floor, -6.5, -0.2, -3.2, 6.5, 0, 7.6, 2.0);
    // back wall with the window hole (x 0.25..1.05, y 1.55..2.35)
    box(wall, -2.3, 0, -2.9, 0.25, 4.2, -2.5); box(wall, 1.05, 0, -2.9, 2.3, 4.2, -2.5);
    box(wall, 0.25, 0, -2.9, 1.05, 1.55, -2.5); box(wall, 0.25, 2.35, -2.9, 1.05, 4.2, -2.5);
    // side walls of the cell
    box(wall, -2.3, 0, -2.9, -2.0, 4.2, 2.5); box(wall, 2.0, 0, -2.9, 2.3, 4.2, 2.5);
    // front: neighbouring cells' walls left/right of the bars, a lintel above the bars
    box(wallDark, -6.5, 3.2, 2.5, 6.5, 4.2, 2.8); // lintel over the whole cell row
    for (const x of [-6.5, -2.3, 2.0, 6.2]) box(wallDark, x, 0, 2.5, x + 0.3, 3.2, 2.8); // pillars between cells
    // neighbour cells left and right: back walls, outer walls, bunks, bars
    box(wall, -6.5, 0, -2.9, -2.3, 4.2, -2.5); box(wall, 2.3, 0, -2.9, 6.5, 4.2, -2.5);
    box(wall, -6.8, 0, -2.9, -6.5, 4.2, 2.8); box(wall, 6.5, 0, -2.9, 6.8, 4.2, 2.8);
    for (const x0 of [-6.3, 5.4]) { box(wood, x0, 0, -2.4, x0 + 0.9, 0.42, -0.4, 0.8); box(mattress, x0 + 0.03, 0.42, -2.36, x0 + 0.87, 0.56, -0.44, 0); }
    // corridor: far wall and the two ends
    // the far side of the block: two tiers of cells behind bars, a catwalk with a railing
    box(floor, -6.5, -0.2, 7.6, 6.5, 0, 10.9, 2.0);
    box(wallDark, -6.8, 0, 2.5, -6.5, 8.2, 10.9); box(wallDark, 6.5, 0, 2.5, 6.8, 8.2, 10.9); box(wallDark, -6.5, 0, 10.5, 6.5, 8.2, 10.9);
    for (const x of [-6.5, -3.4, -0.15, 3.1, 6.2]) box(wallDark, x, 0, 7.2, x + 0.3, 8.2, 10.5); // dividers
    box(wallDark, -6.5, 3.2, 7.2, 6.5, 4.4, 7.5); box(wallDark, -6.5, 7.4, 7.2, 6.5, 8.2, 7.5); // lintels
    box(floor, -6.5, 4.2, 6.1, 6.5, 4.4, 10.5, 2.0); // catwalk + upper floor
    for (let x = -6.3; x < 6.4; x += 0.9) box(iron, x, 4.4, 6.12, x + 0.05, 5.35, 6.17, 0);
    box(iron, -6.5, 5.3, 6.1, 6.5, 5.38, 6.2, 0); box(iron, -6.5, 4.85, 6.12, 6.5, 4.9, 6.17, 0);
    for (let x = -6.2; x < 6.3; x += 0.2) { if (Math.abs(x + 0.0) < 0.2 || Math.abs(x + 3.25) < 0.2 || Math.abs(x - 3.25) < 0.2) continue;
      b.add(new THREE.CylinderGeometry(0.024, 0.024, 3.2, 8).translate(x, 1.6, 7.3), iron); b.add(new THREE.CylinderGeometry(0.024, 0.024, 3.0, 8).translate(x, 5.9, 7.3), iron); }
    for (const x0 of [-6.2, -3.0, 0.3, 3.5]) { box(wood, x0, 0, 9.6, x0 + 1.8, 0.42, 10.45, 0.8); box(mattress, x0 + 0.03, 0.42, 9.65, x0 + 1.77, 0.56, 10.4, 0); }
    // neighbour-cell bars on our side
    for (let x = -6.15; x < -2.35; x += 0.2) b.add(new THREE.CylinderGeometry(0.024, 0.024, 3.2, 8).translate(x, 1.6, 2.62), iron);
    for (let x = 2.45; x < 6.2; x += 0.2) b.add(new THREE.CylinderGeometry(0.024, 0.024, 3.2, 8).translate(x, 1.6, 2.62), iron);
    // security camera and caged wall lamps
    box(iron, 6.1, 3.5, 3.0, 6.5, 3.62, 3.12, 0); box(iron, 5.75, 3.38, 2.95, 6.15, 3.6, 3.2, 0);
    // the guard's desk clutter: mug, donut box, newspaper
    b.add(new THREE.CylinderGeometry(0.045, 0.04, 0.11, 12).translate(4.35, 0.835, 5.6), lam("pg_mug", () => ({ color: "#e9e4da" })));
    box(lam("pg_donutBox", () => ({ color: "#f2b7c6" })), 4.55, 0.78, 5.55, 4.95, 0.86, 5.95, 0);
    b.add(new THREE.TorusGeometry(0.06, 0.028, 8, 16).rotateX(Math.PI / 2).translate(4.75, 0.89, 5.75), lam("pg_donut", () => ({ color: "#d77a9a" })));
    box(lam("pg_paper", () => ({ color: "#ddd8cc" })), 4.15, 0.78, 5.85, 4.5, 0.795, 6.08, 0);
    // bunk: frame, mattress, pillow (the blanket is its own mesh: it disappears)
    box(wood, -1.98, 0, -2.42, -1.02, 0.42, -0.35, 0.8); box(mattress, -1.95, 0.42, -2.38, -1.05, 0.56, -0.4, 0);
    box(pillow, -1.85, 0.56, -2.32, -1.15, 0.66, -1.95, 0);
    // window bars + bar band
    for (const x of [0.45, 0.65, 0.85]) b.add(new THREE.CylinderGeometry(0.018, 0.018, 0.8, 8).translate(x, 1.95, -2.62), iron);
    // cell front bars (fixed part) x -2..0.6 and the door (0.6..1.6) as its own group; the rest x 1.6..2
    const bar = (g: THREE.BufferGeometry[], x: number) => g.push(new THREE.CylinderGeometry(0.026, 0.026, 3.2, 8).translate(x, 1.6, 2.62));
    const fixed: THREE.BufferGeometry[] = [];
    for (let x = -1.9; x < 0.55; x += 0.2) bar(fixed, x);
    for (let x = 1.7; x < 2.0; x += 0.2) bar(fixed, x);
    for (const g of fixed) b.add(g, iron);
    box(iron, -2.0, 0.08, 2.58, 0.6, 0.16, 2.66, 0); box(iron, -2.0, 2.2, 2.58, 0.6, 2.28, 2.66, 0);
    box(iron, 1.6, 0.08, 2.58, 2.0, 0.16, 2.66, 0); box(iron, 1.6, 2.2, 2.58, 2.0, 2.28, 2.66, 0);
    // guard desk + chair in the corridor
    box(desk, 4.1, 0, 5.4, 5.1, 0.78, 6.1, 0); box(desk, 3.15, 0, 5.15, 3.75, 0.46, 5.7, 0); box(desk, 3.15, 0.46, 5.62, 3.75, 1.15, 5.72, 0);
    // rusty pipes along the corridor's far wall, a bucket and a hanging bulb in the cell
    for (const y of [3.55, 3.75]) b.add(new THREE.CylinderGeometry(0.06, 0.06, 13, 10).rotateZ(Math.PI / 2).translate(0, y, 7.1), iron);
    b.add(new THREE.CylinderGeometry(0.06, 0.06, 3.6, 10).translate(-3.2, 1.8, 7.1), iron);
    b.add(new THREE.CylinderGeometry(0.17, 0.13, 0.32, 14).translate(1.6, 0.16, -2.1), iron);
    b.add(new THREE.CylinderGeometry(0.008, 0.008, 1.2, 5).translate(0.2, 3.6, 0.2), iron);
    // wall chains with shackles next to the bunk
    for (const cz of [-0.25, 0.25]) for (let k = 0; k < 9; k++) {
      const tg = new THREE.TorusGeometry(0.035, 0.011, 6, 12); if (k % 2) tg.rotateY(Math.PI / 2);
      b.add(tg.translate(-1.97, 1.75 - k * 0.062, cz), iron);
    }
    const roof = lam("pg_roof", () => ({ map: roofHD("#5a5f6e", true) }));
    b.build(R);
    buildBay(R, wall, roof, PRISON);
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 8), new THREE.MeshBasicMaterial({ color: "#fff1b8" })); bulb.position.set(0.2, 2.95, 0.2); bulb.layers.set(NOINK); R.add(bulb);

    // the blanket (vanishes string by string in shot 8)
    this.blanket = new THREE.Mesh(boxGeo(V(-0.5, 0, -1), V(0.5, 0.07, 1), 0), red);
    this.blanket.position.set(-1.5, 0.56, -1.3); this.blanket.scale.set(0.98, 1, 0.92);
    this.blanket.castShadow = true; this.blanket.receiveShadow = true; R.add(this.blanket);
    // the cell door (hinged at x 0.6)
    const dg: THREE.BufferGeometry[] = [];
    for (let x = 0.7; x < 1.6; x += 0.2) dg.push(new THREE.CylinderGeometry(0.026, 0.026, 3.2, 8).translate(x - 0.6, 1.6, 0));
    dg.push(boxGeo(V(0, 0.08, -0.04), V(1.0, 0.16, 0.04), 0), boxGeo(V(0, 2.2, -0.04), V(1.0, 2.28, 0.04), 0), boxGeo(V(0.9, 1.0, -0.06), V(1.0, 1.25, 0.06), 0));
    for (const g of dg) { const m = new THREE.Mesh(g, iron); m.castShadow = m.receiveShadow = true; this.door.add(m); }
    this.door.position.set(0.6, 0, 2.62); R.add(this.door);
    // what the window looks out on (day / night painted sky)
    this.winDay = ctex("pg_winDay", 512, 640, (g) => drawSky(g, false));
    this.winNight = ctex("pg_winNight", 512, 640, (g) => drawSky(g, true));
    this.winSky = new THREE.MeshBasicMaterial({ map: this.winDay, fog: false });
    const ws = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 3.0), this.winSky);
    ws.position.set(0.65, 2.0, -3.6); ws.layers.set(NOINK); R.add(ws);
    // the guard's lantern glow (night)
    this.glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: ctex("pg_glow", 128, 128, (g) => drawGlow(new Pen(g))), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
    this.glow.position.set(4.5, 1.05, 5.75); this.glow.scale.set(2.4, 2.4, 1); this.glow.layers.set(NOINK); R.add(this.glow);
    // strings (thin unlit tubes, re-aimed every frame)
    const sg = new THREE.CylinderGeometry(1, 1, 1, 5).translate(0, 0.5, 0);
    for (let i = 0; i < 40; i++) { const m = new THREE.Mesh(sg, this.strMat); m.visible = false; m.layers.set(NOINK); this.strings.push(m); R.add(m); }
    // ---- decals: vines, tally marks, cobwebs, puddles, signs ----
    const decal = (key: string, map: THREE.Texture, w: number, h: number, x: number, y: number, z: number, ry: number, flat = false) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), lam(key, () => ({ map, alphaTest: 0.4, side: THREE.DoubleSide })));
      m.position.set(x, y, z); if (flat) m.rotation.set(-Math.PI / 2, 0, ry); else m.rotation.y = ry; m.receiveShadow = true; R.add(m); return m;
    };
    const V0 = vineTex(1), V1 = vineTex(2), V2 = vineTex(3);
    decal("pg_v1", V0, 1.6, 3.2, -1.2, 2.6, -2.49, 0); decal("pg_v2", V1, 1.2, 2.4, 0.65, 3.0, -2.49, 0); decal("pg_v3", V2, 1.4, 2.8, 1.5, 2.8, -2.49, 0);
    decal("pg_v4", V1, 1.6, 3.2, -1.99, 2.6, 1.4, Math.PI / 2); decal("pg_v5", V2, 1.6, 3.2, 1.99, 2.6, -1.2, -Math.PI / 2); decal("pg_v6", V0, 1.4, 2.8, 1.99, 2.8, 1.6, -Math.PI / 2);
    decal("pg_v7", V0, 2.0, 2.2, -0.6, 3.1, 2.49, 0); decal("pg_v8", V2, 2.0, 2.2, 1.4, 3.1, 2.49, 0);
    decal("pg_v9", V1, 2.0, 4.0, -4.5, 6.2, 7.19, Math.PI); decal("pg_v10", V0, 2.0, 4.0, 3.2, 6.2, 7.19, Math.PI); decal("pg_v13", V2, 1.6, 3.6, -6.49, 5.0, 5.0, Math.PI / 2); decal("pg_v11", V2, 1.6, 3.2, -2.6, 2.6, 2.81, 0); decal("pg_v12", V1, 1.6, 3.2, 3.4, 2.6, 2.81, 0);
    decal("pg_tallyM", tallyTex(), 1.1, 1.1, -1.99, 1.25, -1.0, Math.PI / 2);
    for (const [x, z, ry] of [[-1.98, -2.48, 0], [1.98, -2.48, -Math.PI / 2]] as const) decal("pg_webM", webTex(), 0.7, 0.7, x + (ry ? -0.0 : 0.35), 3.2, z + (ry ? 0.35 : 0), ry);
    for (const [x, z, s] of [[0.9, 0.9, 0.9], [-0.9, 1.9, 0.6], [2.6, 4.8, 1.1], [-2.0, 5.6, 0.8]] as const) decal("pg_puddleM", puddleTex(), s, s * 0.7, x, 0.006, z, 0.4, true);
    decal("pg_noPets", signTex("pg_noPetsT", [["NO", 70], ["PETS", 70]], true), 1.0, 0.62, 0.35, 3.8, 7.19, Math.PI);
    decal("pg_plate13", plateTex("C-13"), 0.5, 0.2, 1.1, 3.55, 2.81, 0);
    ["C-21", "C-22", "C-23", "C-24"].forEach((n, i) => decal("pg_plate" + n, plateTex(n), 0.5, 0.2, -4.9 + i * 3.25, 3.0, 7.19, Math.PI));
    decal("pg_plate12", plateTex("C-12"), 0.5, 0.2, -4.3, 3.55, 2.81, 0); decal("pg_plate14", plateTex("C-14"), 0.5, 0.2, 4.3, 3.55, 2.81, 0);
    const yl = new THREE.Mesh(new THREE.PlaneGeometry(13, 0.09), lam("pg_yline", () => ({ color: "#e8c23a" }))); yl.rotation.x = -Math.PI / 2; yl.position.set(0, 0.007, 3.15); yl.receiveShadow = true; R.add(yl);
    for (const [x, z, ry] of [[-3.0, 2.81, 0], [3.0, 2.81, 0], [-1.8, 7.19, Math.PI], [1.4, 7.19, Math.PI]] as const) {
      const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), new THREE.MeshBasicMaterial({ color: "#ffe7a8" })); lamp.position.set(x, 3.0, z + (ry ? -0.08 : 0.08)); lamp.layers.set(NOINK); R.add(lamp);
    }
    this.counter = decal("pg_countA", signTex("pg_countAT", [["DAYS WITHOUT", 40], ["AN ESCAPE", 40], ["2431", 96]]), 1.0, 0.62, 1.95, 3.8, 7.19, Math.PI);
    this.count0 = signTex("pg_count0T", [["DAYS WITHOUT", 40], ["AN ESCAPE", 40], ["0", 110]]);
    this.countA = (this.counter.material as THREE.MeshLambertMaterial).map!;
    // sky set clouds around the flock's path
    const cm = [0, 1, 2, 3].map((k) => cloudHD(k + 10, CLOUD_GOLD));
    for (let i = 0; i < 16; i++) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: cm[i % 4], transparent: true, depthWrite: false, fog: true }));
      const w = 14 + hh(i, 20) * 22;
      m.position.set(940 + hh(i, 21) * 130, 70 + hh(i, 22) * 45, -150 + hh(i, 23) * 50);
      if (i < 3) m.position.set(1010 + i * 25, 100 + i * 8, -60 - i * 10); // mid-distance ones for parallax
      m.scale.set(w, w / 2, 1); m.layers.set(NOINK); this.clouds.push(m); R.add(m);
    }
  }

  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  update(f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = shotAt(f), id = s.id, L = PRESETS[s.light];
    // ---- camera ----
    const c = camAt(f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll ?? 0);
    cam.fov = c.fov; cam.near = 0.05; cam.far = 1500; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    cam.layers.enable(NOINK);
    const focus = V(...c.look);
    // ---- light: fixed world sun per preset (through the cell window), two-tone + card uniforms ----
    const sunDir = V(...L.sunDir).normalize();
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    const R = id === 13 ? 40 : 10, ctr = id === 13 ? focus : V(0, 1, 2);
    this.sun.position.copy(ctr).addScaledVector(sunDir, 60); this.sun.target.position.copy(ctr);
    const sc = this.sun.shadow.camera; sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = 1; sc.far = 140; sc.updateProjectionMatrix();
    this.sun.shadow.bias = -0.0004; this.sun.shadow.normalBias = 0.02;
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term;
    TONE.uBounce.value.set(...(s.light === "golden" ? LOOK.golden.bounce : LOOK.day.bounce)); TONE.uSat.value = 1.05;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad;
    CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    const su = this.skyMat.uniforms;
    L.skyC.forEach((h, i) => srgb(h, su["c" + i].value));
    const e = L.skyE.map((d) => THREE.MathUtils.degToRad(d)); su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    this.fog.color.set(L.fog); this.fog.near = L.fogNear; this.fog.far = L.fogFar; scene.fog = this.fog; scene.background = null;
    this.winSky.map = s.light === "night" ? this.winNight : this.winDay;
    this.glow.visible = s.light === "night";
    for (const m of this.clouds) m.lookAt(cam.position);
    // canvas angle the key light comes FROM on a camera-facing card
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const light2D = (mirror: boolean) => Math.round(Math.atan2(-sunDir.y, sunDir.dot(right) * (mirror ? -1 : 1)) / (Math.PI / 4)) * (Math.PI / 4);

    // ---- set dressing per shot ----
    this.blanket.visible = id <= 8;
    const bk = id === 8 ? 1 - 0.85 * stringsK(t) : 1;
    this.blanket.scale.set(0.98 * Math.max(0.15, bk), 1, 0.92 * Math.max(0.15, bk));
    (this.counter.material as THREE.MeshLambertMaterial).map = id >= 10 && t > at("empty") ? this.count0 : this.countA;
    this.door.rotation.y = id === 10 ? -1.25 * ease(t, KW.finds - 0.45, KW.finds + 0.25) : 0;

    // ---- cast ----
    const cards: Card[] = [], fxc: FxCard[] = [];
    const person = (name: string, o: Outfit, x: number, z: number, expr: Expr, opts: { mode?: "stand" | "march" | "sit" | "stroll"; side?: boolean; mirror?: boolean; phase?: number; wave?: number; tilt?: number; headTilt?: number; y?: number; seed: number; blink?: boolean; look?: number; roll?: number; scale?: number }) => {
      const mirror = !!opts.mirror, light = light2D(mirror), bl = opts.blink ?? blinkAt(t, opts.seed);
      const ph = q(opts.phase ?? 0, 24), wv = opts.wave === undefined ? undefined : q(opts.wave, 8);
      const key = `${name}|${expr}|${opts.mode ?? "stand"}|${opts.side ? 1 : 0}|${ph}|${wv}|${q(opts.tilt ?? 0, 2)}|${q(opts.headTilt ?? 0, 2)}|${bl ? 1 : 0}|${light.toFixed(2)}|${opts.look ?? 0}`;
      const draw = opts.side
        ? (p: Pen) => bodySide(p, o, { phase: ph, expr, mode: opts.mode === "march" ? "march" : "stand", blink: bl, light, seed: opts.seed })
        : (p: Pen) => bodyFront(p, o, { phase: ph, expr, mode: opts.mode ?? "stand", blink: bl, light, seed: opts.seed, wave: wv, tilt: opts.tilt, headTilt: opts.headTilt, look: opts.look, facing: 0 });
      cards.push({ key, draw, at: [x, opts.y ?? 0, z], mirror, roll: opts.roll, big: true, scale: opts.scale });
      if ((opts.y ?? 0) < 0.05) fxc.push({ key: "blob|contact|#6a6470", cw: 128, ch: 128, draw: (p) => fxContact(p, "#6a6470"), at: [x, 0.012, z], w: 0.9, h: 0.6, flat: true });
    };
    const pigeon = (i: number, x: number, y: number, z: number, mirror: boolean, flap: number, peck: number, fly: boolean, tired = false, scale = 0.7) => {
      const fq = q(flap, 4), pq = q(peck, 4);
      cards.push({ key: `pigeon|${fq}|${pq}|${fly ? 1 : 0}|${tired ? 1 : 0}`, draw: (p) => drawPigeon(p, fq, pq, fly, tired), at: [x, y, z], mirror, scale });
    };
    const crumb = (x: number, y: number, z: number, w = 0.09, flat = true) => fxc.push({ key: "crumb", cw: 200, ch: 200, draw: drawCrumb, at: [x, y, z], w, h: w, flat });
    const burst = (x: number, y: number, z: number, t0: number, size = 0.5) => {
      const u = (t - t0) / 0.45;
      if (u > 0 && u < 1) fxc.push({ key: `burst${q(u, 15)}`, cw: 512, ch: 512, draw: (p) => { p.g.scale(512 / 600, 512 / 600); fxBurst(p, q(u, 15)); }, at: [x, y, z], w: size, h: size });
    };
    const flapAt = (ph: number, rate = 3.2) => Math.sin((t * rate + ph) * Math.PI * 2);
    const pigeonsInCell = (n: number) => {
      for (let i = 0; i < n; i++) {
        const sp = CELL_SPOTS[i], tl = landT(i);
        if (t < tl - 0.45) continue;
        const k = clamp01((t - (tl - 0.45)) / 0.45);
        if (k < 1) { // flying in from the window on an arc
          const pos = lerp3(WINDOW, sp.p, smooth(k)); pos[1] += Math.sin(Math.PI * k) * 0.5;
          pigeon(i, pos[0], pos[1], pos[2], sp.mirror, flapAt(sp.ph, 4.5), 0, true);
        } else {
          const pk = Math.max(0, Math.sin((t * 1.3 + sp.ph) * Math.PI * 2)) ** 6;
          pigeon(i, sp.p[0], sp.p[1], sp.p[2], sp.mirror, -0.15, pk, false);
        }
      }
    };
    const PX = -0.3, PZ = 0.6; // the prisoner's spot
    /** the rest of the block: inmates in the neighbouring and opposite cells */
    const inmates = (expr: Expr, laughing: boolean, react = false) => {
      INMATES.forEach((m, i) => {
        const bob = laughing ? Math.sin(t * 20 + i) * 3 : 0;
        person("inm" + i, m.o, m.x, m.z, react && i % 2 ? "shock" : expr, { seed: 20 + i, tilt: bob, headTilt: laughing ? (i % 2 ? 7 : -7) : 0, wave: laughing && i % 2 === 0 ? q(0.5 + 0.5 * Math.sin(t * 9 + i), 4) : undefined });
        if (laughing) {
          const u = ((t - at("laugh")) * 1.3 + i * 0.37) % 1, k = (i + Math.floor((t - at("laugh")) * 1.3 + i * 0.37)) % 3;
          fxc.push({ key: "ha" + k, cw: 512, ch: 256, draw: (p) => haTex(p, k), at: [m.x + 0.25 * Math.sin(i * 2.1), 2.05 + 0.5 * u, m.z - 0.3], w: 0.75, h: 0.375 });
        }
      });
      if (laughing) for (const [gx, gz, j] of [[0.55, 4.3, 0], [1.55, 4.5, 1]] as const) {
        const u = ((t - at("laugh")) * 1.5 + j * 0.5) % 1;
        fxc.push({ key: "ha" + ((j + Math.floor((t - at("laugh")) * 1.5)) % 3), cw: 512, ch: 256, draw: (p) => haTex(p, (j + Math.floor((t - at("laugh")) * 1.5)) % 3), at: [gx, 2.15 + 0.45 * u, gz - 0.2], w: 0.6, h: 0.3 });
      }
    };

    if (id === 1 || id === 4) inmates("neutral", false);
    if (id === 1) {
      const wv = ease(t, at("single") - 0.5, at("single"));
      person("pris", PRISONER, PX, PZ, t > at("single") - 0.4 ? "grin" : "smile", { seed: 3, wave: wv > 0.02 ? wv : undefined });
      const hx = PX + right.x * 0.34, hz = PZ + right.z * 0.34;
      if (wv > 0.5) crumb(hx, 1.6 + 0.03 * Math.sin(t * 3), hz, 0.12, false);
      burst(hx, 1.6, hz, at("breadcrumb1"), 0.5);
    } else if (id === 2) {
      const k = walkK(t), p = lerp3(P_WALK[0], P_WALK[1], k), walking = k > 0 && k < 1;
      const dx = walking || k === 0 ? P_WALK[1][0] - P_WALK[0][0] : -1, dz = walking || k === 0 ? P_WALK[1][2] - P_WALK[0][2] : -0.25;
      person("pris", PRISONER, p[0], p[2], t > at("leaves") - 0.4 ? "grin" : "smile", { seed: 3, side: true, mode: walking ? "march" : "stand", phase: walking ? (t * 1.7) % 1 : 0, mirror: dx * right.x + dz * right.z < 0 });
      if (t > at("leaves")) crumb(0.7, 1.556, -2.62);
      burst(0.7, 1.62, -2.6, at("leaves"), 0.35);
    } else if (id === 3 || id === 4) {
      if (t > at("leaves")) crumb(0.7, 1.556, -2.62);
      pigeonsInCell(id === 3 ? 1 : 40);
      if (id === 4 && t > at("forty") - 0.3) person("pris", PRISONER, PX, PZ, "grin", { seed: 3, wave: q(0.5 + 0.5 * Math.sin(t * 7), 4) });
      if (id === 3) burst(0.5, 1.75, -2.6, at("pigeon"), 0.4);
    } else if (id === 5 || id === 6) {
      pigeonsInCell(40);
      if (id === 5) person("pris", PRISONER, PX, PZ, "smile_closed", { seed: 3 });
      const laughing = id === 6 && t > at("laugh"), bob = laughing ? Math.sin(t * 22) * 3 : 0;
      const exA: Expr = laughing ? "laugh" : t > at("lonely") || id === 6 ? "grin" : "stern";
      inmates(laughing ? "laugh" : id === 6 || t > at("lonely") ? "grin" : "smile", laughing);
      person("guardA", GUARD_A, id === 6 ? 0.55 : 1.9, id === 6 ? 4.3 : 3.35, exA, { seed: 5, scale: 1.12, tilt: bob, headTilt: laughing ? 6 : 0 });
      person("guardB", GUARD_B, id === 6 ? 1.55 : 1.1, id === 6 ? 4.5 : 3.45, laughing ? "laugh" : exA === "stern" ? "stern" : "grin", { seed: 6, scale: 1.1, tilt: -bob, headTilt: laughing ? -6 : 0 });
    } else if (id === 7) {
      const nod = ease(t, at("falls"), at("asleep"));
      person("guardB", GUARD_B, 3.45, 5.05, nod > 0.6 ? "whistle" : "neutral", { seed: 6, mode: "sit", y: 0.0, blink: nod > 0.6 || (nod > 0.2 && Math.sin(t * 20) > 0), headTilt: q(14 * nod, 1), tilt: q(4 * nod, 1) });
      if (t > at("asleep")) for (let k = 0; k < 3; k++) {
        const u = ((t - at("asleep")) * 0.6 + k / 3) % 1;
        fxc.push({ key: "z", cw: 200, ch: 200, draw: drawZ, at: [3.6 + 0.35 * u, 1.75 + 0.7 * u, 4.95], w: 0.12 + 0.12 * u, h: 0.12 + 0.12 * u, soft: false });
      }
    } else if (id === 8) {
      const sk = stringsK(t), n = Math.round(sk * 40), hand: V3 = [PX + 0.05, 1.0, PZ - 0.3];
      person("pris", PRISONER, PX, PZ - 0.3, "grin", { seed: 3 });
      for (let i = 0; i < 40; i++) {
        const sp = RING_SPOTS[i], pk = Math.max(0, Math.sin((t * 1.1 + i * 0.37) * Math.PI * 2)) ** 6;
        pigeon(i, sp[0], sp[1], sp[2], sp[0] > PX, -0.15, pk, false);
        this.aim(i, i < n ? [sp[0], 0.22, sp[2]] : null, hand);
      }
    } else if (id === 9) {
      inmates("smile", false);
      const x = wardenX(t), walking = t > KW.warden - 0.6 && t < KW.cell - 0.1;
      person("warden", WARDEN, x, 3.4, "stern", { seed: 9, side: true, mode: walking ? "march" : "stand", phase: walking ? (t * 1.8) % 1 : 0 });
    } else if (id === 10) {
      inmates(t > at("empty") ? "grin" : "neutral", false, t > at("empty"));
      const ex: Expr = t > at("empty") ? "shock" : t > at("finds") - 0.2 ? "nervous" : "stern";
      person("warden", WARDEN, 1.1, 3.25, ex, { seed: 9, blink: ex === "shock" ? false : undefined });
    } else if (id === 12) {
      crumb(-1.48, 0.665, -2.12, 0.11);
      burst(-1.48, 0.76, -2.1, at("breadcrumb2"), 0.32);
    } else if (id === 13) {
      const F = flockAt(t), sway = Math.sin(t * 1.1) * 0.08, man: V3 = [F[0] + sway * 2, F[1] - 3.6, F[2]];
      person("pris", PRISONER, man[0], man[2], "grin", { seed: 3, y: man[1], wave: q(0.5 + 0.5 * Math.sin(t * 5), 4), roll: sway });
      const grip: V3 = [man[0] + 0.1, man[1] + 2.15, man[2]];
      for (let i = 0; i < 40; i++) {
        const o = FLOCK_SPOTS[i], p: V3 = [F[0] + o[0], F[1] + o[1], F[2] + o[2]];
        pigeon(i, p[0], p[1], p[2], false, flapAt(hh(i, 30), 2.4 + hh(i, 31)), 0, true, true, 0.9);
        this.aim(i, [p[0] + 0.05, p[1] + 0.12, p[2]], grip);
      }
    }
    if (id <= 6 || (id >= 10 && id <= 12)) for (let i = 0; i < 26; i++) {
      const u = (t * 0.05 + hh(i, 40)) % 1;
      fxc.push({ key: "mote", cw: 64, ch: 64, draw: (p) => { const g = p.g, gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,244,214,0.9)"); gr.addColorStop(1, "rgba(255,244,214,0)"); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); },
        at: [0.2 + hh(i, 41) * 1.1 + 0.15 * Math.sin(t * 0.7 + i), 0.4 + ((hh(i, 42) + u * 0.4) % 1) * 2.0, -2.3 + hh(i, 43) * 1.8], w: 0.025, h: 0.025, soft: true });
    }
    if (id !== 8 && id !== 13) for (const m of this.strings) m.visible = false;

    // ---- cards -> meshes ----
    let ai = 0;
    for (const p of cards) {
      const a = this.actor(ai++), d = cam.position.distanceTo(this.v.set(p.at[0], p.at[1] + 1, p.at[2]));
      const [w, h, k] = p.key.startsWith("pigeon") ? tier(d * 2.4) : tier(d);
      a.r = this.pool.req(p.key, w, h, k, p.draw);
      a.mesh.visible = true; a.mesh.position.set(...p.at);
      a.mesh.rotation.set(0, Math.atan2(cam.position.x - p.at[0], cam.position.z - p.at[2]), p.roll ?? 0);
      const sc2 = p.scale ?? 1; a.mesh.scale.set(p.mirror ? -sc2 : sc2, sc2, sc2);
      a.mesh.castShadow = false;
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    let fi = 0;
    for (const p of fxc) {
      const e = this.fx(fi++);
      e.r = this.pool.req(p.key, p.cw, p.ch, 1, p.draw);
      e.use(!!p.soft); e.mesh.visible = true; e.mesh.position.set(...p.at);
      if (p.flat) e.mesh.rotation.set(-Math.PI / 2, 0, p.rot ?? 0); else { e.mesh.quaternion.copy(cam.quaternion); e.mesh.rotateZ(p.rot ?? 0); }
      e.mesh.scale.set(p.w, p.h, 1);
    }
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (let i = 0; i < ai; i++) this.actors[i].bind();
    for (let i = 0; i < fi; i++) this.fxs[i].bind();
    return focus;
  }

  /** string i from a to b (null hides it) */
  private aim(i: number, a: V3 | null, b: V3) {
    const m = this.strings[i];
    if (!a) { m.visible = false; return; }
    const A = V(...a), B = V(...b), d = B.clone().sub(A), len = d.length();
    m.visible = true; m.position.copy(A);
    m.quaternion.setFromUnitVectors(V(0, 1, 0), d.normalize());
    m.scale.set(0.0032, len, 0.0032);
  }
}
export { SHOTS };
