'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export default function SaunaViewer({ modelPath, bakedMaterials = false }) {
  const canvasRef = useRef(null);
  const [loadingText, setLoadingText] = useState('Laadimine...');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // ── Scene ──────────────────────────────────────────────
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);

    // ── Camera ─────────────────────────────────────────────
    const camera = new THREE.PerspectiveCamera(
      45,
      canvas.clientWidth / canvas.clientHeight,
      0.1,
      100
    );
    camera.position.set(4, 2.5, 5);

    // ── Renderer ───────────────────────────────────────────
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.8;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // ── Lights ─────────────────────────────────────────────
    scene.add(new THREE.AmbientLight(0xffffff, 2.5));
    scene.add(new THREE.HemisphereLight(0xffffff, 0xe8e0d8, 1.2));

    const keyLight = new THREE.DirectionalLight(0xfff5e6, 2.0);
    keyLight.position.set(-3, 5, 6);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.set(2048, 2048);
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 30;
    keyLight.shadow.camera.left = -5;
    keyLight.shadow.camera.right = 5;
    keyLight.shadow.camera.top = 5;
    keyLight.shadow.camera.bottom = -5;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xc8d8ff, 1.2);
    fillLight.position.set(3, 3, 5);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xffffff, 0.6);
    rimLight.position.set(2, 4, -4);
    scene.add(rimLight);

    const bottomLight = new THREE.DirectionalLight(0xffe8d0, 0.5);
    bottomLight.position.set(0, -3, 2);
    scene.add(bottomLight);

    // ── Ground ─────────────────────────────────────────────
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(20, 20),
      new THREE.ShadowMaterial({ opacity: 0.15 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.01;
    ground.receiveShadow = true;
    scene.add(ground);

    // ── Controls ───────────────────────────────────────────
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.target.set(0, 1.0, 0);
    controls.minDistance = 2;
    controls.maxDistance = 12;
    controls.maxPolarAngle = Math.PI / 2 + 0.1;
    controls.update();

    // ── Textures ───────────────────────────────────────────
    const texLoader = new THREE.TextureLoader();

    function tex(path, rx = 1, ry = 1, linear = false) {
      const t = texLoader.load(path);
      t.wrapS = t.wrapT = THREE.RepeatWrapping;
      t.repeat.set(rx, ry);
      if (!linear) t.colorSpace = THREE.SRGBColorSpace;
      return t;
    }

    const spruceMat = new THREE.MeshStandardMaterial({
      map: tex('/textures/wood_planks_dirt_diff.jpg', 4, 1),
      roughnessMap: tex('/textures/wood_planks_dirt_rough.jpg', 4, 1, true),
      normalMap: tex('/textures/wood_planks_dirt_unknown.jpg', 4, 1, true),
      roughness: 0.85, side: THREE.DoubleSide,
    });
    const wallMat = new THREE.MeshStandardMaterial({
      map: tex('/textures/raw_plank_wall_diff.jpg', 2, 2),
      roughnessMap: tex('/textures/raw_plank_wall_rough.jpg', 2, 2, true),
      normalMap: tex('/textures/raw_plank_wall_unknown.jpg', 2, 2, true),
      roughness: 0.8, side: THREE.DoubleSide,
    });
    const shinglesMat = new THREE.MeshStandardMaterial({
      map: tex('/textures/roof_09_diff.jpg', 4, 4),
      roughnessMap: tex('/textures/roof_09_rough.jpg', 4, 4, true),
      normalMap: tex('/textures/roof_09_unknown.jpg', 4, 4, true),
      roughness: 0.9, color: new THREE.Color(0x444444),
    });
    const trimMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.5, metalness: 0.3 });
    const legMat = new THREE.MeshStandardMaterial({
      map: tex('/textures/wooden_planks_diff.jpg'),
      roughnessMap: tex('/textures/wooden_planks_rough.jpg', 1, 1, true),
      normalMap: tex('/textures/wooden_planks_unknown.jpg', 1, 1, true),
      roughness: 0.8,
    });
    const floorMat = new THREE.MeshStandardMaterial({
      map: tex('/textures/wood_planks_diff.jpg', 2, 2),
      roughnessMap: tex('/textures/wood_planks_arm.jpg', 2, 2, true),
      normalMap: tex('/textures/wood_planks_nor.jpg', 2, 2, true),
      roughness: 0.75,
    });
    const benchMat = new THREE.MeshStandardMaterial({
      map: tex('/textures/finewood_diff.jpg', 2, 1),
      roughnessMap: tex('/textures/finewood_rough.jpg', 2, 1, true),
      normalMap: tex('/textures/finewood_nor.jpg', 2, 1, true),
      roughness: 0.6, color: new THREE.Color(0xdec8a0),
    });
    const porchMat = new THREE.MeshStandardMaterial({
      map: tex('/textures/brown_planks_09_diff.jpg'),
      roughnessMap: tex('/textures/brown_planks_09_rough.jpg', 1, 1, true),
      normalMap: tex('/textures/brown_planks_09_unknown.jpg', 1, 1, true),
      roughness: 0.75,
    });
    const ventMat = new THREE.MeshStandardMaterial({ color: 0x555555, roughness: 0.4, metalness: 0.7 });
    const stoneMat = new THREE.MeshStandardMaterial({ color: 0x3a3a3a, roughness: 0.9, metalness: 0.1 });
    const heaterMat = new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.3, metalness: 0.8 });
    const stoneSaunaMat = new THREE.MeshStandardMaterial({ color: 0x6b6b6b, roughness: 0.95, metalness: 0.05 });
    const chimneyMat = new THREE.MeshStandardMaterial({ color: 0xcccccc, roughness: 0.2, metalness: 0.9 });
    const glassMat = new THREE.MeshPhysicalMaterial({
      transparent: true, opacity: 0.25, roughness: 0.05,
      transmission: 0.92, ior: 1.5, thickness: 0.01,
      color: 0xffffff, side: THREE.DoubleSide,
    });
    const doorFrameMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.35, metalness: 0.8 });

    const meshMatMap = {
      stave_body: spruceMat, shell_outer: spruceMat,
      front_wall: wallMat, back_wall: wallMat, front_wall_mesh: wallMat,
      front_wall_ring: trimMat, back_wall_ring: trimMat, front_wall_ring_mesh: trimMat,
      roof_shingles: shinglesMat,
      cradle_front: legMat, cradle_middle: legMat, cradle_back: legMat,
      louvered_vent_back_1: ventMat, louvered_vent_back_2: ventMat,
      floor_duckboard: floorMat,
      bench_back_upper: benchMat, bench_back_lower: benchMat,
      bench_left_upper: benchMat, bench_left_lower: benchMat,
      bench_support: benchMat, 'bench_support.001': benchMat,
      'bench_support.002': benchMat, 'bench_support.003': benchMat,
      'bench_support.004': benchMat,
      heater_base: stoneMat, heater_body: heaterMat,
      heater_glass: glassMat, heater_basket: heaterMat,
      heater_stones: stoneSaunaMat,
      chimney_tank: chimneyMat, chimney_pipe: chimneyMat,
      chimney_cap: chimneyMat, chimney_cap_support: chimneyMat,
      door_panel: doorFrameMat, door_glass: glassMat,
      door_frame_vmullion_1: doorFrameMat, door_frame_vmullion_2: doorFrameMat,
      door_frame_hmullion: doorFrameMat, door_handle: chimneyMat,
      porch_seat_left: porchMat, porch_seat_right: porchMat,
    };

    // ── Load model ─────────────────────────────────────────
    let saunaModel = null;
    const loader = new GLTFLoader();

    loader.load(
      modelPath,
      (gltf) => {
        const model = gltf.scene;
        saunaModel = model;

        model.traverse((child) => {
          if (!child.isMesh) return;
          child.castShadow = true;
          child.receiveShadow = true;
          if (bakedMaterials) {
            // Use embedded materials, just ensure double-sided
            if (child.material) child.material.side = THREE.DoubleSide;
          } else {
            const mat = meshMatMap[child.name];
            if (mat) {
              child.material = mat;
            } else if (child.material) {
              child.material.side = THREE.DoubleSide;
            }
          }
        });

        // Add to scene first so Three.js fully resolves all world transforms
        scene.add(model);

        // Compute bounds from mesh geometry only (skips empties/helpers)
        const box = new THREE.Box3();
        model.traverse((child) => {
          if (child.isMesh) box.expandByObject(child);
        });
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        // Center model horizontally, sit on ground
        model.position.x -= center.x;
        model.position.z -= center.z;
        model.position.y -= box.min.y;

        // Recompute after repositioning for accurate orbit target
        const box2 = new THREE.Box3();
        model.traverse((child) => {
          if (child.isMesh) box2.expandByObject(child);
        });
        const center2 = box2.getCenter(new THREE.Vector3());

        controls.target.copy(center2);
        const maxDim = Math.max(size.x, size.y, size.z);
        camera.position.set(center2.x + maxDim * 1.5, center2.y + maxDim * 0.8, center2.z + maxDim * 1.8);
        controls.update();

        setLoaded(true);
      },
      (progress) => {
        if (progress.total > 0) {
          const pct = Math.round((progress.loaded / progress.total) * 100);
          setLoadingText(`Laadimine... ${pct}%`);
        }
      },
      (error) => {
        console.error('GLB load error:', error);
        setLoadingText('Viga laadimisel.');
      }
    );

    // ── Render loop ────────────────────────────────────────
    const clock = new THREE.Clock();
    let animId;

    function animate() {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      if (saunaModel) saunaModel.rotation.y += 0.1 * delta;
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // ── Resize ─────────────────────────────────────────────
    function onResize() {
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
    }
    window.addEventListener('resize', onResize);

    // ── Cleanup ────────────────────────────────────────────
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
      controls.dispose();
      renderer.dispose();
    };
  }, [modelPath]);

  return (
    <>
      <canvas ref={canvasRef} className="viewer-canvas" />
      {!loaded && (
        <div className="loading-overlay">
          <div className="spinner" />
          <span>{loadingText}</span>
        </div>
      )}
    </>
  );
}
