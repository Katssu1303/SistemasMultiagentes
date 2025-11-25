const fs = require("fs");

// Inicializar variables
let vertices = []; // [ base0, cima0, base1, cima1, base2, cima2, base3, cima3, ... ]
let normales = [];
let faces = [];

// Obtener valores (input) para hacer los cálculos
const numLados = parseInt(process.argv[2]) || 8;
const alturaSegmento = parseFloat(process.argv[3]) || 2.0;

// Lista de radios para cada nivel (de abajo hacia arriba)
// Formato: [radio_base, radio_nivel1, radio_nivel2, ..., radio_cima]
let radios = [];
if (process.argv.length > 4) {
  // Si se pasan radios como argumentos
  radios = process.argv.slice(4).map(parseFloat);
} else {
  // Valores por defecto (como en la imagen)
  radios = [1.0, 0.6, 0.8, 1.2, 0.8, 0.4];
}

// Función para normalizar los vectores
function normalizar(v) {
  const len = Math.hypot(v[0], v[1], v[2]);
  if (len === 0) return [0, 0, 0];
  return [v[0] / len, v[1] / len, v[2] / len];
}

function restar(a, b) {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}

// Función para producto cruz para generar normales de las paredes laterales
function cruz(a, b) {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0],
  ];
}

// Generar vértices por niveles
// Igual que antes -> primero se genera un vértice central, luego un anillo
for (let nivel = 0; nivel < radios.length; nivel++) {
  const radio = radios[nivel];
  const y = nivel * alturaSegmento;

  // Vértices del perímetro del nivel
  for (let i = 0; i < numLados; i++) {
    const angulo = (i / numLados) * Math.PI * 2;
    const x = Math.cos(angulo) * radio;
    const z = Math.sin(angulo) * radio;
    vertices.push([x, y, z]);
  }
}

// Agregar centro de la base al final
vertices.push([0, 0, 0]);

// Agregar centro de la cima al final
vertices.push([0, (radios.length - 1) * alturaSegmento, 0]);

// Normal hacia abajo para la base
normales.push([0, -1, 0]);

// Normal hacia arriba para la cima
normales.push([0, 1, 0]);

// Calcular normales para cada segmento lateral
for (let seg = 0; seg < radios.length - 1; seg++) {
  // Para cada lado del segmento
  for (let i = 0; i < numLados; i++) {
    // v0 = punto en el anillo inferior del segmento
    // v1 = punto en el anillo superior del segmento
    // v2 = siguiente punto en el nivel inferior (para cerrar el polígono)
    const v0_idx = seg * numLados + i;
    const v1_idx = (seg + 1) * numLados + i;
    const v2_idx = seg * numLados + ((i + 1) % numLados);

    const v0 = vertices[v0_idx];
    const v1 = vertices[v1_idx];
    const v2 = vertices[v2_idx];

    const borde_vertical = restar(v1, v0); // vector que sube verticalmente
    const borde_lateral = restar(v2, v0); // vector que va hacia el siguiente vértice de la base
    const n = normalizar(cruz(borde_vertical, borde_lateral));

    normales.push(n);
  }
}

// Índices para los centros (están al final del array de vértices)
const centroBaseIdx = vertices.length - 1; // penúltimo vértice
const centroCimaIdx = vertices.length; // último vértice

// Generar cara de la base (triángulos desde el centro hacia los vértices)
for (let i = 0; i < numLados; i++) {
  const v1 = i + 1; // +1 para índice obj
  const v2 = ((i + 1) % numLados) + 1;

  // Triángulo apuntando hacia abajo (winding order invertido)
  faces.push([centroBaseIdx, v2, v1, 1]);
}

// Generar cara de la cima (triángulos desde el centro hacia los vértices)
const ultimoNivel = radios.length - 1;
const offsetCima = ultimoNivel * numLados;

for (let i = 0; i < numLados; i++) {
  const v1 = offsetCima + i + 1; // +1 para índice OBJ
  const v2 = offsetCima + ((i + 1) % numLados) + 1;

  // Triángulo apuntando hacia arriba
  faces.push([centroCimaIdx, v1, v2, 2]);
}

// Generar caras laterales para cada segmento
for (let seg = 0; seg < radios.length - 1; seg++) {
  const offsetActual = seg * numLados;
  const offsetSiguiente = (seg + 1) * numLados;

  for (let i = 0; i < numLados; i++) {
    // Vértices del cuadrilátero (dividido en 2 triángulos)
    const v0 = offsetActual + i + 1;
    const v1 = offsetSiguiente + i + 1;
    const v2 = offsetActual + ((i + 1) % numLados) + 1;
    const v3 = offsetSiguiente + ((i + 1) % numLados) + 1;

    // Índice de la normal para este lado en este segmento
    const normalIdx = 3 + seg * numLados + i;

    // Triángulo 1: v0, v2, v1
    faces.push([v0, v2, v1, normalIdx]);

    // Triángulo 2: v1, v2, v3
    faces.push([v1, v2, v3, normalIdx]);
  }
}

// Generar archivo
// output archivo .obj
// v x y z, orden: vertice centro, vertice arriba (0,0,0), vertice abajo, vertice centro abajo (0, h, 0), vertices abajo (eje: v 0.0000 0.0000 0.0000 v 0.0000 6.0000 0.0000 v 1.0000 0.0000 0.0000)
// cantidad vertices normales
// vn x y z (eje: vn 0.0000 -1.0000 0.0000 vn 0.0000 1.0000 0.0000 vn 0.9234 0.0308 0.3825)
// cantidad de caras - f
// f num_vertice//num_diagonal en el orden que aparecen (eje: 5//1 1//1 3//1)
// aumentar num_diagonal en uno (eje: f 5//1 1//1 3//1 f 4//2 2//2 6//2 f 5//3 3//3 4//3)
let out = "";

// Header
out += `# OBJ file: building_${numLados}_${radios.length}seg.obj\n`;
out += `# ${vertices.length} vertices, ${normales.length} normals, ${faces.length} faces\n`;
out += `# Segments: ${radios.length}, Radii: [${radios.join(", ")}]\n\n`;

// Vértices
vertices.forEach((v) => {
  out += `v ${v[0].toFixed(4)} ${v[1].toFixed(4)} ${v[2].toFixed(4)}\n`;
});

out += "\n";

// Normales
normales.forEach((n) => {
  out += `vn ${n[0].toFixed(4)} ${n[1].toFixed(4)} ${n[2].toFixed(4)}\n`;
});

out += "\n";

// Caras
faces.forEach((f) => {
  const [v1, v2, v3, ni] = f;
  out += `f ${v1}//${ni} ${v2}//${ni} ${v3}//${ni}\n`;
});

// Guardar archivo
const filename = `building_${numLados}_${radios.length}seg.obj`;
fs.writeFileSync(filename, out);
