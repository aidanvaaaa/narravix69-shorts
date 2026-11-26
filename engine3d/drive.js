// Headless WebGL renderer driver: renders exported shots to mp4 files.
// usage: node drive.js <workdir> <shot1,shot2,...> [--still frames] [--w 720 --h 1280]
const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
let pw; try { pw = require('playwright'); } catch (e) { pw = require('/opt/npm-tools/node_modules/playwright'); }
const HERE = __dirname;
const WORK = path.resolve(process.argv[2]); const shots = process.argv[3].split(',');
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const W = +arg('--w', 720), H = +arg('--h', 1280), STILL = arg('--still', null), MS = arg('--ms', '4'), SMQ = arg('--sm', '2048');
const FONT_ANTON = process.env.FONT_ANTON || '/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf';
const FONT_POPPINS = process.env.FONT_POPPINS || '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf';
(async () => {
  const b = await pw.chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: W, height: H } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.route('http://local/**', async r => {
    const u = new URL(r.request().url()); let f;
    if (u.pathname.startsWith('/font2/')) f = FONT_POPPINS;
    else if (u.pathname.startsWith('/font/')) f = FONT_ANTON;
    else if (u.pathname.startsWith('/data/')) f = path.join(WORK, 'data', u.pathname.slice(6));
    else if (u.pathname.startsWith('/tex/')) f = path.join(WORK, 'tex', u.pathname.slice(5));
    else f = path.join(HERE, u.pathname);
    try { r.fulfill({ body: fs.readFileSync(f) }); } catch (e) { r.fulfill({ status: 404 }); }
  });
  console.log('GL', await p.evaluate(() => { const g = document.createElement('canvas').getContext('webgl2'); const e = g.getExtension('WEBGL_debug_renderer_info'); return g.getParameter(e.UNMASKED_RENDERER_WEBGL); }));
  await p.goto(`http://local/renderer.html?w=${W}&h=${H}&ms=${MS}&sm=${SMQ}`); await p.evaluate(() => window.ready);
  fs.mkdirSync(path.join(WORK, 'vid'), { recursive: true });
  for (const s of shots) {
    const n = await p.evaluate(s => loadShot(s), s);
    if (STILL) {
      const fis = STILL === 'mid' ? [Math.floor(n * 0.6)] : STILL.split(',').map(Number);
      for (const fi of fis) {
        const d = await p.evaluate(i => renderFrame(i), Math.min(fi, n - 1));
        fs.writeFileSync(path.join(WORK, `still_${s}_${fi}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
      }
      continue;
    }
    const outf = path.join(WORK, 'vid', `${s}.mp4`), tmp = path.join(WORK, 'vid', `tmp_${s}.mp4`);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', '30', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30', tmp]);
    const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      const d = await p.evaluate(i => renderFrame(i), i);
      if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); const code = await new Promise(r => ff.on('close', r));
    if (code !== 0) { console.log('ffmpeg failed', s); process.exit(1); }
    fs.renameSync(tmp, outf);
    console.log('done', s, n, ((Date.now() - t0) / n).toFixed(0) + 'ms/f');
  }
  await b.close();
})();
