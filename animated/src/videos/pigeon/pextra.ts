// The rest of the cell block: other inmates (outfits + where they stand), "HA!" mocking text, cell number plates.
import { Pen, Outfit, INK } from "../bridge/toon";
import { ctex } from "../bridge/paint";

const inmate = (jacket: string, hair: string | null, skin: string, extra: Partial<Outfit> = {}): Outfit =>
  ({ jacket, pants: jacket, boots: "#3a2a20", hat: hair ? "hair" : null, hair: hair ?? undefined, skin, buttons: "#fbe7c8", ...extra });

/** neighbours left/right of our cell, and the four cells across the corridor */
export const INMATES: { o: Outfit; x: number; z: number }[] = [
  { o: inmate("#f08a2c", "#1c1410", "#c99067", { build: "stout" }), x: -4.3, z: 1.7 },
  { o: inmate("#e8742a", null, "#f5c9a0", { moustache: "#3a2414" }), x: 4.4, z: 1.5 },
  { o: inmate("#f39a3a", "#7a4a22", "#ecd0b6"), x: -4.9, z: 8.2 },
  { o: inmate("#ee8030", "#2a2a2a", "#8a5a3c", { build: "stout" }), x: -1.7, z: 8.35 },
  { o: inmate("#f08a2c", "#c9b27a", "#f5c9a0"), x: 1.55, z: 8.25 },
  { o: inmate("#e57828", null, "#d6a47e", { moustache: "#1a1412", build: "stout" }), x: 4.8, z: 8.3 },
];

/** "HA!" / "HAHA" / "LOL" mocking text in comic lettering (512 x 256) */
export const haTex = (p: Pen, k: number) => {
  const g = p.g, txt = ["HA!", "HAHA", "HA HA!"][k % 3];
  g.save(); g.translate(256, 140); g.rotate([-0.12, 0.08, -0.05][k % 3]);
  g.font = "900 120px Arial Black, Arial"; g.textAlign = "center"; g.textBaseline = "middle";
  g.lineJoin = "round"; g.lineWidth = 22; g.strokeStyle = INK; g.strokeText(txt, 0, 0);
  g.fillStyle = ["#ffe066", "#ffffff", "#ffb347"][k % 3]; g.fillText(txt, 0, 0);
  g.restore();
};

/** black cell number plate with white stencil text */
export const plateTex = (txt: string) => ctex("pg_plate_" + txt, 256, 102, (g) => {
  g.fillStyle = "#1d1f24"; g.fillRect(0, 0, 256, 102);
  g.strokeStyle = "#8a8f99"; g.lineWidth = 6; g.strokeRect(5, 5, 246, 92);
  g.fillStyle = "#f0ede4"; g.font = "900 62px Arial Black, Arial"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(txt, 128, 54);
});
