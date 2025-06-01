const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000,
);

const render = new THREE.WebGLRenderer({ antialias: true });
render.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(render.domElement);

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(0, 10, 10);
scene.add(light);

camera.position.z = 5;

const loader = new THREE.GLTFLoader();
const models_to_load = ["static/assets/3d/desk_optimized.glb"];

let current_index = 0;
function loadNextModel() {
  if (current_index >= models_to_load.length) {
    console.log("All models load");
    return;
  }
  const path = models_to_load[current_index];
  console.log("Loading model ${current_index + 1}: ${path}");
  loader.load(
    path,
    function (gltf) {
      scene.add(gltf.scene);
      gltf.scene.position.x = current_index * 3;
      current_index++;
      loadNextModel();
    },
    undefined,
    function (error) {
      console.error("Error loading model ${path}", error);
      current_index++;
      loadNextModel();
    },
  );
}

loadNextModel();

function animate() {
  requestAnimationFrame(animate);
  render.render(scene, camera);
}
