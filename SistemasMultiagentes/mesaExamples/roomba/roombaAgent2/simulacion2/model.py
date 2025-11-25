import mesa
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid

from .agents import FloorCell, RoombaAgent


class RoombaModel(Model):
    """
    Cleaning environment for one or multiple Roombas
    """

    def __init__(
        self,
        width=20,
        height=20,
        dirt_prob=0.3,
        obstacle_prob=0.1,
        num_agents=1,
        seed=42,
        steps = 0

    ):
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.dirt_prob = dirt_prob
        self.obstacle_prob = obstacle_prob
        self.num_agents = num_agents

        # Grid (Mesa >= 3.0 usa 2 argumentos)
        self.grid = OrthogonalMooreGrid(width, height)

        # Program the scheduler
        self.schedule = mesa.time.RandomActivation(self)

        # Crear celdas del piso
        self.create_floor_cells()

        # Crear roombas y estación de carga
        self.create_roombas_and_chargers()

        # DataCollector
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "CleanPct": lambda m: self.percent_clean(),
                "DirtyCells": lambda m: self.count_cells_state("Dirty"),
                "CleanCells": lambda m: self.count_cells_state("Clean"),
                "ObstacleCells": lambda m: self.count_cells_state("Obstacle"),
                "AvgBattery": lambda m: self.average_battery(),
                "TotalMoves": lambda m: self.total_moves(),
            }
        )

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

                cell = (x, y)
                floor = FloorCell(self, cell=cell, state=state)

                # colocar en grid
                self.grid.place_agent(floor, (x, y))

                # activar en scheduler si tiene step()
                self.schedule.add(floor)


    # Crear roombas y estaciones de carga
    def create_roombas_and_chargers(self):
        # Seleccionar una celda aleatoria no obstáculo para la base
        free_cells = [
            (x, y) for x in range(self.width)
            for y in range(self.height)
            if not self.grid_contains_obstacle((x, y))
        ]

        if len(free_cells) == 0:
            raise ValueError("No hay celdas libres para colocar estaciones de carga.")

        # Elegir estación de carga principal
        charger_pos = self.random.choice(free_cells)

        # Cambiar la celda a Charger
        for agent in self.grid.get_cell_list_contents([charger_pos]):
            if isinstance(agent, FloorCell):
                agent.state = "Charger"

        # Crear roombas encima del cargador
        for _ in range(self.num_agents):
            roomba = RoombaAgent(self, cell=charger_pos)
            self.grid.place_agent(roomba, charger_pos)
            self.schedule.add(roomba)

    def grid_contains_obstacle(self, pos):
        """Bool -> devuelve True si la celda contiene un piso con estado obstacle."""
        x, y = pos
        contents = self.grid.get_cell_list_contents([pos])

        for agent in contents:
            if isinstance(agent, FloorCell) and agent.state == "Obstacle":
                return True

        return False
        
    # Métricas
    def count_cells_state(self, state):
        count = 0
        for x in range(self.width):
            for y in range(self.height):
                for obj in self.grid.get_cell_list_contents([(x, y)]):
                    if isinstance(obj, FloorCell) and obj.state == state:
                        count += 1
        return count

    def percent_clean(self):
        total = self.width * self.height
        clean = self.count_cells_state("Clean")
        return clean / total if total > 0 else 0

    def average_battery(self):
        roombas = [a for a in self.schedule.agents if isinstance(a, RoombaAgent)]
        if not roombas:
            return 0
        return sum(a.battery for a in roombas) / len(roombas)

    def total_moves(self):
        roombas = [a for a in self.schedule.agents if isinstance(a, RoombaAgent)]
        return sum(a.moves for a in roombas)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.steps += 1 