import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// ── Scene setup ──────────────────────────────────────────────
const canvas = document.getElementById('canvas3d');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf2ece6);

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
renderer.toneMappingExposure = 2.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// ── Lighting (wrap-around studio setup) ─────────────────────
// Strong ambient so no face is ever black
const ambientLight = new THREE.AmbientLight(0xffffff, 2.5);
scene.add(ambientLight);

// Hemisphere light - sky above, warm ground bounce
const hemiLight = new THREE.HemisphereLight(0xddeeff, 0xc8a882, 1.2);
scene.add(hemiLight);

// Key light - front-left above (illuminates the front wall!)
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

// Fill light - front-right (so both sides of front face get light)
const fillLight = new THREE.DirectionalLight(0xc8d8ff, 1.2);
fillLight.position.set(3, 3, 5);
scene.add(fillLight);

// Back light - gentle rim from behind
const rimLight = new THREE.DirectionalLight(0xffffff, 0.6);
rimLight.position.set(2, 4, -4);
scene.add(rimLight);

// Bottom fill - prevents dark undersides on cradles
const bottomLight = new THREE.DirectionalLight(0xffe8d0, 0.5);
bottomLight.position.set(0, -3, 2);
scene.add(bottomLight);

// ── Ground plane ─────────────────────────────────────────────
const groundGeo = new THREE.PlaneGeometry(20, 20);
const groundMat = new THREE.MeshStandardMaterial({
  color: 0xd8cfc5,
  roughness: 0.9,
});
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

// ── Loading indicator ────────────────────────────────────────
const loadingEl = document.getElementById('loading');

// ── Textures ─────────────────────────────────────────────────
const texLoader = new THREE.TextureLoader();

