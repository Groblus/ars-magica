import * as THREE from 'three';
import './styles.css';

type FocusKey = 'notebook' | 'books' | 'arts' | 'window';

interface FocusPoint {
  key: FocusKey;
  label: string;
  copy: string;
  x: number;
  y: number;
}

const focusPoints: FocusPoint[] = [
  {
    key: 'notebook',
    label: 'Open manuscript',
    copy: 'Character identity begins here. The future builder writes choices into this page.',
    x: 50,
    y: 72,
  },
  {
    key: 'books',
    label: 'Rules shelf',
    copy: 'Rules references will come from the existing corpus data, not a parallel lore store.',
    x: 79,
    y: 35,
  },
  {
    key: 'arts',
    label: 'Armillary',
    copy: 'Arts and magical style should feel like aligning a brass instrument, not filling a grid.',
    x: 20,
    y: 49,
  },
  {
    key: 'window',
    label: 'Tribunal view',
    copy: 'Origin and covenant context live at the threshold between room and Mythic Europe.',
    x: 50,
    y: 29,
  },
];

const app = document.querySelector<HTMLDivElement>('#app');
if (!app) {
  throw new Error('Missing #app root.');
}

app.innerHTML = `
  <main class="sanctum">
    <canvas class="sanctum__canvas" aria-hidden="true"></canvas>
    <section class="sanctum__painting" aria-label="Wizard study fallback painting">
      <img id="hero-image" src="${import.meta.env.BASE_URL}reference/hero.jpg" alt="Painterly wizard study with open manuscript" />
      <div class="sanctum__vignette"></div>
      <div class="sanctum__hotspots">
        ${focusPoints
          .map(
            (point) => `
              <button class="hotspot" style="left:${point.x}%;top:${point.y}%" data-focus="${point.key}">
                <span>${point.label}</span>
              </button>
            `,
          )
          .join('')}
      </div>
    </section>
    <section class="notebook" aria-live="polite">
      <p class="notebook__eyebrow">Ars Magica sanctum experiment</p>
      <h1 id="focus-title">Open manuscript</h1>
      <p id="focus-copy">Character identity begins here. The future builder writes choices into this page.</p>
      <dl>
        <div><dt>Mode</dt><dd>Painting fallback</dd></div>
        <div><dt>Source</dt><dd>Three.js/Spark-ready shell</dd></div>
        <div><dt>Next</dt><dd>Approved view reconstruction</dd></div>
      </dl>
    </section>
  </main>
`;

const heroImage = document.querySelector<HTMLImageElement>('#hero-image');
heroImage?.addEventListener('error', () => {
  heroImage.src = `${import.meta.env.BASE_URL}reference/hero-placeholder.svg`;
});

const title = document.querySelector<HTMLHeadingElement>('#focus-title');
const copy = document.querySelector<HTMLParagraphElement>('#focus-copy');

document.querySelectorAll<HTMLButtonElement>('.hotspot').forEach((button) => {
  button.addEventListener('click', () => {
    const focus = focusPoints.find((point) => point.key === button.dataset.focus);
    if (!focus || !title || !copy) return;
    title.textContent = focus.label;
    copy.textContent = focus.copy;
    document.querySelectorAll('.hotspot').forEach((item) => item.classList.remove('is-active'));
    button.classList.add('is-active');
  });
});

document.querySelector<HTMLButtonElement>('[data-focus="notebook"]')?.classList.add('is-active');

const canvas = document.querySelector<HTMLCanvasElement>('.sanctum__canvas');
if (!canvas) {
  throw new Error('Missing Three.js canvas.');
}

const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
camera.position.set(0, 0, 5);

const geometry = new THREE.PlaneGeometry(3.2, 2.0, 32, 18);
const material = new THREE.MeshBasicMaterial({
  color: 0xffd892,
  transparent: true,
  opacity: 0.11,
  wireframe: true,
});
const parallaxPlane = new THREE.Mesh(geometry, material);
parallaxPlane.position.set(0, 0, -0.4);
scene.add(parallaxPlane);

const resize = () => {
  const { innerWidth, innerHeight } = window;
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
};

window.addEventListener('resize', resize);
resize();

let pointerX = 0;
let pointerY = 0;
window.addEventListener('pointermove', (event) => {
  pointerX = (event.clientX / window.innerWidth - 0.5) * 2;
  pointerY = (event.clientY / window.innerHeight - 0.5) * 2;
});

const animate = () => {
  parallaxPlane.rotation.y += (pointerX * 0.035 - parallaxPlane.rotation.y) * 0.045;
  parallaxPlane.rotation.x += (-pointerY * 0.025 - parallaxPlane.rotation.x) * 0.045;
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
};

animate();
