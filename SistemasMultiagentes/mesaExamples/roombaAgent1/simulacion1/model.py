import mesa
from mesa.discrete_space import OrthogonalMooreGrid
from mesa.time import BaseScheduler

from .agent import RoomCell, RoombaAgent, ObstacleAgent


class RoombaModel(mesa.Model):
    """
    Modelo del entorno de limpieza para una Roomba.
    """

    def __init__(self, width=20, height=20,
                 dirt_prob=0.3, obstacle_prob=0.1, seed=None):

        super().__init__(seed=seed)

        self.width = width
        self.height = height

        # Grid que permite 2 agentes por celda: RoomCell y Roomba
        self.grid = OrthogonalMooreGrid((width, height), capacity=2, random=self.random)

        # Scheduler clásico de Mesa
        self.schedule = BaseScheduler(self)

        # Inicializar celdas
        self._init_cells(dirt_prob, obstacle_prob)

        # Crear la Roomba en el cargador
        self.roomba = RoombaAgent(self, pos=(1, 1))
        self.grid.place_agent(self.roomba, (1, 1))
        self.schedule.add(self.roomba)

        self.running = True
        self.steps = 0
        self.max_steps = 1000  # límite de seguridad

        # Recolector de datos
        self.datacollector = mesa.DataCollector(
            {
                "CleanPct": lambda m: m.percent_clean(),
                "DirtyCells": lambda m: m.count_state("Dirty"),
                "Battery": lambda m: m.roomba.battery,
                "Moves": lambda m: m.roomba.moves,
            }
        )

        self.datacollector.collect(self)

    def _init_cells(self, dirt_prob, obstacle_prob):
        """
        Inicializa la grilla con:
        - una celda cargador en (1,1)
        - celdas sucias o limpias
        - (por ahora) obstáculos como estado dentro de RoomCell
        """

        for x in range(self.width):
            for y in range(self.height):

                # Celda base
                if (x, y) == (1, 1):
                    cell = RoomCell(self, (x, y), state="Charger")
                else:
                    r = self.random.random()
                    if r < obstacle_prob:
                        cell = RoomCell(self, (x, y), state="Obstacle")
                    elif r < obstacle_prob + dirt_prob:
                        cell = RoomCell(self, (x, y), state="Dirty")
                    else:
                        cell = RoomCell(self, (x, y), state="Clean")

                self.grid.place_agent(cell, (x, y))

    def step(self):
        """Avanza el modelo un paso."""

        self.schedule.step()          # Ejecuta step() de los agentes
        self.datacollector.collect(self)
        self.steps += 1

        # Condiciones de parada
        if self.steps >= self.max_steps:
            self.running = False

        if self.count_state("Dirty") == 0:
            self.running = False

    def count_state(self, state):
        """Cuenta cuántas RoomCells están en un estado dado."""
        count = 0
        for cell in self.grid.agents:
            if isinstance(cell, RoomCell) and cell.state == state:
                count += 1
        return count

    def percent_clean(self):
        total = self.width * self.height
        dirty = self.count_state("Dirty")
        return (total - dirty) / total
