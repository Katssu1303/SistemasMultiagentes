"use strict";

//import * as twgl from "twgl-base.js";
import * as twgl from "twgl.js";
import { pinguinShape, pivotShape } from "./Pinguin";
import { M3 } from "./A01781097-2d-libs";
import GUI from "lil-gui";

// Vertex Shader as a string
const vsGLSL = `#version 300 es
in vec2 a_position;
in vec4 a_color;

uniform mat3 u_matrix;

out vec4 v_color;

void main() {
    // Aplicar la matriz 3x3 al vector 
    vec3 pos = u_matrix * vec3(a_position, 1.0);
    // Pasar a coordenadas de clipspace
    gl_Position = vec4(pos.xy, 0.0, 1.0);
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

const objects = {
  model: {
    transforms: {
      t: {
        x: 0,
        y: 0,
        z: 0,
      },
      rr: {
        x: 0,
        y: 0,
        z: 0,
      },
      s: {
        x: 1,
        y: 1,
        z: 1,
      },
    },
    pivot: {
      x: 0,
      y: 0,
      color: [0, 0.3, 0.7, 1],
    },
  },
};

function main() {
  //
  const canvas = document.querySelector("canvas");
  const gl = canvas.getContext("webgl2");
  twgl.resizeCanvasToDisplaySize(gl.canvas);
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

  setupUI(gl);

  const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

  // Pinguino
  const pinguin = pinguinShape();
  const bufferInfoPinguin = twgl.createBufferInfoFromArrays(gl, pinguin);
  const vaoPinguin = twgl.createVAOFromBufferInfo(
    gl,
    programInfo,
    bufferInfoPinguin
  );

  // Pivote
  const arraysPivot = pivotShape(objects.model.pivot.color);
  const bufferInfoPivot = twgl.createBufferInfoFromArrays(gl, arraysPivot);
  const vaoPivot = twgl.createVAOFromBufferInfo(
    gl,
    programInfo,
    bufferInfoPivot
  );

  drawScene(
    gl,
    vaoPinguin,
    programInfo,
    bufferInfoPinguin,
    vaoPivot,
    bufferInfoPivot
  );
}

// Function to do the actual display of the objects
function drawScene(
  gl,
  vaoPinguin,
  programInfo,
  bufferInfo,
  vaoPivot,
  bufferInfoPivot
) {
  let translate = [objects.model.transforms.t.x, objects.model.transforms.t.y];
  let angle_radians = objects.model.transforms.rr.z;
  let scale = [objects.model.transforms.s.x, objects.model.transforms.s.y];
  let pivot = [objects.model.pivot.x, objects.model.pivot.y];

  // Create transform matrices - modelo
  const scaMat = M3.scale(scale);
  const rotMat = M3.rotation(angle_radians);
  const traMat = M3.translation(translate);

  // Pivote
  // Tasladar hacia el pivote
  const traPivot = M3.translation(pivot);
  //Trasladar desde el pivote hacia el origen
  const traNegPivot = M3.translation([-pivot[0], -pivot[1]]);

  // Transformaciones para el pinguino con base en el pivote
  // Matriz compuesta: T * R * S
  // M = T(model) * T(pivot) * R * S * T(-pivot)
  let pinguinTransforms = M3.identity();
  pinguinTransforms = M3.multiply(traNegPivot, pinguinTransforms);
  pinguinTransforms = M3.multiply(scaMat, pinguinTransforms);
  pinguinTransforms = M3.multiply(rotMat, pinguinTransforms);
  pinguinTransforms = M3.multiply(traPivot, pinguinTransforms);
  pinguinTransforms = M3.multiply(traMat, pinguinTransforms);

  let pivotTransforms = M3.translation(pivot);

  gl.useProgram(programInfo.program);

  // Pinguin
  twgl.setUniforms(programInfo, {
    u_matrix: pinguinTransforms,
  });
  gl.bindVertexArray(vaoPinguin);
  twgl.drawBufferInfo(gl, bufferInfo);

  // Pivot
  twgl.setUniforms(programInfo, {
    u_matrix: pivotTransforms,
  });
  gl.bindVertexArray(vaoPivot);
  twgl.drawBufferInfo(gl, bufferInfoPivot);

  requestAnimationFrame(() =>
    drawScene(
      gl,
      vaoPinguin,
      programInfo,
      bufferInfo,
      vaoPivot,
      bufferInfoPivot
    )
  );
}

// Crear y definir interfaz de usuario
function setupUI(gl) {
  const gui = new GUI();

  const traFolder = gui.addFolder("Translation");
  traFolder.add(objects.model.transforms.t, "x", -1, 1);
  traFolder.add(objects.model.transforms.t, "y", -1, 1);

  const rotFolder = gui.addFolder("Rotation");
  //rango desde 0 al angulo
  rotFolder.add(objects.model.transforms.rr, "z", 0, Math.PI * 2);

  const scaFolder = gui.addFolder("Scale");
  scaFolder.add(objects.model.transforms.s, "x", -5, 5);
  scaFolder.add(objects.model.transforms.s, "y", -5, 5);

  // Se espera un objeto y una propiedad de ese objeto
  // Crear parametro de translacion y como se va a mover, rango desde 0 al canvas
  const pivFolder = gui.addFolder("Pivot");
  pivFolder.add(objects.model.pivot, "x", -1, 1);
  pivFolder.add(objects.model.pivot, "y", -1, 1);

  //gui.addColor(objects.model, "color");
}

main();
