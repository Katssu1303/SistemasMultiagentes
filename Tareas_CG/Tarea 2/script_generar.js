const fs = require("fs");

// Inicializr variables
let vertices = []; // [ base0, cima0, base1, cima1, base2, cima2, base3, cima3, ... ]
let normales = [];
let faces = [];

// Obtener valores (input) para hacer los cálculos
const numLados = parseInt(process.argv[2]) || 8;
const altura = parseFloat(process.argv[3]) || 6.0;
const radioBase = parseFloat(process.argv[4]) || 1.0;
const radioCima = parseFloat(process.argv[5]) || 0.8;

console.log(`Generando modelo con:
Lados = ${numLados}
Altura = ${altura}
Radio base = ${radioBase}
Radio cima = ${radioCima}
`);

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

// Calcular vértices de las bases dependierndo del número de lados
for (let i = 0; i < numLados; i++) {
  // θ= numLados/2π -> usar i para el ángulo del vértice
  const angulo = (i / numLados) * Math.PI * 2;

  // x=cos(θ)*r z=sin(θ)*r
  const xBase = Math.cos(angulo) * radioBase;
  const zBase = Math.sin(angulo) * radioBase;
  const xCima = Math.cos(angulo) * radioCima;
  const zCima = Math.sin(angulo) * radioCima;

  // Para cada lado i guardar 2 vértices(bas y cima) para ver la unión después
  vertices.push([xBase, 0, zBase]); // agregar base -> (x,0,z)
  vertices.push([xCima, altura, zCima]); // agregar cima -> (x, h, z)
}

console.log(vertices);

// Calcular vectores normales para cada cara -> par de lado
for (let i = 0; i < numLados; i++) {
  // Como se tienen guardados 2 vétices usar * 2
  const base_actual = i * 2;
  const cima_actual = i * 2 + 1;
  // Usar % numLados para que al final regrese al 0 y cerrar el círculo
  const base_siguiente = ((i + 1) % numLados) * 2;

  const v0 = vertices[base_actual]; // punto en la base del lado actual
  const v1 = vertices[cima_actual]; // punto en la cima del mismo lado
  const v2 = vertices[base_siguiente]; // punto en la base del siguiente lado

  // normal de la cara lateral
  const borde_vertical = restar(v1, v0); // vector que sube verticalmente
  const borde_lateral = restar(v2, v0); // vector que va hacia el siguiente vértice de la base
  const n = normalizar(cruz(borde_vertical, borde_lateral));

  // misma normal para los 4 vértices del cuadrado lateral -> ccada lado tiene dos vértices: vértice base - vértice cima
  normales.push(n);
  normales.push(n);
}

// Generar caras laterales (triángulos) -> Dos tríangulos para formar cada lado
//  (base_i, base_{i+1}, cima_i)
//  (cima_i, base_{i+1}, cima_{i+1})
for (let i = 0; i < numLados; i++) {
  const base_actual = i * 2;
  const cima_actual = i * 2 + 1;

  const base_siguiente = ((i + 1) % numLados) * 2; // vértice base siguiente
  const cima_siguiente = base_siguiente + 1; // vértice cima siguiente

  const normal = i + 1;

  // Triángulo 1
  faces.push([base_actual, base_siguiente, cima_actual, normal]);
  // Triángulo 2
  faces.push([cima_actual, base_siguiente, cima_siguiente, normal]);
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
out += `# OBJ file building_${numLados}_${altura}_${radioBase}_${radioCima}.obj\n`;
out += `# ${vertices.length} vertices\n`;

// Vértices
vertices.forEach((v) => {
  out += `v ${v[0].toFixed(4)} ${v[1].toFixed(4)} ${v[2].toFixed(4)}\n`;
});

// Normales
out += `# ${normales.length} normals\n`;
normales.forEach((n) => {
  out += `vn ${n[0].toFixed(4)} ${n[1].toFixed(4)} ${n[2].toFixed(4)}\n`;
});

// Caras
out += `# ${faces.length} faces\n`;
faces.forEach((f) => {
  const [v1, v2, v3, ni] = f;
  out += `f ${v1}//${ni} ${v2}//${ni} ${v3}//${ni}\n`;
});

// Guardar archivo
const filename = `building_${numLados}_${altura}_${radioBase}_${radioCima}.obj`;
fs.writeFileSync(filename, out);

console.log("Archivo generado:", filename);
