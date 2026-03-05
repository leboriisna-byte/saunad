Subject: Sauna .glb Model & Three.js Material Tweaks

Hey! 

The AI is generating the 3D sauna model now. It will automatically export to the repo as `public/models/sauna.glb`. 

I made sure the prompt forces the AI to use standard Principled BSDF nodes in Blender so the materials actually load in Three.js (no weird Blender-specific procedural nodes).

However, you'll need to make a few quick tweaks to the materials once you load the GLTF into the scene, since Blender's GLTF exporter doesn't perfectly translate glass and glows out-of-the-box:

1. **The Glass (Window & Door)**
   - You'll likely need to grab the glass material and manually tweak it so it looks like actual glass.
   - Set `transparent = true`, lower the `opacity` (around 0.2 - 0.4), and set `roughness` very low. You might also want to play with `transmission` and `ior` (around 1.5) if you're using `MeshPhysicalMaterial`.

2. **The LED Strip (Emission)**
   - There is a material for the LED strip wrapping the panoramic window. 
   - It has an emissive color set to a warm white, but you will need to crank up the `emissiveIntensity` in Three.js to give it a proper glow. (Adding a Bloom pass in post-processing will make this look amazing).

3. **The Door Hinge**
   - Good news: I explicitly instructed the AI to place the object origin for the glass door directly on its right-side hinges. 
   - You don't need to do any complex math or grouping to make the door open—just target the door mesh and rotate it on its local axis, and it should swing naturally.

Let me know if the scale feels off or if any meshes are named weirdly and we can adjust!
