import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial, Text, Html } from '@react-three/drei';

function Tumor({ position, onClick }) {
    const [hovered, setHover] = useState(false);

    return (
        <group position={position}>
            <Sphere args={[0.3, 32, 32]} onClick={onClick} onPointerOver={() => setHover(true)} onPointerOut={() => setHover(false)}>
                <MeshDistortMaterial
                    color="#ef4444"
                    speed={2}
                    distort={0.4}
                    roughness={0.2}
                    emissive="#991b1b"
                    emissiveIntensity={hovered ? 0.8 : 0.4}
                />
            </Sphere>
            {hovered && (
                <Html distanceFactor={10}>
                    <div className="bg-slate-900/90 p-2 rounded-lg border border-red-500/50 text-xs w-32 backdrop-blur-md">
                        <p className="font-bold text-red-400">Glioblastoma</p>
                        <p className="text-gray-300">Vol: 14.2 cm³</p>
                        <p className="text-gray-300">Conf: 98.2%</p>
                    </div>
                </Html>
            )}
        </group>
    );
}

function BrainCortex() {
    return (
        <Sphere args={[1.5, 64, 64]}>
            <MeshDistortMaterial
                color="#e2e8f0"
                transparent
                opacity={0.3}
                roughness={0.1}
                metalness={0.1}
                distort={0.2}
                speed={0.5}
                depthWrite={false} // Important for transparency
            />
        </Sphere>
    );
}

export default function BrainModel() {
    const groupRef = useRef();

    useFrame((state) => {
        const t = state.clock.getElapsedTime();
        if (groupRef.current) {
            groupRef.current.rotation.y = Math.sin(t / 4) * 0.2;
        }
    });

    return (
        <group ref={groupRef}>
            {/* Cerebro "Mock" traslúcido */}
            <BrainCortex />

            {/* Tumor simulado en el lóbulo frontal derecho */}
            <Tumor position={[0.8, 0.5, 0.5]} />

            {/* Segundo tumor pequeño profundo */}
            <Tumor position={[-0.4, -0.2, 0.2]} />
        </group>
    );
}
