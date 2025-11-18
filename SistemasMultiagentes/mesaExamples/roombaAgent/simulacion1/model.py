import mesa
from mesa.space import MultiGrid
#from mesa.time import BaseScheduler

from .agent import RoomCell, RoombaAgent


class RoombaModel(mesa.Model):
    """
    Roomba Cleaning Environment Model.
    """

    def __init__(self, width=20, height=20,
                 dirt_prob=0.3, obstacle_prob=0.1,
                 max_steps=500, seed=None):

        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.max_steps = max_steps

        # Grid with multiple agents per cell allowed
        self.grid = MultiGrid(width, height, torus=False)

        # Scheduler — simple because we only have 1 Roomba for now
        #self.schedule = BaseScheduler(self)

        # Initialize room cells (dirty / clean / obstacle / charger)
        self._init_cells(dirt_prob, obstacle_prob)

        # Initialize Roomba at the charger
        self.roomba = RoombaAgent(999, self, pos=(1, 1))
        self.grid.place_agent(self.roomba, (1, 1))
        self.schedule.add(self.roomba)

        self.running = True
        self.steps = 0

        # Data Collector
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
        Initialize the room grid with:
        - a fixed charger at (1,1)
        - dirty & clean cells
        - obstacles
        """
        uid = 0
        for x in range(self.width):
            for y in range(self.height):

                # Charger location
                if (x, y) == (1, 1):
                    cell = RoomCell(uid, self, (x, y), state="Charger")
                else:
                    r = self.random.random()
                    if r < obstacle_prob:
                        cell = RoomCell(uid, self, (x, y), state="Obstacle")
                    elif r < obstacle_prob + dirt_prob:
                        cell = RoomCell(uid, self, (x, y), state="Dirty")
                    else:
                        cell = RoomCell(uid, self, (x, y), state="Clean")

                self.grid.place_agent(cell, (x, y))
                uid += 1


    def step(self):
        """Advance the model by one step."""

        self.schedule.step()
        self.datacollector.collect(self)
        self.steps += 1

        # stop conditions
        if self.steps >= self.max_steps:
            self.running = False

        if self.count_state("Dirty") == 0:
            self.running = False


    def count_state(self, state):
        """Count room cells in a given condition."""
        count = 0
        for cell in self.grid.agents:
            if isinstance(cell, RoomCell) and cell.state == state:
                count += 1
        return count

    def percent_clean(self):
        total = self.width * self.height
        dirty = self.count_state("Dirty")
        return (total - dirty) / total
