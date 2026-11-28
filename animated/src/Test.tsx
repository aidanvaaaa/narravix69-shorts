import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";

export const TestCube: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#204060" }}>
      <ThreeCanvas width={1080} height={1920} gl={{ preserveDrawingBuffer: true }} camera={{ fov: 40, position: [0, 0, 6] }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[3, 4, 5]} intensity={1.5} />
        <mesh rotation={[0.4, f * 0.05, 0]}>
          <boxGeometry args={[2, 2, 2]} />
          <meshStandardMaterial color="#e05030" />
        </mesh>
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
