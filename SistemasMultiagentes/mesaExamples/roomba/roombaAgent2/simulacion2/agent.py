from mesa.discrete_space import CellAgent, FixedAgent
from collections import deque

class FloorCell(FixedAgent):
    """
    Static cell of the room.

    state:
        - "Dirty"
        - "Clean"
        - "Charger"
        - "Obstacle"
    """

    def __init__(self, model, cell, state: str = "Dirty") -> None:
        super().__init__(model)
        self.cell = cell
        self.state = state

    def step(self) -> None:
        pass


class RoombaAgent(CellAgent):
    """
    Cleaning agent.

    state:
        - "cleaning"
        - "returning"
        - "charging"
        - "idle"
        - "dead" (battery 0)
        - "comunicating"
    """

    def __init__(
        self,
        model,
        cell,
        battery_max = 100,
    ):
        super().__init__(model)
        self.cell = cell
        self.battery_max = battery_max
        self.battery = battery_max
        self.state = "cleaning"
        self.moves = 0
        self.cleaned_cells = 0

        # Posición inicial - estación de carga
        self.home_cell = cell
        # Estaciones de carga
        self.charging_stations = [cell]
        # Celdas visitadas
        self.visited_cells = set()
        # Guardar camino
        self.way = None
        # Guardar celdas visitadas para compartir
        self.visited_cells_sharing = set()


    def consume_battery(self, amount: int = 1) -> None:
        if self.battery <= 0:
            self.battery = 0
            self.state = "dead"
        else:
            self.battery = max(0, self.battery - amount)
            if self.battery == 0:
                self.state = "dead"

    def get_floor_here(self) -> FloorCell | None:
        """Return the FloorCell in the current cell."""
        for obj in self.cell.agents:
            if isinstance(obj, FloorCell):
                return obj
        return None

    # Detectar si hay obstaculos
    def is_obstacle_cell(self, candidate_cell) -> bool:
        for obj in candidate_cell.agents:
            if isinstance(obj, FloorCell) and obj.state == "Obstacle":
                return True
        return False
    
    
    def clean_or_move(self):
        floor = self.get_floor_here()
        if floor is None:
            self.move()
            return

        if floor.state == "Dirty":
            self.clean()
        else:
            self.move()

    def clean(self):
        floor = self.get_floor_here()
        if floor is not None and floor.state == "Dirty":
            floor.state = "Clean"
            self.cleaned_cells += 1
            self.consume_battery()

    def move(self):
        """
        Move randomly to a neighbor cell that is not an obstacle.
        """
        # Guardar en ambas listas
        self.visited_cells.add(self.cell)
        self.visited_cells_sharing.add(self.cell)

        # Validar si hay una FloorCell con estado "Obstacle" - si hay obstaculos (bool)
        safe_cells = self.cell.neighborhood.select(
            lambda c: not self.is_obstacle_cell(c)
        )

        if len(safe_cells) == 0:
            # Si no hay ninguna celda segura alrededor (todas son obstáculos) -> el agente no puede moverse.
            self.consume_battery()
            return

        # Elegir celdas en orden para que cumpla el objetivo de limpiar en el menor tiempo
        choose = self.choose_cells(safe_cells)

        if choose:
            target = self.random.choice(choose)
            self.cell = target
            self.moves += 1
            self.consume_battery()

    def choose_cells(self, disp_cells):
        """
        Choose the cell depending is the roomba knows it and its dirtiness
        """
        type_of_cell = {
            'unkwon_dirty': [],
            'unkwon': [],
            'known_dirty': [],
            'known': []
        }

        for cell in disp_cells:
            dirty = any(
                isinstance(obj, FloorCell) and obj.state == "Dirty"
                for obj in cell.agents
            )

            unknown = (cell not in self.visited_cells and cell not in self.visited_cells_sharing)

            # Condiciones para dar prioridad
            if dirty and unknown:
                type_of_cell['unkwon_dirty'].append(cell)
            elif not dirty and unknown:
                type_of_cell['unkwon'].append(cell)
            elif dirty and not unknown:
                type_of_cell['known_dirty'].append(cell)
            else:
                type_of_cell['known'].append(cell)
            
        for t in ['unkwon_dirty', 'unkwon', 'known_dirty', 'known']:
            if type_of_cell[t]:
                return type_of_cell[t]
        
        return disp_cells
    
    def communicate(self):
        """
        Shares information about charging cells and visited cells
        with neighboring RoombaAgents in the same cell.
        """
        roombas_neighbors = [
            obj for obj in self.cell.agents
            if isinstance(obj, RoombaAgent) and obj is not self
        ]

        for roomba in roombas_neighbors:

            # Compartir celdas de carga 
            # Roomba al vecino
            for charge_cell in self.charging_stations:
                if charge_cell not in roomba.charging_stations:
                    roomba.charging_stations.append(charge_cell)
            # Vecino a mi roomba
            for charge_cell in roomba.charging_stations:
                if charge_cell not in self.charging_stations:
                    self.charging_stations.append(charge_cell)
            # Compartir celdas visitadas
            # Roomba al vecino
            roomba.visited_cells_sharing.update(self.visited_cells)
            # Vecino a mi roomba
            self.visited_cells_sharing.update(roomba.visited_cells)

    def charge(self):
        """
        While on a charger, increase battery.
        """
        floor = self.get_floor_here()
        if floor is None:
            self.state = "returning"
            return
        #Buscar estación
        if floor.state == "Charger":
            self.battery = min(self.battery_max, self.battery + 5)
            # Guardar estación
            if self.cell not in self.charging_stations:
                self.charging_stations.append(self.cell)
            # Cuando la batería es mayor o igual a 50 volver a limpiar
            if self.battery >= 50:
                self.state = "cleaning"
                self.way = None
        else:
            # Not really on a charger → try to go back
            self.state = "returning"
            self.way = None

    def bfs_shortest_path(self):
        """
        Uses BFS to find the best path to the nearest charging station.
        """
        if not self.charging_stations:
            return None

        # Verificar si ya estoy en una estación
        floor = self.get_floor_here()
        if floor and floor.state == "Charger":
            return []

       # cola de doble extremo -> agregar al final y sacar del inicio para FIFO (First In, First Out)
        # metes rutas nuevas al final y sacas la ruta más antigua al principio
        # cola donde se guardan las rutas
        cola_rutas = deque()
        # conjunto de posiciones que ya fueron exploradas por el BFS ()
        visited = set()
        cola_rutas.append((self.cell, []))
        visited.add(self.cell)

        # Algoritmo BFS
        while cola_rutas:
            my_cell, way = cola_rutas.popleft()

            # Checar si esta celda es una estación CONOCIDA
            if my_cell in self.charging_stations:
                return way

            # Explorar vecinos
            for n in my_cell.neighborhood:
                if n not in visited and not self.is_obstacle_cell(n):

                    visited.add(n)
                    new_way = way + [n]
                    cola_rutas.append((n, new_way))

        # Si no se encuentra camino
        return None
    
    def move_way(self, way):
        """
        Move following the path created with BFS
        """
        if way and len(way) > 0:
            new_cell = way[0]
            self.cell = new_cell
            self.moves += 1
            self.consume_battery()  # Consumir batería al moverse


    def return_to_charger(self):
        """
        Return to the charger station
        """
        # Verificar si ya esta en una estación de carga y cambiar el estado
        floor = self.get_floor_here()
        if floor is not None and floor.state == "Charger":
            self.state = "charging"
            return
        
        # Calcular camino si no hay uno
        if self.way is None:
            self.way = self.bfs_shortest_path()
            if self.way is None:
                # No se encontró camino, moverse aleatoriamente
                safe_cells = self.cell.neighborhood.select(
                    lambda c: not self.is_obstacle_cell(c)
                )
                if safe_cells:
                    self.cell = self.random.choice(safe_cells)
                    self.moves += 1
                    self.consume_battery()
                return
        
        # Seguir el camino BFS paso a paso
        if self.way and len(self.way) > 0:
            self.move_way(self.way)
            # Eliminar la celda que ya recorrió
            self.way = self.way[1:]
            # Verificar si ya llegó al cargador
            floor = self.get_floor_here()
            if floor is not None and floor.state == "Charger":
                self.state = "charging"


    def step(self):
        # Si está muerto, no hace nada
        if self.state == "dead":
            return

        # Si batería baja y NO está cargando -> regresar
        if self.battery <= 20 and self.state not in ("returning", "charging"):
            self.state = "returning"
            self.way = None  # reset camino

        # 1. ESTADO: CHARGING
        if self.state == "charging":
            self.charge()  
            return         

        # 2. ESTADO: RETURNING
        if self.state == "returning":
            self.return_to_charger()
            return

        # 3. ESTADO: CLEANING
        if self.state == "cleaning":
            floor = self.get_floor_here()
            if floor and floor.state == "Dirty":
                self.clean()
            else:
                # No hay suciedad -> explorar
                self.move()
            return

        # 4. ESTADO: COMUNICATING
        if self.state == "comunicating":
            self.communicate()
            # Después de comunicar, vuelve a limpiar o explorar
            self.state = "cleaning"
            self.consume_battery()
            return

        # 5. ESTADO: MOVING (por defecto)
        self.move()  # movimiento normal con consumo de batería
        # Checar muerte
        if self.battery <= 0:
            self.state = "dead"