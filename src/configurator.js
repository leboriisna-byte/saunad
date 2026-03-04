/**
 * Configurator logic — connects UI buttons to GLB mesh visibility.
 *
 * Mesh naming in the GLB:
 *   door_wooden, door_wooden_window
 *   door_fullglass, door_fullglass_frame
 *   door_panoramic
 *   heater_harvia, heater_harvia_stones
 *   heater_huum, heater_huum_base
 *   roof_shingles
 *   roof_metal
 */

const CONFIG_GROUPS = {
  door: ['wooden', 'fullglass', 'panoramic'],
  heater: ['harvia', 'huum'],
  roof: ['shingles', 'metal'],
};

const state = {
  door: 'wooden',
  heater: 'harvia',
  roof: 'shingles',
};

export function setupConfigurator(scene) {
  const buttons = document.querySelectorAll('.opt-btn');

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const group = btn.closest('.options').dataset.group;
      const option = btn.dataset.option;

      // Update state
      state[group] = option;

      // Update active button styling
      btn.closest('.options').querySelectorAll('.opt-btn').forEach((b) => {
        b.classList.remove('active');
      });
      btn.classList.add('active');

      // Toggle mesh visibility
      updateMeshVisibility(scene, group, option);
    });
  });

  // Apply initial visibility based on default state
  Object.keys(state).forEach((group) => {
    updateMeshVisibility(scene, group, state[group]);
  });
}

function updateMeshVisibility(scene, group, activeOption) {
  const allOptions = CONFIG_GROUPS[group];
  if (!allOptions) return;

  scene.traverse((child) => {
    if (!child.isMesh && !child.isGroup) return;
    const name = child.name.toLowerCase();

    // Check if this mesh belongs to any option in this group
    for (const opt of allOptions) {
      const prefix = `${group}_${opt}`;
      if (name.startsWith(prefix)) {
        // Show if it matches the active option, hide otherwise
        child.visible = (opt === activeOption);
        break;
      }
    }
  });
}

export function getState() {
  return { ...state };
}
