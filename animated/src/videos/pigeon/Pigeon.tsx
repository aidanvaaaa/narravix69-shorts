// The Pigeon Escape in the 3D toon-world engine. One world (pworld.ts) posed per frame from pstory.ts.
// Rendered without the R3F EffectComposer by default (it renders blank under software GL on CI); three's own
// Neutral tone mapping stands in for the composer's tone-map pass. inputProps { post: { composer: true } } tries
// the full ink + lens + grade chain with 8-bit buffers.
import React, { useEffect, useMemo } from "react";
import * as THREE from "three";
import { AbsoluteFill, getInputProps, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { EffectComposer } from "@react-three/postprocessing";
import { ToneMappingEffect, ToneMappingMode } from "postprocessing";
import { PWorld } from "./pworld";
import { InkPass, noInkFallback } from "../bridge/ink";
import { TOTAL, FPS, SHOTS } from "./pstory";
import { KW } from "./ptime";

export const PIGEON_FRAMES = TOTAL;
type Toggles = { composer: boolean; ink: boolean };
const toggles = (): Toggles => ({ composer: false, ink: true, ...((getInputProps() as { post?: Partial<Toggles> }).post ?? {}) });

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const { camera, scene, gl } = useThree();
  const world = useMemo(() => new PWorld(), []);
  const on = useMemo(toggles, []);
  const fx = useMemo(() => ({ ink: new InkPass(scene, camera as THREE.PerspectiveCamera), tone: new ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL }) }), [camera, scene]);
  useEffect(() => () => fx.ink.dispose(), [fx]);
  useEffect(() => {
    gl.toneMapping = on.composer ? THREE.NoToneMapping : THREE.NeutralToneMapping;
    gl.toneMappingExposure = 1.0; gl.outputColorSpace = THREE.SRGBColorSpace;
  }, [gl, on]);
  world.update(f, camera as THREE.PerspectiveCamera, scene);
  noInkFallback(world.root);
  return (
    <>
      <primitive object={world.root} dispose={null} />
      {on.composer ? (
        <EffectComposer multisampling={0} frameBufferType={THREE.UnsignedByteType}>
          {on.ink ? <primitive object={fx.ink} dispose={null} /> : <></>}
          <primitive object={fx.tone} dispose={null} />
        </EffectComposer>
      ) : null}
    </>
  );
};

/** "30 DAYS LATER" stamp (shot 9), slams in on "Thirty" */
const Stamp: React.FC<{ f: number }> = ({ f }) => {
  const t = f / FPS, t0 = KW.thirty - 2 / FPS, u = t - t0;
  if (u < 0 || u > 2.0) return null;
  const s = u < 0.12 ? 1.6 - 5 * u : 1, o = u > 1.7 ? 1 - (u - 1.7) / 0.3 : 1;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
      <div style={{ transform: `rotate(-6deg) scale(${s})`, opacity: o, marginTop: -560, padding: "18px 40px", border: "10px solid #d8322f", borderRadius: 18, background: "rgba(255,248,236,0.88)",
        color: "#d8322f", fontFamily: "Arial Black, Arial, sans-serif", fontWeight: 900, fontSize: 104, letterSpacing: 6, boxShadow: "0 8px 0 rgba(36,23,38,0.55)" }}>
        30 DAYS LATER
      </div>
    </AbsoluteFill>
  );
};

export const PigeonShort: React.FC = () => {
  const f = useCurrentFrame();
  // short dips to black into and out of the night shots
  const n0 = SHOTS[6].a, n1 = SHOTS[8].a;
  const dip = Math.max(0, 1 - Math.abs(f - n0) / 5, 1 - Math.abs(f - n1) / 5) * 0.9;
  return (
    <AbsoluteFill style={{ background: "#101018" }}>
      <ThreeCanvas width={1080} height={1920} shadows camera={{ fov: 40, near: 0.05, far: 1500 }}
        gl={{ preserveDrawingBuffer: true, antialias: true, stencil: false, powerPreference: "high-performance" }}>
        <Inner />
      </ThreeCanvas>
      <Stamp f={f} />
      {dip > 0 && <AbsoluteFill style={{ background: "#000", opacity: dip }} />}
    </AbsoluteFill>
  );
};
