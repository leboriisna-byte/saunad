# Sauna 3D Model Specifications for Blender MCP

These specifications are derived from the reference blueprints and 3D renders. Use these exact details when generating the Blender Python script via MCP.

## 1. Overall Shape, Dimensions & Walls
- **Type**: Squircle/Rounded-Rectangular "Barrel-style" Sauna.
- **Outer Dimensions**:
  - Length (Depth): 2400 mm (2.4m) total.
  - Width: 2300 mm (2.3m).
  - Height: 2300 mm (2.3m).
- **Wall Thickness (Crucial)**: Hollow out the interior to a depth of 1745mm, leaving a front and back wall thickness of 77.5mm. The front porch overhang is exactly 500mm deep.
- **Base/Legs**: 3 wooden cradle supports under the sauna. Each support is 150mm wide. To fit within the 2400mm total length, there is a 30mm overhang at the very front and very back. The legs start 30mm inset from the edges, with 945mm spacing between them. The flat walkable floor width inside is 1800mm.
- **Roof/Sides**: The outer shell is wrapped with black/dark-grey hexagonal asphalt shingles covering the top and curving down the sides, leaving the exact bottom exposed wood.

## 2. Exterior Features
- **Front Facade**:
  - Left/Center: Large panoramic curved glass window taking up roughly 60% of the front facade, following the contour of the sauna wall.
  - Right Side: Full glass door with a black/dark metal frame (not wooden). There is minimal wooden wall on the front face, mostly just structural framing for the door and glass.
  - Porch/Overhang: The roof and side walls extend forward by 500mm to create a small porch.
  - Porch Seating: Two small wooden seats (each 540mm wide) fit on the left and right sides of the door on the porch.
  - Trim/Edges: The edges where the roof meets the front/back walls have black curved trim pieces.
- **Door Mechanics**: The glass door swings outward. Place the object origin (pivot point) on the right-side hinges so it opens correctly in Three.js.

## 3. Interior Layout (L-shaped)
- **Benches (L-Kujuline)**:
  - Layout: L-shaped configuration. Long section across the back wall, short section coming forward on the left side (under the panoramic window).
  - Back Wall Bench Depths: Top bench is 550mm depth. Lower bench is 590mm depth.
  - Left Side Bench Depths: The short section coming forward along the left side wall is deeper: both top and bottom tiers are 620mm deep.
  - Heights: Lower bench is 480mm from the floor. Top bench is roughly 420-450mm above the lower bench.
  - Material: Light sauna wood (e.g., Alder or Aspen) with horizontal slats.
- **Floor**: Flat section has a slatted wooden duckboard raised 250mm from the absolute bottom curve.
- **Lighting**: A continuous linear LED light strip runs along the inner frame of the panoramic window arch, wrapping from floor to ceiling.

## 4. Heater & Accessories
- **Heater**: Wood-burning stove placed on the right side of the interior.
  - Base: Stands on a protective dark metallic/stone base plate.
  - Design: Black/dark metal body with a glass fire-viewing door at the bottom, and a rock basket full of stones on top.
  - Water Tank/Chimney: A cylindrical stainless-steel water tank sits directly on the chimney pipe above the heater.
  - Chimney Top: The chimney stack protrudes straight through the roof, topped with a stainless steel rain cap.

## Prompt Instructions for Claude (Blender MCP)
Copy and paste this exact prompt to Claude to execute the build via Blender MCP:

```text
Please generate a Python script to model a 3D Sauna in Blender using the provided specifications, and execute it using the Blender MCP tool.

CRITICAL WORKFLOW REQUIREMENTS:
1. Materials MUST use standard Principled BSDF nodes. Do not use complex Blender-specific nodes, as they will turn invisible or break when exported to Three.js.
2. Once the model is generated and materials are assigned, automatically EXPORT the model as a `.glb` (GLTF Binary) file to the `public/models/sauna.glb` directory in my workspace.

MODELING INSTRUCTIONS (CRITICAL - DO NOT USE SUBDIVISION SURFACES TO MAKE THE SQUIRCLE):
1. The Squircle Shape: Do NOT use a subdivided cube or it will turn into a balloon. Create the 2.4m depth barrel by creating a rectangular profile (2.3m x 2.3m) and applying a Bevel to the 4 corners (Radius: ~0.8m) to create the flat-sided "squircle". Extrude this shape.
2. The Walls & Hollow Interior: Do not manually scale faces. Hollow out the interior using a Boolean difference modifier with a slightly smaller squircle (1745mm deep), leaving exactly 77.5mm for the front and back walls. The roof/porch overhangs 500mm at the front.
3. Front Facade & Panoramic Window: Do NOT just spawn rectangular frames. The left panoramic window MUST be cut into the curved wall using a Boolean operation so the glass perfectly follows the curve of the outer wall. It takes up 60% of the front width. 
4. The Door & Hinge: The glass door is on the right. Place the object origin (pivot point) of the door exactly on its right-side hinges so it swings outward properly in Three.js.
5. Base Cradles (Legs): Do not use intersecting triangles. Create 3 flat-bottomed rectangular wooden cradles (150mm wide) that curve inward at the top to perfectly match the bottom curve of the sauna. The legs start 30mm inset from the front/back edges and are spaced 945mm apart.
6. Porch Seats: Create two porch seats (540mm wide) outside the door. They must sit completely flush against the floor and wall—they cannot float or clip through geometry.
7. Interior Benches: L-shaped. Back wall section: 550mm top depth, 590mm lower depth. Left side section follows the curve: both top and bottom tiers are exactly 620mm deep.
8. Heater & Lighting: Wood-burning stove with rocks and water tank on the right. Add a linear LED strip (Emission shader, warm white) tracing the inside of the panoramic window frame.
9. Shingles: Separate the materials: Wood for the main structure, Asphalt Shingles for the outer top/side casing. The absolute bottom remains exposed wood.

Ensure all scale is applied (`Ctrl+A`) and dimensions precisely match the metric values provided (meters/millimeters).

THREE.JS INTEGRATION INSTRUCTIONS (To be executed by you after GLB generation):
Once the `public/models/sauna.glb` is generated, integrate it into the Three.js dev server:
1. Glass Material Tweaks: The glass materials from Blender won't look perfectly transparent in Three.js by default. In your Three.js code, target the glass meshes (panoramic window and door), and assign them a `MeshPhysicalMaterial`. Set `transparent: true`, `opacity: ~0.3`, `roughness: 0.1`, `transmission: 0.9`, and `ior: 1.5` so it looks like realistic glass.
2. LED Emission: Target the LED strip mesh. Ensure its material is a `MeshStandardMaterial` or `MeshPhysicalMaterial` with a warm white `emissive` color, and crank up the `emissiveIntensity` so it glows (consider adding a Bloom post-processing pass to the scene).
3. Door Interaction: Since you set the door's origin on its hinge, do NOT do any weird math to make it open. Just implement a simple rotation on its local Y-axis when the user interacts with it.
```
