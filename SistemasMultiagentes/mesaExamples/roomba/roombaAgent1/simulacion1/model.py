import mesa
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid

from .agent import FloorCell, RoombaAgent


class RoombaModel(Model):
    """
    Cleaning environment for one or multiple Roombas
    """

    # Para que ShowSteps de Solara no truene si alguna vez ve la clase
    steps: int = 0

    def __init__(
        self,
        width=20,
        height=20,
        dirt_prob=0.3,
        obstacle_prob=0.1,
        num_agents=1,
        seed=42,
    ):
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.dirt_prob = dirt_prob
        self.obstacle_prob = obstacle_prob
        self.num_agents = num_agents

        # contador de pasos a nivel instancia
        self.steps = 0

        # Grid de discrete_space (OJO: pasamos self.random)
        self.grid = OrthogonalMooreGrid(
            (width, height),
            torus=False,
            random=self.random,
        )
        # alias para SolaraViz
        self.space = self.grid

        # DataCollector ANTES de crear agentes
        self.datacollector = DataCollector(
            model_reporters={
                "CleanPct": self.percent_clean,
                "DirtyCells": lambda m: m.count_cells_state("Dirty"),
                "CleanCells": lambda m: m.count_cells_state("Clean"),
                "ObstacleCells": lambda m: m.count_cells_state("Obstacle"),
                "AvgBattery": self.average_battery,
                "TotalMoves": self.total_moves,
            }
        )

        # Crear celdas del piso (FloorCell) y roombas
        self.create_floor_cells()
        self.create_roombas_and_chargers()

        # Recolectar datos iniciales
        self.datacollector.collect(self)

    # Crear piso: Dirty, Clean, Obstacle
    def create_floor_cells(self):
        for x in range(self.width):
            for y in range(self.height):

                # decidir obstáculo
                if self.random.random() < self.obstacle_prob:
                    state = "Obstacle"
                else:
                    # decidir suciedad
                    state = "Dirty" if self.random.random() < self.dirt_prob else "Clean"

                # obtenemos la celda de discrete_space
                cell = self.grid[x, y]

                # FloorCell es FixedAgent; asignarle la celda lo coloca en el grid
                FloorCell(self, cell=cell, state=state)

    # Crear roombas y estaciones de carga
    def create_roombas_and_chargers(self):
        # Colocar la estación de carga en la posición [1,1]
        charger_cell = self.grid[1, 1]
        
        # Verificar que la celda no sea un obstáculo
        if self.grid_contains_obstacle((1, 1)):
            # Si [1,1] es un obstáculo, cambiar a Clean primero
            for agent in charger_cell.agents:
                if isinstance(agent, FloorCell) and agent.state == "Obstacle":
                    agent.state = "Clean"
        
        # Cambiar la FloorCell de esa celda a Charger
        for agent in charger_cell.agents:
            if isinstance(agent, FloorCell):
                agent.state = "Charger"

        # Crear roombas encima del cargador
        for _ in range(self.num_agents):
            # RoombaAgent es CellAgent: asignar cell la registra en esa celda
            RoombaAgent(self, cell=charger_cell)

    def grid_contains_obstacle(self, pos):
        """
        Bool -> devuelve True si la celda contiene un piso con estado Obstacle.
        pos es una tupla (x, y), pero aquí ya usamos la API nueva.
        """
        cell = self.grid[pos]  # OrthogonalMooreGrid.__getitem__ devuelve un Cell

        for agent in cell.agents:
            if isinstance(agent, FloorCell) and agent.state == "Obstacle":
                return True
        return False

    # Métricas
    def count_cells_state(self, state):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x, y]
                for obj in cell.agents:
                    if isinstance(obj, FloorCell) and obj.state == state:
                        count += 1
        return count

    def percent_clean(self):
        total = self.width * self.height
        clean = self.count_cells_state("Clean")
        chargers = self.count_cells_state("Charger")
        obstacles = self.count_cells_state("Obstacle")
        # Solo contar las celdas limpiables (ni obstáculos ni cargadores)
        cleanable = total - obstacles - chargers
        return (clean / cleanable) * 100 if cleanable > 0 else 0

    def average_battery(self):
        roombas = [agent for agent in self.agents if isinstance(agent, RoombaAgent)]
        if not roombas:
            return 0
        return sum(a.battery for a in roombas) / len(roombas)

    def total_moves(self):
        roombas = [agent for agent in self.agents if isinstance(agent, RoombaAgent)]
        return sum(a.moves for a in roombas)

    def step(self):
        # Ejecutar el step de todos los agentes (FloorCell + Roombas)
        self.agents.do("step")
        self.datacollector.collect(self)
        self.steps += 1