import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// ── Scene setup ──────────────────────────────────────────────
const canvas = document.getElementById('canvas3d');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

// ── Camera ───────────────────────────────────────────────────
const camera = new THREE.PerspectiveCamera(
  45,
  canvas.clientWidth / canvas.clientHeight,
  0.1,
  100
);
camera.position.set(4, 2.5, 5);

// ── Renderer ─────────────────────────────────────────────────
const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.8;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// ── Lighting ─────────────────────────────────────────────────
const ambientLight = new THREE.AmbientLight(0xffffff, 2.5);
scene.add(ambientLight);

const hemiLight = new THREE.HemisphereLight(0xffffff, 0xe8e0d8, 1.2);
scene.add(hemiLight);

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

// ── Ground plane ─────────────────────────────────────────────
const groundGeo = new THREE.PlaneGeometry(20, 20);
const groundMat = new THREE.ShadowMaterial({ opacity: 0.15 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.01;
ground.receiveShadow = true;
scene.add(ground);

// ── Orbit controls ───────────────────────────────────────────
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 1.0, 0);
controls.minDistance = 2;
controls.maxDistance = 12;
controls.maxPolarAngle = Math.PI / 2 + 0.1;
controls.update();

// ── Texture loader helper ────────────────────────────────────
const texLoader = new THREE.TextureLoader();

function loadTex(path, repeatX = 1, repeatY = 1) {
  const tex = texLoader.load(path);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(repeatX, repeatY);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function loadTexLinear(path, repeatX = 1, repeatY = 1) {
  const tex = texLoader.load(path);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(repeatX, repeatY);
  return tex;
}

// ── Material definitions ─────────────────────────────────────
// Spruce exterior (shell staves)
const spruceMat = new THREE.MeshStandardMaterial({
  map: loadTex('/textures/wood_planks_dirt_diff.jpg', 4, 1),
  roughnessMap: loadTexLinear('/textures/wood_planks_dirt_rough.jpg', 4, 1),
  normalMap: loadTexLinear('/textures/wood_planks_dirt_unknown.jpg', 4, 1),
  roughness: 0.85,
  side: THREE.DoubleSide,
});

// Spruce walls (front/back)
const wallMat = new THREE.MeshStandardMaterial({
  map: loadTex('/textures/raw_plank_wall_diff.jpg', 2, 2),
  roughnessMap: loadTexLinear('/textures/raw_plank_wall_rough.jpg', 2, 2),
  normalMap: loadTexLinear('/textures/raw_plank_wall_unknown.jpg', 2, 2),
  roughness: 0.8,
  side: THREE.DoubleSide,
});

// Shingles (roof)
const shinglesMat = new THREE.MeshStandardMaterial({
  map: loadTex('/textures/roof_09_diff.jpg', 4, 4),
  roughnessMap: loadTexLinear('/textures/roof_09_rough.jpg', 4, 4),
  normalMap: loadTexLinear('/textures/roof_09_unknown.jpg', 4, 4),
  roughness: 0.9,
  color: new THREE.Color(0x444444),
});

// Black trim
const trimMat = new THREE.MeshStandardMaterial({
  color: 0x1a1a1a,
  roughness: 0.5,
  metalness: 0.3,
});

// Cradle / leg wood
const legMat = new THREE.MeshStandardMaterial({
  map: loadTex('/textures/wooden_planks_diff.jpg', 1, 1),
  roughnessMap: loadTexLinear('/textures/wooden_planks_rough.jpg', 1, 1),
  normalMap: loadTexLinear('/textures/wooden_planks_unknown.jpg', 1, 1),
  roughness: 0.8,
});

// Floor duckboard
const floorMat = new THREE.MeshStandardMaterial({
  map: loadTex('/textures/wood_planks_diff.jpg', 2, 2),
  roughnessMap: loadTexLinear('/textures/wood_planks_arm.jpg', 2, 2),
  normalMap: loadTexLinear('/textures/wood_planks_nor.jpg', 2, 2),
  roughness: 0.75,
});

// Alder bench wood
const benchMat = new THREE.MeshStandardMaterial({
  map: loadTex('/textures/finewood_diff.jpg', 2, 1),
  roughnessMap: loadTexLinear('/textures/finewood_rough.jpg', 2, 1),
  normalMap: loadTexLinear('/textures/finewood_nor.jpg', 2, 1),
  roughness: 0.6,
  color: new THREE.Color(0xdec8a0),
});

// Porch seats
const porchMat = new THREE.MeshStandardMaterial({
  map: loadTex('/textures/brown_planks_09_diff.jpg', 1, 1),
  roughnessMap: loadTexLinear('/textures/brown_planks_09_rough.jpg', 1, 1),
  normalMap: loadTexLinear('/textures/brown_planks_09_unknown.jpg', 1, 1),
  roughness: 0.75,
});

// Vent metal
const ventMat = new THREE.MeshStandardMaterial({
  color: 0x555555,
  roughness: 0.4,
  metalness: 0.7,
});

// Stone base
const stoneMat = new THREE.MeshStandardMaterial({
  color: 0x3a3a3a,
  roughness: 0.9,
  metalness: 0.1,
});

// Heater metal
const heaterMat = new THREE.MeshStandardMaterial({
  color: 0x222222,
  roughness: 0.3,
  metalness: 0.8,
});

// Sauna stones
const stoneSaunaMat = new THREE.MeshStandardMaterial({
  color: 0x6b6b6b,
  roughness: 0.95,
  metalness: 0.05,
});

// Chimney steel
const chimneyMat = new THREE.MeshStandardMaterial({
  color: 0xcccccc,
  roughness: 0.2,
  metalness: 0.9,
});

// Glass material
const glassMat = new THREE.MeshPhysicalMaterial({
  transparent: true,
  opacity: 0.25,
  roughness: 0.05,
  transmission: 0.92,
  ior: 1.5,
  thickness: 0.01,
  color: 0xffffff,
  side: THREE.DoubleSide,
});

// Door frame / handle metal
const doorFrameMat = new THREE.MeshStandardMaterial({
  color: 0x1a1a1a,
  roughness: 0.35,
  metalness: 0.8,
});

// ── Material mapping by node name ────────────────────────────
const meshMatMap = {
  // Exterior shell
  stave_body: spruceMat,
  shell_outer: spruceMat,

  // Walls
  front_wall: wallMat,
  back_wall: wallMat,
  front_wall_mesh: wallMat,

  // Wall rings / trim
  front_wall_ring: trimMat,
  back_wall_ring: trimMat,
  front_wall_ring_mesh: trimMat,

  // Roof
  roof_shingles: shinglesMat,

  // Cradles / legs
  cradle_front: legMat,
  cradle_middle: legMat,
  cradle_back: legMat,

  // Vents
  louvered_vent_back_1: ventMat,
  louvered_vent_back_2: ventMat,

  // Floor
  floor_duckboard: floorMat,

  // Benches
  bench_back_upper: benchMat,
  bench_back_lower: benchMat,
  bench_left_upper: benchMat,
  bench_left_lower: benchMat,
  bench_support: benchMat,
  'bench_support.001': benchMat,
  'bench_support.002': benchMat,
  'bench_support.003': benchMat,
  'bench_support.004': benchMat,

  // Heater
  heater_base: stoneMat,
  heater_body: heaterMat,
  heater_glass: glassMat,
  heater_basket: heaterMat,
  heater_stones: stoneSaunaMat,

  // Chimney
  chimney_tank: chimneyMat,
  chimney_pipe: chimneyMat,
  chimney_cap: chimneyMat,
  chimney_cap_support: chimneyMat,

  // Door
  door_panel: doorFrameMat,
  door_glass: glassMat,
  door_frame_vmullion_1: doorFrameMat,
  door_frame_vmullion_2: doorFrameMat,
  door_frame_hmullion: doorFrameMat,
  door_handle: chimneyMat,

  // Porch seats
  porch_seat_left: porchMat,
  porch_seat_right: porchMat,
};

// ── Loading indicator ────────────────────────────────────────
const loadingEl = document.getElementById('loading');
const loadingText = loadingEl ? loadingEl.querySelector('span') : null;

// ── Load GLB Model ───────────────────────────────────────────
const gltfLoader = new GLTFLoader();
let saunaModel = null;

gltfLoader.load(
  '/models/sauna_model.glb',
  (gltf) => {
    const model = gltf.scene;
    saunaModel = model;

    // Apply textures by mesh name
    model.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;

        const mat = meshMatMap[child.name];
        if (mat) {
          child.material = mat;
        } else {
          // Fallback: keep original but ensure double-sided
          if (child.material) {
            child.material.side = THREE.DoubleSide;
          }
        }
      }
    });

    // Auto-center and position the model
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    model.position.x -= center.x;
    model.position.z -= center.z;
    model.position.y -= box.min.y;

    controls.target.set(0, size.y / 2, 0);
    const maxDim = Math.max(size.x, size.y, size.z);
    camera.position.set(maxDim * 1.5, maxDim * 0.8, maxDim * 1.8);
    controls.update();

    scene.add(model);

    // Hide loading indicator
    if (loadingEl) {
      loadingEl.style.opacity = '0';
      setTimeout(() => loadingEl.style.display = 'none', 500);
    }
  },
  (progress) => {
    if (loadingText) {
      const pct = progress.total > 0
        ? Math.round((progress.loaded / progress.total) * 100)
        : Math.round(progress.loaded / 1024);
      loadingText.textContent = `Laadimine... ${progress.total > 0 ? pct + '%' : pct + 'KB'}`;
    }
  },
  (error) => {
    console.error('Error loading GLB:', error);
    if (loadingText) loadingText.textContent = 'Viga laadimisel.';
  }
);

// ── Render loop ──────────────────────────────────────────────
const clock = new THREE.Clock();

function animate() {
  const delta = clock.getDelta();

  // Slow auto-rotation
  if (saunaModel) {
    saunaModel.rotation.y += 0.1 * delta;
  }

  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();

// ── Fullscreen toggle ────────────────────────────────────────
const fullscreenBtn = document.getElementById('fullscreen-btn');
if (fullscreenBtn) {
  fullscreenBtn.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.body.requestFullscreen().catch(err => {
        console.warn(`Error attempting to enable fullscreen: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  });
}

// ── Resize handling ──────────────────────────────────────────
window.addEventListener('resize', () => {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h, false);
});
