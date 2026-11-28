// usage: node scripts/stills.mjs <compId> <outPrefix> <frame,frame,...>
//   or:  JOBS='[{"comp":"X","frame":10,"out":"out/a.jpg","props":{...}}]' node scripts/stills.mjs
import fs from "node:fs";
import path from "node:path";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
const chromiumOptions = { gl: process.env.REMOTION_GL || "swangle", enableMultiProcessOnLinux: true };
let jobs;
if (process.env.JOBS) jobs = JSON.parse(process.env.JOBS);
else { const [comp, prefix, frames] = process.argv.slice(2); jobs = frames.split(",").map((f) => ({ comp, frame: Number(f), out: `${prefix}${f}.jpg` })); }
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const onBrowserLog = (l) => { if (!/THREE.Clock|404|Failed to load resource/.test(l.text)) console.log(`[${l.type}]`, l.text.slice(0, 400)); };
for (const j of jobs) {
  fs.mkdirSync(path.dirname(j.out), { recursive: true });
  const t0 = Date.now();
  try {
    const composition = await selectComposition({ serveUrl, id: j.comp, chromiumOptions, inputProps: j.props || {} });
    await renderStill({ composition, serveUrl, frame: j.frame, output: j.out, imageFormat: "jpeg", jpegQuality: 90,
      chromiumOptions, inputProps: j.props || {}, timeoutInMilliseconds: 600000, onBrowserLog });
    console.log("still", j.comp, j.frame, j.out, ((Date.now() - t0) / 1000).toFixed(1) + "s");
  } catch (e) { console.log("FAILED", j.comp, j.frame, String(e).slice(0, 600)); }
}
