'use client'

import { Box, Environment, Float, Icosahedron, MeshDistortMaterial, Octahedron, Sphere, Torus } from '@react-three/drei'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Suspense, useEffect, useRef } from 'react'
import * as THREE from 'three'

export function Scene() {
    const { camera, gl } = useThree()
    const groupRef = useRef<THREE.Group>(null)
    const particlesRef = useRef<THREE.Points | null>(null)

    // Create particle system
    useEffect(() => {
        const particleCount = 2000
        const positions = new Float32Array(particleCount * 3)
        const colors = new Float32Array(particleCount * 3)

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 50
            positions[i * 3 + 1] = (Math.random() - 0.5) * 50
            positions[i * 3 + 2] = (Math.random() - 0.5) * 50

            colors[i * 3] = Math.random() * 0.5 + 0.5     // R
            colors[i * 3 + 1] = Math.random() * 0.5 + 0.5 // G
            colors[i * 3 + 2] = Math.random()              // B
        }

        const geometry = new THREE.BufferGeometry()
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

        const material = new THREE.PointsMaterial({
            size: 0.5,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        })

        const particles = new THREE.Points(geometry, material)
        particlesRef.current = particles

        return () => {
            geometry.dispose()
            material.dispose()
        }
    }, [])

    useFrame((state) => {
        const time = state.clock.getElapsedTime()

        if (groupRef.current) {
            groupRef.current.rotation.y = time * 0.1
            groupRef.current.rotation.x = Math.sin(time * 0.2) * 0.1
        }

        if (particlesRef.current) {
            particlesRef.current.rotation.y = time * 0.05
            particlesRef.current.rotation.x = Math.sin(time * 0.1) * 0.05
        }

        // Camera movement
        camera.position.x = Math.sin(time * 0.1) * 2
        camera.position.y = Math.cos(time * 0.15) * 1
        camera.lookAt(0, 0, 0)
    })

    return (
        <group ref={groupRef}>
            {/* Particle system */}
            {particlesRef.current && <primitive object={particlesRef.current} />}

            {/* Floating geometric shapes */}
            <Float speed={2} rotationIntensity={1} floatIntensity={2}>
                <Sphere args={[1, 32, 32]} position={[-3, 2, -2]}>
                    <MeshDistortMaterial
                        color="#00f2fe"
                        attach="material"
                        distort={0.3}
                        speed={2}
                        transparent
                        opacity={0.7}
                    />
                </Sphere>
            </Float>

            <Float speed={1.5} rotationIntensity={2} floatIntensity={1.5}>
                <Octahedron args={[1.2]} position={[3, -1, -1]}>
                    <MeshDistortMaterial
                        color="#00ff88"
                        attach="material"
                        distort={0.4}
                        speed={1.5}
                        transparent
                        opacity={0.6}
                    />
                </Octahedron>
            </Float>

            <Float speed={2.5} rotationIntensity={1.5} floatIntensity={1}>
                <Torus args={[1, 0.4, 16, 32]} position={[0, -2, 2]}>
                    <MeshDistortMaterial
                        color="#ff0080"
                        attach="material"
                        distort={0.2}
                        speed={3}
                        transparent
                        opacity={0.8}
                    />
                </Torus>
            </Float>

            <Float speed={1} rotationIntensity={3} floatIntensity={2.5}>
                <Icosahedron args={[0.8]} position={[-2, -3, 1]}>
                    <MeshDistortMaterial
                        color="#8000ff"
                        attach="material"
                        distort={0.5}
                        speed={1}
                        transparent
                        opacity={0.5}
                    />
                </Icosahedron>
            </Float>

            <Float speed={3} rotationIntensity={2} floatIntensity={1.5}>
                <Box args={[1.5, 1.5, 1.5]} position={[2, 3, -3]}>
                    <MeshDistortMaterial
                        color="#ffaa00"
                        attach="material"
                        distort={0.1}
                        speed={2.5}
                        transparent
                        opacity={0.6}
                    />
                </Box>
            </Float>

            {/* Central energy core */}
            <Float speed={4} rotationIntensity={4} floatIntensity={0.5}>
                <Sphere args={[0.3, 16, 16]} position={[0, 0, 0]}>
                    <meshBasicMaterial
                        color="#ffffff"
                        transparent
                        opacity={0.9}
                    />
                </Sphere>
            </Float>

            {/* Energy rings */}
            <Torus args={[2, 0.05, 8, 64]} position={[0, 0, 0]}>
                <meshBasicMaterial
                    color="#00f2fe"
                    transparent
                    opacity={0.3}
                />
            </Torus>

            <Torus args={[2.5, 0.03, 8, 64]} position={[0, 0, 0]}>
                <meshBasicMaterial
                    color="#00ff88"
                    transparent
                    opacity={0.2}
                />
            </Torus>

            <Torus args={[3, 0.02, 8, 64]} position={[0, 0, 0]}>
                <meshBasicMaterial
                    color="#ff0080"
                    transparent
                    opacity={0.1}
                />
            </Torus>
        </group>
    )
}

export function SceneCanvas() {
    return (
        <Canvas
            camera={{ position: [0, 0, 10], fov: 75 }}
            gl={{
                antialias: true,
                alpha: true,
                powerPreference: "high-performance"
            }}
            style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 10
            }}
        >
            <Suspense fallback={null}>
                <Scene />
                <Environment preset="night" />
            </Suspense>
        </Canvas>
    )
}
