# simulacion1/model.py
import math
from typing import Optional

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid

from .agents import FloorCell, RoombaAgent


class RoombaModel(Model):
    """
    Cleaning environment for one or multiple Roombas, using Mesa >= 3.0.

    Parameters
    ----------
    width, height : int
        Room size (M x N).
    dirt_prob : float
        Probability that a non-obstacle cell starts as Dirty.
    obstacle_prob : float
        Probability that a cell is an Obstacle.
    num_agents : int
        Number of Roomba agents.
    max_steps : int
        Maximum number of steps to run.
    fixed_start : bool
        - True  => single agent starting at (1, 1) with a charger there.
        - False => agents start at random positions; each start cell is a charger.
    seed : Optional[int]
        Random seed.
    """

    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        dirt_prob: float = 0.3,
        obstacle_prob: float = 0.1,
        num_agents: int = 1,
        max_steps: int = 1_000,
        fixed_start: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.dirt_prob = dirt_prob
        self.obstacle_prob = obstacle_prob
        self.num_agents = num_agents
        self.max_steps = max_steps
        self.fixed_start = fixed_start

        # Orthogonal grid (Moore neighborhood), no torus
        self.grid = OrthogonalMooreGrid(
            [self.height, self.width],
            torus=False,
            capacity=math.inf,
            random=self.random,
        )

        # Create floor cells (Dirty / Clean / Obstacle)
        self._create_floor_cells()

        # Create roombas + chargers
        self._create_roombas_and_chargers()

        # Stats
        self.step_count = 0
        self.running = True

        # DataCollector
        self.datacollector = DataCollector(
            model_reporters={
                "CleanPct": lambda m: m.percent_clean(),
                "DirtyCells": lambda m: m.count_cells_state("Dirty"),
                "CleanCells": lambda m: m.count_cells_state("Clean"),
                "ObstacleCells": lambda m: m.count_cells_state("Obstacle"),
                "AvgBattery": lambda m: m.average_battery(),
                "TotalMoves": lambda m: m.total_moves(),
            }
        )
        self.datacollector.collect(self)

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    def _create_floor_cells(self) -> None:
        """
        For every cell in the grid, create a FloorCell with the appropriate
        initial state (Dirty / Clean / Obstacle).
        """
        for cell in self.grid.all_cells:
            # Decide if it's an obstacle
            if self.random.random() < self.obstacle_prob:
                state = "Obstacle"
            else:
                # If not an obstacle, decide if it's dirty
                state = "Dirty" if self.random.random() < self.dirt_prob else "Clean"

            FloorCell(self, cell=cell, state=state)

    def _create_roombas_and_chargers(self) -> None:
        """
        Create Roomba agents and assign charger cells according to the simulation type.
        """
        if self.num_agents < 1:
            return

        # --- Determine starting cells ---
        if self.fixed_start and self.num_agents == 1:
            # Single agent starting at (1,1)
            # NOTE: coordinates are 0-based in Mesa 3, so (1,1) means "segunda fila, segunda columna"
            start_coord = (1, 1)
            # Clamp just in case
            i = max(0, min(self.height - 1, start_coord[0]))
            j = max(0, min(self.width - 1, start_coord[1]))
            start_cell = self.grid[i, j]
            start_cells = [start_cell]
        else:
            # Multiple agents: random starting cells
            start_cells = self.random.choices(
                self.grid.all_cells.cells, k=self.num_agents
            )

        # --- Create agents ---
        RoombaAgent.create_agents(
            self,
            self.num_agents,
            cell=start_cells,
            battery_max=100,
        )

        # --- Mark charger cells (one per starting cell) ---
        roombas = self.agents_by_type[RoombaAgent]
        for agent in roombas:
            cell = agent.cell
            agent.home_cell = cell  # save home

            # Find the floor cell in this grid cell and mark as charger
            for obj in cell.agents:
                if isinstance(obj, FloorCell):
                    obj.state = "Charger"
                    break

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    def count_cells_state(self, state: str) -> int:
        floor_cells = self.agents_by_type.get(FloorCell, [])
        return len(floor_cells.select(lambda c: c.state == state))

    def percent_clean(self) -> float:
        floor_cells = self.agents_by_type.get(FloorCell, [])
        total = len(floor_cells)
        if total == 0:
            return 1.0
        dirty = len(floor_cells.select(lambda c: c.state == "Dirty"))
        return (total - dirty) / total

    def average_battery(self) -> float:
        roombas = self.agents_by_type.get(RoombaAgent, [])
        n = len(roombas)
        if n == 0:
            return 0.0
        total_batt = sum(a.battery for a in roombas)
        return total_batt / n

    def total_moves(self) -> int:
        roombas = self.agents_by_type.get(RoombaAgent, [])
        return sum(a.moves for a in roombas)

    # ------------------------------------------------------------------
    # Simulation step
    # ------------------------------------------------------------------
    def step(self) -> None:
        """
        One step of the model: move and act all Roombas.
        """
        # Only Roomba agents perform actions; floor cells are static
        roombas = self.agents_by_type.get(RoombaAgent, [])
        roombas.shuffle_do("step")

        self.step_count += 1
        self.datacollector.collect(self)

        # Stop conditions:
        #  - all cells clean, OR
        #  - reached max_steps, OR
        #  - all agents dead (battery 0)
        if self.count_cells_state("Dirty") == 0:
            self.running = False
            return

        if self.step_count >= self.max_steps:
            self.running = False
            return

        all_dead = all(a.state == "dead" for a in roombas)
        if all_dead:
            self.running = False