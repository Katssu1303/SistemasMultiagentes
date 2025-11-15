"use strict";

import * as twgl from "twgl-base.js";

// Vertex Shader as a string
const vsGLSL = `#version 300 es
in vec4 a_position;
in vec4 a_color;

out vec4 v_color;

void main() {
    gl_Position = a_position;
    v_color = a_color;
}
`;

// Fragment Shader as a string
const fsGLSL = `#version 300 es
precision highp float;

in vec4 v_color;

out vec4 outColor;

void main() {
    outColor = v_color;
}
`;

function main() {
  const canvas = document.querySelector("canvas");
  const gl = canvas.getContext("webgl2");

  const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

  gl.useProgram(programInfo.program);

  const cara = generateData(64, 0.7, 0.0, 0.0, [0.3, 0.6, 1, 1]);
  const caraBuffer = twgl.createBufferInfoFromArrays(gl, cara);

  const ojoIzq = generateData(32, 0.1, -0.25, 0.25, [0, 0, 0.3, 1]);
  const ojoDer = generateData(32, 0.1, 0.25, 0.25, [0, 0, 0.3, 1]);

  const ojoIzqBuffer = twgl.createBufferInfoFromArrays(gl, ojoIzq);
  const ojoDerBuffer = twgl.createBufferInfoFromArrays(gl, ojoDer);

  //const pico = generateData(3, 0.2, 0.0, -0.1, [1, 0.8, 0.1, 1]);
  const pico = generateData(4, 0.2, 0.0, -0.1, [1, 0.8, 0.1, 1]);
  const picoBuffer = twgl.createBufferInfoFromArrays(gl, pico);

  const pupilaIzq = generateData(32, 0.08, -0.25, 0.25, [0, 0, 0, 1]);
  const pupilaDer = generateData(32, 0.08, 0.25, 0.25, [0, 0, 0, 1]);

  const pupilaIzqBuffer = twgl.createBufferInfoFromArrays(gl, pupilaIzq);
  const pupilaDerBuffer = twgl.createBufferInfoFromArrays(gl, pupilaDer);

  const reflejoIzq = generateData(20, 0.04, -0.2, 0.3, [1, 1, 1, 1]);
  const reflejoDer = generateData(20, 0.04, 0.2, 0.3, [1, 1, 1, 1]);

  const reflejoIzqBuffer = twgl.createBufferInfoFromArrays(gl, reflejoIzq);
  const reflejoDerBuffer = twgl.createBufferInfoFromArrays(gl, reflejoDer);

  //const vao = twgl.createVAOFromBufferInfo(gl, programInfo, bufferInfo);
  //console.log(vao);

  //gl.bindVertexArray(vao);

  gl.useProgram(programInfo.program);

  // Dibuja la cara
  twgl.setBuffersAndAttributes(gl, programInfo, caraBuffer);
  twgl.drawBufferInfo(gl, caraBuffer);

  // Dibuja pico
  twgl.setBuffersAndAttributes(gl, programInfo, picoBuffer);
  twgl.drawBufferInfo(gl, picoBuffer);

  // Dibuja ojo izquierdo
  twgl.setBuffersAndAttributes(gl, programInfo, ojoIzqBuffer);
  twgl.drawBufferInfo(gl, ojoIzqBuffer);

  // Dibuja ojo derecho
  twgl.setBuffersAndAttributes(gl, programInfo, ojoDerBuffer);
  twgl.drawBufferInfo(gl, ojoDerBuffer);

  // Dibuja pupila izquierda
  twgl.setBuffersAndAttributes(gl, programInfo, pupilaIzqBuffer);
  twgl.drawBufferInfo(gl, pupilaIzqBuffer);

  // Dibuja pupila derecho
  twgl.setBuffersAndAttributes(gl, programInfo, pupilaDerBuffer);
  twgl.drawBufferInfo(gl, pupilaDerBuffer);

  // Dibuja reflejo izquierdo
  twgl.setBuffersAndAttributes(gl, programInfo, reflejoIzqBuffer);
  twgl.drawBufferInfo(gl, reflejoIzqBuffer);

  // Dibuja reflejo derecho
  twgl.setBuffersAndAttributes(gl, programInfo, reflejoDerBuffer);
  twgl.drawBufferInfo(gl, reflejoDerBuffer);
}

// Create the data for the vertices of the polyton, as an object with two arrays
function generateData(sides, radious, cx, cy, color) {
  // The arrays are initially empty
  let arrays = {
    //Hacer carita
    //Primer circulo
    // Two components for each position in 2D
    a_position: { numComponents: 2, data: [] },
    // Four components for a color (RGBA)
    a_color: { numComponents: 4, data: [] },
    // Three components for each triangle, the 3 vertices
    indices: { numComponents: 3, data: [] },
  };

  // Initialize the center vertex, at the origin and with white color
  arrays.a_position.data.push(cx, cy); //centro
  arrays.a_color.data.push(...color);

  let angleStep = (2 * Math.PI) / sides; //circunferencia dividida entre lados pra obtener angulo
  // Loop over the sides to create the rest of the vertices
  for (let s = 0; s < sides; s++) {
    let angle = angleStep * s;
    // Generate the coordinates of the vertex - coordenadas polares (distancia y ángulo)
    let x = cx + radious * Math.cos(angle);
    let y = cy + radious * Math.sin(angle);
    arrays.a_position.data.push(x);
    arrays.a_position.data.push(y);
    arrays.a_color.data.push(...color);
    // Define the triangles, in counter clockwise order
    //Para los indices definir un triangulo
    arrays.indices.data.push(0); //indice 0
    arrays.indices.data.push(s + 1); //s es donde voy en la iteración
    arrays.indices.data.push(s + 2 <= sides ? s + 2 : 1); //crea la conexión
  }
  console.log(arrays);

  return arrays;
}

main();
