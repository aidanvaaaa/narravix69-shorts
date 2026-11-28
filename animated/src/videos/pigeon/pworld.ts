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
  golden: { ...LIGHTS.golden, actorShadow: false, sunDir: [-0.42, 0.3, 0.86], skyC: LOOK.golden.sky.c, skyE: LOOK.golden.sky.e, fogNear: 60, fogFar: 420 },
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
    const wall = lam("pg_wall", () => ({ map: stoneHD("pg_wallStone", ["#b9b0a4", "#aea596", "#c3baae", "#a69d90"], "#857c72") }));
    const wallDark = lam("pg_wall2", () => ({ map: stoneHD("pg_wallStone2", ["#9c948c", "#918a82", "#a69e95", "#8a837b"], "#6e6760") }));
    const floor = lam("pg_floor", () => ({ map: stoneHD("pg_floorStone", ["#8f8a86", "#86817c", "#99938e", "#7f7a75"], "#615c58") }));
    const wood = lam("pg_wood", () => ({ map: planksHD() }));
    const iron = lam("pg_iron", () => ({ color: "#4a4f5a" }));
    const mattress = lam("pg_mattress", () => ({ map: ctex("pg_ticking", 256, 256, (g) => { g.fillStyle = "#ece6d8"; g.fillRect(0, 0, 256, 256); g.fillStyle = "#6f86b8"; for (let x = 8; x < 256; x += 32) g.fillRect(x, 0, 9, 256); g.fillStyle = "#9fb0d4"; for (let x = 22; x < 256; x += 32) g.fillRect(x, 0, 3, 256); }) }));
    const pillow = lam("pg_pillow", () => ({ color: "#f3efe6" }));
    const red = lam("pg_blanket", () => ({ color: "#c0353a" }));
    const desk = lam("pg_desk", () => ({ color: "#8a5a3c" }));
    const b = new Batch();
    const box = (m: THREE.Material, x0: number, y0: number, z0: number, x1: number, y1: number, z1: number, tile = 1.2) => b.add(boxGeo(V(x0, y0, z0), V(x1, y1, z1), tile), m);

    // ---- cell (x -2..2, z -2.5..2.5) + corridor (z 2.5..7.2) ----
    box(floor, -6.5, -0.2, -3.2, 6.5, 0, 7.6, 1.0);
    // back wall with the window hole (x 0.25..1.05, y 1.55..2.35)
    box(wall, -2.3, 0, -2.9, 0.25, 4.2, -2.5); box(wall, 1.05, 0, -2.9, 2.3, 4.2, -2.5);
    box(wall, 0.25, 0, -2.9, 1.05, 1.55, -2.5); box(wall, 0.25, 2.35, -2.9, 1.05, 4.2, -2.5);
    // side walls of the cell
    box(wall, -2.3, 0, -2.9, -2.0, 4.2, 2.5); box(wall, 2.0, 0, -2.9, 2.3, 4.2, 2.5);
    // front: neighbouring cells' walls left/right of the bars, a lintel above the bars
    box(wallDark, -6.5, 0, 2.5, -2.0, 4.2, 2.8); box(wallDark, 2.0, 0, 2.5, 6.5, 4.2, 2.8); box(wallDark, -2.0, 3.2, 2.5, 2.0, 4.2, 2.8);
    // corridor: far wall and the two ends
    box(wallDark, -6.5, 0, 7.2, 6.5, 4.2, 7.6); box(wallDark, -6.8, 0, 2.5, -6.5, 4.2, 7.6); box(wallDark, 6.5, 0, 2.5, 6.8, 4.2, 7.6);
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
    // ---- the prison far below the sky set ----
    const grass = lam("pg_grass", () => ({ map: grassHD() }));
    const roof = lam("pg_roof", () => ({ map: roofHD("#5a5f6e", true) }));
    box(grass, 700, -0.5, -400, 1300, -0.25, 300, 6);
    const [px, , pz] = PRISON;
    box(wall, px - 16, -0.25, pz - 10, px + 16, 9, pz + 10, 2); box(roof, px - 16.5, 9, pz - 10.5, px + 16.5, 9.6, pz + 10.5, 3);
    for (const [dx, dz] of [[-22, -16], [22, -16], [-22, 16], [22, 16]]) { box(wall, px + dx - 2, -0.25, pz + dz - 2, px + dx + 2, 15, pz + dz + 2, 2); box(roof, px + dx - 2.6, 15, pz + dz - 2.6, px + dx + 2.6, 16, pz + dz + 2.6, 3); }
    box(wallDark, px - 22, -0.25, pz - 16.6, px + 22, 6, pz - 15.4, 2); box(wallDark, px - 22, -0.25, pz + 15.4, px + 22, 6, pz + 16.6, 2);
    box(wallDark, px - 22.6, -0.25, pz - 16, px - 21.4, 6, pz + 16, 2); box(wallDark, px + 21.4, -0.25, pz - 16, px + 22.6, 6, pz + 16, 2);
    b.build(R);

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
    this.door.rotation.y = id === 10 ? -1.25 * ease(t, KW.finds - 0.45, KW.finds + 0.25) : 0;

    // ---- cast ----
    const cards: Card[] = [], fxc: FxCard[] = [];
    const person = (name: string, o: Outfit, x: number, z: number, expr: Expr, opts: { mode?: "stand" | "march" | "sit" | "stroll"; side?: boolean; mirror?: boolean; phase?: number; wave?: number; tilt?: number; headTilt?: number; y?: number; seed: number; blink?: boolean; look?: number; roll?: number }) => {
      const mirror = !!opts.mirror, light = light2D(mirror), bl = opts.blink ?? blinkAt(t, opts.seed);
      const ph = q(opts.phase ?? 0, 24), wv = opts.wave === undefined ? undefined : q(opts.wave, 8);
      const key = `${name}|${expr}|${opts.mode ?? "stand"}|${opts.side ? 1 : 0}|${ph}|${wv}|${q(opts.tilt ?? 0, 2)}|${q(opts.headTilt ?? 0, 2)}|${bl ? 1 : 0}|${light.toFixed(2)}|${opts.look ?? 0}`;
      const draw = opts.side
        ? (p: Pen) => bodySide(p, o, { phase: ph, expr, mode: opts.mode === "march" ? "march" : "stand", blink: bl, light, seed: opts.seed })
        : (p: Pen) => bodyFront(p, o, { phase: ph, expr, mode: opts.mode ?? "stand", blink: bl, light, seed: opts.seed, wave: wv, tilt: opts.tilt, headTilt: opts.headTilt, look: opts.look, facing: 0 });
      cards.push({ key, draw, at: [x, opts.y ?? 0, z], mirror, roll: opts.roll, big: true });
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

    if (id === 1) {
      const wv = ease(t, at("single") - 0.5, at("single"));
      person("pris", PRISONER, PX, PZ, t > at("single") - 0.4 ? "grin" : "smile", { seed: 3, wave: wv > 0.02 ? wv : undefined });
      if (wv > 0.5) crumb(PX + 0.34, 1.6 + 0.03 * Math.sin(t * 3), PZ + 0.05, 0.12, false);
      burst(PX + 0.34, 1.6, PZ + 0.04, at("breadcrumb1"), 0.5);
    } else if (id === 2) {
      const k = walkK(t), p = lerp3(P_WALK[0], P_WALK[1], k), walking = k > 0 && k < 1;
      person("pris", PRISONER, p[0], p[2], "smile", { seed: 3, side: true, mode: walking ? "march" : "stand", phase: walking ? (t * 1.7) % 1 : 0, mirror: true });
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
      person("guardA", GUARD_A, id === 6 ? 0.84 : 0.65, id === 6 ? 4.6 : 4.15, exA, { seed: 5, tilt: bob, headTilt: laughing ? 6 : 0 });
      person("guardB", GUARD_B, id === 6 ? 1.42 : 1.6, id === 6 ? 4.55 : 4.0, laughing ? "laugh" : exA === "stern" ? "neutral" : "smile", { seed: 6, tilt: -bob, headTilt: laughing ? -6 : 0 });
    } else if (id === 7) {
      const nod = ease(t, at("falls"), at("asleep"));
      person("guardB", GUARD_B, 3.45, 5.3, nod > 0.6 ? "whistle" : "neutral", { seed: 6, mode: "sit", y: 0.0, blink: nod > 0.6 || (nod > 0.2 && Math.sin(t * 20) > 0), headTilt: q(14 * nod, 1), tilt: q(4 * nod, 1) });
      if (t > at("asleep")) for (let k = 0; k < 3; k++) {
        const u = ((t - at("asleep")) * 0.6 + k / 3) % 1;
        fxc.push({ key: "z", cw: 200, ch: 200, draw: drawZ, at: [3.6 + 0.35 * u, 1.75 + 0.7 * u, 5.2], w: 0.12 + 0.12 * u, h: 0.12 + 0.12 * u, soft: false });
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
      const x = wardenX(t), walking = t > KW.warden - 0.6 && t < KW.cell - 0.1;
      person("warden", WARDEN, x, 3.4, "stern", { seed: 9, side: true, mode: walking ? "march" : "stand", phase: walking ? (t * 1.8) % 1 : 0 });
    } else if (id === 10) {
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
