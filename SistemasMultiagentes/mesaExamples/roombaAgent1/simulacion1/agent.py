from mesa.discrete_space import CellAgent, FixedAgent
import random


class RoomCell(CellAgent):
    """
    Celda del cuarto.
    Estados posibles:
        - "Dirty"   -> sucia, debe limpiarse
        - "Clean"   -> limpia
        - "Charger" -> estación de carga
    """

    def __init__(self, model, pos, state="Dirty"):
        super().__init__(model)
        self.pos = pos
        self.state = state

    def step(self):
        pass


class RoombaAgent(CellAgent):
    """
    Agente Roomba encargado de limpiar.
    Estados posibles:
        - "cleaning"       -> limpiando
        - "returning"      -> regresando al cargador
        - "charging"       -> cargando batería
        - "idle"           -> sin hacer nada
        - "communicating"  -> hablando con otros agentes
    """

    def __init__(self, model, pos):
        super().__init__(model)
        self.pos = pos
        self.battery = 100
        self.state = "cleaning"
        self.moves = 0  # Contador de movimientos
        self.known_obstacles = set()

    def step(self):
        """Lógica principal de decisión del agente."""
        
        if self.state == "charging":
            self.charge_battery()
            return

        # Si la batería es baja deve volver a la estación
        # Decidir cuánta batería mínima necesita
        if self.battery <= 10 and self.state != "returning":
            self.state = "returning"

        if self.state == "returning":
            self.return_to_charger()
            return

        # limpiar o moverse
        if self.state == "cleaning":
            self.clean_or_move()

    # Función de carga
    def charge_battery(self):
        """
        Incrementa la batería mientras está en la estación.
        La Roomba puede decidir aleatoriamente cargar más
        incluso si ya tiene el mínimo necesario para salir.
        """
        cell = self.model.grid.get_cell_list_contents([self.pos])[0]

        # Verificar que está realmente sobre el cargador
        if cell.state == "Charger":
            # Incremento de carga
            self.battery = min(100, self.battery + 5)

            # Probabilidad de seguir cargando aunque ya esté arriba de 50
            prob_continuar_cargando = 0.4  # 40%

            # Condición para regresar a limpiar
            if self.battery >= 50:
                if random.random() > prob_continuar_cargando:
                    self.state = "cleaning"

        else:
            # Si no está sobre el cargador, forzar retorno
            self.state = "returning"

    # Función para regresar al cargador
    def return_to_charger(self):
        """
        Regresa al cargador usando BFS para encontrar el camino óptimo.
        Por ahora el cargador está en (1,1), pero eventualmente se usaran 
        todas las posiciones de las estaciones.
        """

        target = (1, 1)  # temporal: más adelante será dinámico

        # Calcular ruta
        path = self.bfs_shortest_path(self.pos, target)

        if not path or len(path) < 2:
            return  # No hay camino o ya está encima del cargador

        next_step = path[1]  # El primer paso REAL (path[0] = pos actual)

        # Mover al siguiente paso
        if self.model.grid.is_cell_empty(next_step):
            self.model.grid.move_agent(self, next_step)
            self.pos = next_step
            self.moves += 1
            self.battery -= 1

        # Si llegó al cargador
        if self.pos == target:
            self.state = "charging"
    
    # Función para encontrar el camino más corto
    def bfs_shortest_path(self, start, goal):
        # cola de doble extremo -> agregar al final y sacar del inicio para FIFO (First In, First Out)
        # metes rutas nuevas al final y sacas la ruta más antigua al principio
        from collections import deque

        # cola donde se guardan las rutas
        cola_rutas = deque([[start]])
        # conjunto de posiciones que ya fueron exploradas por el BFS ()
        visited = set([start])

        # mientras haya rutas pendientes en la cola, seguir explorando.
        while cola_rutas:
            path = cola_rutas.popleft()
            x, y = path[-1]

            if (x, y) == goal:
                return path

            neighbors = self.model.grid.get_neighborhood(
                (x, y), moore=True, include_center=False
            )

            for nx, ny in neighbors:

                # 1) Si es un obstáculo conocido -> evitar
                if (nx, ny) in self.known_obstacles:
                    continue

                # 2) Si ya visitamos -> ignorar
                if (nx, ny) in visited:
                    continue

                # 3) Si está vacío -> puedes caminar
                if self.model.grid.is_cell_empty((nx, ny)):
                    visited.add((nx, ny))
                    cola_rutas.append(path + [(nx, ny)])
                    continue

                # 4) Si es la meta -> permite entrar a esa celda
                if (nx, ny) == goal:
                    visited.add((nx, ny))
                    cola_rutas.append(path + [(nx, ny)])
                    continue

                # 5) Si es un obstáculo no detectado, lo detectas (guardas) ahora
                cell_contents = self.model.grid.get_cell_list_contents([(nx, ny)])
                for obj in cell_contents:
                    if isinstance(obj, ObstacleAgent):
                        # lo guardamos en memoria
                        self.known_obstacles.add((nx, ny))
                        continue
                        #break
        return None

    # Función elegir limpiar o moverse
    def clean_or_move(self):
        """
        Evalúa si la celda actual está sucia.
        Si está sucia: limpia.
        Si no: se mueve.
        """
        cell = self.model.grid.get_cell_list_contents([self.pos])[0]

        if cell.state == "Dirty":
            self.clean()
        else:
            self.move()

    # Función para limpiar
    def clean(self):
        """Limpia la celda actual si está sucia."""
        cell = self.model.grid.get_cell_list_contents([self.pos])[0]
        if cell.state == "Dirty":
            cell.state = "Clean"
            self.battery -= 1

   # Función para moverse
    def move(self):
        """Movimiento aleatorio a una celda libre disponible."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        free_spaces = [p for p in possible_steps if self.model.grid.is_cell_empty(p)]

        if free_spaces:
            new_pos = self.random.choice(free_spaces)
            self.model.grid.move_agent(self, new_pos)
            self.pos = new_pos
            self.moves += 1
            self.battery -= 1


class ObstacleAgent(FixedAgent):
    """
    Agente obstáculo. No realiza acciones.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass
