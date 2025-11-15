// Función para dibujal al pinguino (parte por parte)
function pinguinShape() {
  // Objeto del pinguino
  let pinguin = {
    cara: {
      sides: 64,
      color: [0.3, 0.6, 1, 1],
      x: 0,
      y: 0,
      radius: 0.7,
    },
    ojoIzq: {
      sides: 32,
      color: [0, 0, 0.3, 1],
      x: -0.25,
      y: 0.25,
      radius: 0.1,
    },
    ojoDer: {
      sides: 32,
      color: [0, 0, 0.3, 1],
      x: 0.25,
      y: 0.25,
      radius: 0.1,
    },
    pico: {
      sides: 4,
      color: [1, 0.8, 0.1, 1],
      x: 0,
      y: -0.1,
      radius: 0.2,
    },
    reflejoIzq: {
      sides: 20,
      color: [1, 1, 1, 1],
      x: -0.2,
      y: 0.3,
      radius: 0.04,
    },
    reflejoDer: {
      sides: 20,
      color: [1, 1, 1, 1],
      x: 0.2,
      y: 0.3,
      radius: 0.04,
    },
  };

  // Inicialización de los arreglos
  let arrays = {
    // Two components for each position in 2D -> [x0, y0, x1, y1, x2, y2]
    a_position: { numComponents: 2, data: [] },
    // Four components for a color (RGBA) - a = opacidad
    a_color: { numComponents: 4, data: [] },
    // Three components for each triangle, the 3 vertices -> como dibuja con base a triangulos almacena los índices de los vértices
    indices: { numComponents: 1, data: [] },
  };

  // Variable para guardad cuantos vértices acumulados hay
  let indexOffset = 0;
  // Recorrer objeto
  for (const pinguinPart in pinguin) {
    const part = pinguin[pinguinPart]; // Datos de la parte
    const { sides, radius, x: cx, y: cy, color } = part;

    // Vértice central (el centro del círculo o polígono)
    arrays.a_position.data.push(cx);
    arrays.a_position.data.push(cy);
    arrays.a_color.data.push(...color);

    const angleStep = (2 * Math.PI) / sides;

    for (let s = 0; s < sides; s++) {
      let angle = angleStep * s;

      // Sumar cx/cy para mover el crírculo a su lugar
      let vx = cx + radius * Math.cos(angle);
      let vy = cy + radius * Math.sin(angle);

      arrays.a_position.data.push(vx);
      arrays.a_position.data.push(vy);
      arrays.a_color.data.push(...color);

      // Vértices para formar cada triángulo
      arrays.indices.data.push(indexOffset + 0); // Siempre el mismo vértice
      arrays.indices.data.push(indexOffset + s + 1); // Vértice actual del borde
      arrays.indices.data.push(indexOffset + (s + 2 <= sides ? s + 2 : 1)); // Siguiente vértice del borde, si ya no hay siguiente vuelve al primero
    }

    indexOffset += sides + 1;
  }

  return arrays;
}

function pivotShape(color) {
  let arrays = {
    a_position: { numComponents: 2, data: [] },
    a_color: { numComponents: 4, data: [] },
    indices: { numComponents: 1, data: [] },
  };

  let sides = 4;
  const radius = 0.07;

  arrays.a_position.data.push(0);
  arrays.a_position.data.push(0);
  arrays.a_color.data.push(...color);

  let angleStep = (2 * Math.PI) / sides;

  for (let s = 0; s < sides; s++) {
    let angle = angleStep * s;

    // Coordenadas del vértice
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;

    arrays.a_position.data.push(x);
    arrays.a_position.data.push(y);
    arrays.a_color.data.push(...color);

    arrays.indices.data.push(0);
    arrays.indices.data.push(s + 1);
    arrays.indices.data.push(s + 2 <= sides ? s + 2 : 1);
  }
  return arrays;
}

export { pinguinShape, pivotShape };
