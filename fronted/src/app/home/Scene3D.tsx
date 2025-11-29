'use client';

import React, { useRef, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Text3D, Center, Float } from '@react-three/drei';
import * as THREE from 'three';

function SwingingLamp() {
  const pivotRef = useRef<THREE.Group>(null);
  const targetRef = useRef<THREE.Object3D>(null);
  const lightRef = useRef<THREE.SpotLight>(null);

  useEffect(() => {
    if (lightRef.current && targetRef.current) {
      lightRef.current.target = targetRef.current;
    }
  }, []);

  useFrame(({ clock }) => {
    if (pivotRef.current) {
      const t = clock.getElapsedTime();
      const angleZ = Math.sin(t * 1.5) * 0.4 + Math.sin(t * 0.5) * 0.1; 
      const angleX = Math.sin(t * 1.1) * 0.2;
      
      pivotRef.current.rotation.z = angleZ;
      pivotRef.current.rotation.x = angleX;
    }
  });

  return (
    <group position={[0, 10, 0]}>
      <group ref={pivotRef}>
        <mesh position={[0, -3, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 6]} />
          <meshStandardMaterial color="#111" />
        </mesh>
        
        <group position={[0, -6, 0]}>
          <mesh position={[0, 0.2, 0]}>
             <cylinderGeometry args={[0.3, 0.5, 0.8]} />
             <meshStandardMaterial color="#333" roughness={0.3} metalness={0.8} />
          </mesh>
          <mesh position={[0, -0.2, 0]}>
            <coneGeometry args={[1.8, 1.5, 64, 1, true]} />
            <meshPhysicalMaterial 
                color="#222" 
                metalness={0.8} 
                roughness={0.2} 
                clearcoat={0.5}
                side={THREE.DoubleSide} 
            />
          </mesh>
          <mesh position={[0, -0.2, 0]}>
             <sphereGeometry args={[0.4, 32, 32]} />
             <meshBasicMaterial color="#fff" toneMapped={false} />
          </mesh>

          <spotLight
            ref={lightRef}
            castShadow
            angle={0.6}
            penumbra={0.2}
            intensity={3000}
            color="#ffffff"
            distance={60}
            decay={1.2}
            shadow-mapSize={[2048, 2048]}
            shadow-bias={-0.0001}
          />
          <pointLight intensity={200} distance={10} color="#eef" />
          
          <object3D ref={targetRef} position={[0, -10, 0]} />
        </group>
      </group>
    </group>
  );
}

function Title3D() {
  return (
    <Center position={[0, 0, 0]}>
        <Float speed={3} rotationIntensity={0.2} floatIntensity={0.2}>
            <Text3D
                font="https://unpkg.com/three@0.160.0/examples/fonts/helvetiker_bold.typeface.json"
                size={1.2}
                height={0.3}
                curveSegments={24}
                bevelEnabled
                bevelThickness={0.04}
                bevelSize={0.02}
                bevelOffset={0}
                bevelSegments={8}
            >
                Dota2 API Docs
                <meshStandardMaterial 
                    color="#aaaaaa"
                    metalness={0.9}
                    roughness={0.1}
                />
            </Text3D>
        </Float>
    </Center>
  );
}

function SceneContent() {
  return (
    <>
        <SwingingLamp />
        <Title3D />
        
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -3, 0]} receiveShadow>
            <planeGeometry args={[100, 100]} />
            <shadowMaterial transparent opacity={0.15} color="#000000" />
        </mesh>

        {/* Lights replacing Environment to prevent fetch errors */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <pointLight position={[-5, 0, 5]} intensity={0.5} color="blue" />
    </>
  );
}

export default function Scene3D() {
  return (
    <div className="absolute inset-0 w-full h-full">
       <Canvas 
         shadows 
         camera={{ position: [0, 0, 12], fov: 35 }} 
         dpr={[1, 2]}
         gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.0, alpha: true }}
       >
          <Suspense fallback={null}>
             <SceneContent />
          </Suspense>
       </Canvas>
    </div>
  );
}