function loadTex(path, repeat = [4, 2]) {
  const tex = texLoader.load(path);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(repeat[0], repeat[1]);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function loadNormal(path, repeat = [4, 2]) {
  const tex = texLoader.load(path);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(repeat[0], repeat[1]);
  return tex;
}

// ── Textures (Polyhaven CC0) ────────────────────────────────
// raw_plank_wall - cylinder UV baked in Blender; repeat [1,1] lets UV drive tiling
const stave_diff = loadTex('/textures/raw_plank_wall_diff.jpg', [1, 1]);
const stave_rough = loadNormal('/textures/raw_plank_wall_rough.jpg', [1, 1]);

// walls - same texture, different repeat
const wall_diff = loadTex('/textures/raw_plank_wall_diff.jpg', [2, 2]);
const wall_rough = loadNormal('/textures/raw_plank_wall_rough.jpg', [2, 2]);

// door panels
const door_diff = loadTex('/textures/raw_plank_wall_diff.jpg', [1, 2]);
const door_rough = loadNormal('/textures/raw_plank_wall_rough.jpg', [1, 2]);

// door frame — same raw_plank_wall as front wall; repeat [1,1] since Blender UVs are physical-scale (1 UV = 10 cm)
const frame_diff = loadTex('/textures/raw_plank_wall_diff.jpg', [1, 1]);
const frame_rough = loadNormal('/textures/raw_plank_wall_rough.jpg', [1, 1]);

// roof_09 - asphalt/bitumen shingles
const roof_diff = loadTex('/textures/roof_09_diff.jpg', [4, 3]);
const roof_rough = loadNormal('/textures/roof_09_rough.jpg', [4, 3]);

// ── Materials ────────────────────────────────────────────────
// Spruce staves (same raw_plank_wall texture as the front face)
const spruceExtMat = new THREE.MeshStandardMaterial({
  map: stave_diff,
  roughnessMap: stave_rough,
  roughness: 0.65,
  color: 0xffffff,
  side: THREE.DoubleSide,
});

// End walls (vertical raw planks on circular faces)
const spruceWallMat = new THREE.MeshStandardMaterial({
  map: wall_diff,
  roughnessMap: wall_rough,
  roughness: 0.65,
  color: 0xffffff,
  side: THREE.DoubleSide,
});

// Door wood (vertical planks)
const doorWoodMat = new THREE.MeshStandardMaterial({
  map: door_diff,
  roughnessMap: door_rough,
  roughness: 0.6,
  color: 0xffffff,
  side: THREE.DoubleSide,
});

// Support cradle legs (same plank wood)
const legWoodMat = new THREE.MeshStandardMaterial({
  map: stave_diff,
  roughnessMap: stave_rough,
  roughness: 0.65,
  color: 0xffffff,
  side: THREE.DoubleSide,
});

// Clear glass (door window)
const glassMat = new THREE.MeshStandardMaterial({
  color: 0xc8dde8,
  transparent: true,
  opacity: 0.25,
  roughness: 0.05,
  metalness: 0.1,
  side: THREE.DoubleSide,
  depthWrite: false,
});

// Metal band (dark steel straps)
const metalBandMat = new THREE.MeshStandardMaterial({
  color: 0x2a2a2e,
  roughness: 0.35,
  metalness: 0.9,
  side: THREE.DoubleSide,
});

// Chimney pipe (stainless steel)
const chimneyMat = new THREE.MeshStandardMaterial({
  color: 0x888890,
  roughness: 0.2,
  metalness: 0.95,
  side: THREE.DoubleSide,
});

// Door frame — physical-scale UVs from Blender (1 UV = 10 cm), repeat [1,1] so Blender drives tiling
const doorFrameMat = new THREE.MeshStandardMaterial({
  map: frame_diff,
  roughnessMap: frame_rough,
  roughness: 0.65,
  color: 0xffffff,
  side: THREE.DoubleSide,
});

// Door handle (dark iron)
const handleMat = new THREE.MeshStandardMaterial({
  color: 0x1a1a1e,
  roughness: 0.35,
  metalness: 0.9,
  side: THREE.DoubleSide,
});

// Roof shingles (dark bitumen)
const shinglesMat = new THREE.MeshStandardMaterial({
  map: roof_diff,
  roughnessMap: roof_rough,
  roughness: 0.9,
  color: 0x666666,
  side: THREE.DoubleSide,
});

// Wall ring trim (slightly darker tint for contrast)
const ringMat = new THREE.MeshStandardMaterial({
  map: stave_diff,
  roughnessMap: stave_rough,
  roughness: 0.55,
  color: 0xddccbb,
  side: THREE.DoubleSide,
});

// Louvered vent (dark metal disc)
const louveredVentMat = new THREE.MeshStandardMaterial({
  color: 0x2a2a2e,
  roughness: 0.45,
  metalness: 0.8,
  side: THREE.DoubleSide,
});

// ── Material assignment by mesh name ─────────────────────────
// Order matters: more specific patterns first, then general ones
const meshMatMap = [
  { match: /^stave_/, mat: spruceExtMat },
  { match: /^front_wall_ring/, mat: ringMat },
  { match: /^back_wall_ring/, mat: ringMat },
  { match: /^front_overhang/, mat: spruceExtMat },
  { match: /^back_overhang/, mat: spruceExtMat },
  { match: /^front_wall/, mat: spruceWallMat },
  { match: /^back_wall/, mat: spruceWallMat },
  { match: /^door_panel/, mat: doorWoodMat },
  { match: /^door_frame/, mat: doorFrameMat },
  { match: /^door_glass/, mat: glassMat },
  { match: /^door_handle/, mat: handleMat },
  { match: /^chimney/, mat: chimneyMat },
  { match: /^roof_shingles/, mat: shinglesMat },
  { match: /^metal_band/, mat: metalBandMat },
  { match: /^cradle_/, mat: legWoodMat },
  { match: /^louvered_vent/, mat: louveredVentMat },
];

// ── Load GLB Model ───────────────────────────────────────────
const gltfLoader = new GLTFLoader();

gltfLoader.load(
  '/models/sauna_model.glb',
  (gltf) => {
    const model = gltf.scene;
    model.name = 'sauna';

    console.log('GLB loaded, traversing meshes...');

    // Replace GLB materials with our custom ones
    model.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;

        let matched = false;
        for (const { match, mat } of meshMatMap) {
          if (match.test(child.name)) {
            child.material = mat;
            matched = true;
            break;
          }
        }
        // Ensure unmatched meshes also render both sides
        if (!matched && child.material) {
          child.material.side = THREE.DoubleSide;
        }
        console.log(`  ${child.name} → ${matched ? 'MATCHED' : 'unmatched (DoubleSide applied)'}`);
      }
    });

    // Auto-center and position the model
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    console.log('Model bounds:', { center, size });

    // Center model horizontally, sit on ground plane
    model.position.x -= center.x;
    model.position.z -= center.z;
    model.position.y -= box.min.y; // sit on y=0

    // Update controls target to model center
    controls.target.set(0, size.y / 2, 0);

    // Position camera based on model size
    const maxDim = Math.max(size.x, size.y, size.z);
    camera.position.set(maxDim * 1.2, maxDim * 0.8, maxDim * 1.5);
    controls.update();

    // Adjust ground plane
    ground.position.y = 0;

    scene.add(model);

    // Hide loading indicator
    if (loadingEl) loadingEl.style.display = 'none';
    console.log('Model added to scene');
  },
  (progress) => {
    const pct = progress.total > 0
      ? Math.round((progress.loaded / progress.total) * 100)
      : Math.round(progress.loaded / 1024);
    if (loadingEl) loadingEl.textContent = `Loading model... ${progress.total > 0 ? pct + '%' : pct + 'KB'}`;
  },
  (error) => {
    console.error('Error loading GLB:', error);
    if (loadingEl) loadingEl.textContent = 'Error loading model: ' + error.message;
  }
);

// ── Render loop ──────────────────────────────────────────────
function animate() {
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();

// ── Resize handling ──────────────────────────────────────────
window.addEventListener('resize', () => {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h, false);
});
