import mesa
from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
#from mesa.time import BaseScheduler

from .agent import RoomCell, RoombaAgent, ObstacleAgent


class RoombaModel(Model):
    """
    Modelo del entorno de limpieza para una Roomba.
    """

    def __init__(self, width=8, height=8,
                 dirt_prob=0.5, obstacle_prob=0.2, seed=None, num_agents=1):

        super().__init__(seed=seed)
        self.seed = seed
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.grid = OrthogonalMooreGrid((width, height), torus=False)

        # Inicializar celdas sucias
        self.create_cells(dirt_prob)

        # Inicializar obstaculos de manera random
        all_cells = list(self.grid)
        num_obstacles = int(len(all_cells) * obstacle_prob)
        # Seleccionar celdas aleatorias sin repetición
        obstacle_cells = self.random.sample(all_cells, num_obstacles)
        # Crear obstáculos
        for cell in obstacle_cells:
            ObstacleAgent(self, cell=cell)

        # Crear los Roomba
        p = self.grid[1, 1]
        RoombaAgent.create_agents(
            self,
            self.num_agents,
            cell=p
            # De la lista de todas las celdas vacías de la grilla selecciona una celda aleatoria para cada agente
            #cell=self.random.choices(self.grid.empties.cells, k=self.num_agents)
        )


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

    def create_cells(self, dirt_prob):
        """
        Inicializa la grilla con:
        - una celda cargador en (1,1)
        - celdas sucias o limpias
        - (por ahora) obstáculos como estado dentro de RoomCell
        """
        # Recorrer las celdas del grid, una por una
        for cell in self.grid.all_cells:
            pos = cell.coordinate
            if pos == (1, 1):
                agent = RoomCell(self, state="Charger")
                self.grid.place_agent(agent, pos)
            else:
                if self.random.random() < dirt_prob:
                    agent = RoomCell(self, state="Dirty")
                else:
                    agent = RoomCell(self, state="Clean")

                self.grid.place_agent(agent, pos)

    def step(self):
        """Avanza el modelo un paso."""
        # Mezcla aleatoriamente el orden de los agentes y llama método "step" de cada agente
        self.agents.shuffle_do("step") 

        self.datacollector.collect(self)

        # Si no queda ningún agente con condición “Dirty”, entonces la simulación se detiene
        if self.count_type("Dirty") == 0:
            self.running = False

    @staticmethod
    def count_type(model, state):
        """Cuenta cuántas RoomCells están en un estado dado."""
        return len(model.agents.select(lambda x: x.condition == state))

    @staticmethod
    def percent_clean(self):
        total = self.width * self.height
        dirty = self.count_state("Dirty")
        return (total - dirty) / total
