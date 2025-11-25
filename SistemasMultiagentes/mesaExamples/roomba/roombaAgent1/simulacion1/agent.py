# simulacion1/agents.py
import math
from typing import List

from mesa.discrete_space import CellAgent, FixedAgent


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
        # Floor does nothing; it's just environment.
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
    """

    def __init__(
        self,
        model,
        cell=None,
        battery_max: int = 100,
    ) -> None:
        super().__init__(model)
        self.cell = cell
        self.battery_max = battery_max
        self.battery = battery_max
        self.state = "cleaning"
        self.moves = 0
        self.cleaned_cells = 0

        # Home/charger cell: initial position
        self.home_cell = cell

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _consume_battery(self, amount: int = 1) -> None:
        if self.battery <= 0:
            self.battery = 0
            self.state = "dead"
        else:
            self.battery = max(0, self.battery - amount)
            if self.battery == 0:
                self.state = "dead"

    def _get_floor_here(self) -> FloorCell | None:
        """Return the FloorCell in the current cell."""
        for obj in self.cell.agents:
            if isinstance(obj, FloorCell):
                return obj
        return None

    def _is_obstacle_cell(self, candidate_cell) -> bool:
        for obj in candidate_cell.agents:
            if isinstance(obj, FloorCell) and obj.state == "Obstacle":
                return True
        return False

    # ---------------------------------------------------------
    # High-level decision
    # ---------------------------------------------------------
    def step(self) -> None:
        if self.state == "dead":
            return

        # If currently charging, handle charging logic and exit.
        if self.state == "charging":
            self._charge()
            return

        # Battery low → start returning to charger
        if self.battery <= 10 and self.state != "returning":
            self.state = "returning"

        # If returning, move towards charger.
        if self.state == "returning":
            self._return_to_charger()
            return

        # Normal cleaning behavior
        if self.state == "cleaning":
            self._clean_or_move()

    # ---------------------------------------------------------
    # Behaviors
    # ---------------------------------------------------------
    def _charge(self) -> None:
        """
        While on a charger, increase battery.
        """
        floor = self._get_floor_here()
        if floor is None:
            # Should not happen; be defensive
            self.state = "returning"
            return

        if floor.state == "Charger":
            self.battery = min(self.battery_max, self.battery + 5)

            # When battery is reasonably high, go back to cleaning
            if self.battery >= 50:
                # Small probability of staying charging extra time
                if self.random.random() < 0.4:
                    # keep charging
                    return
                self.state = "cleaning"
        else:
            # Not really on a charger → try to go back
            self.state = "returning"

    def _return_to_charger(self) -> None:
        """
        Greedy movement towards home_cell, avoiding obstacles.

        Not a full BFS, but enough for the assignment:
        the agent actively tries to regresar a cargar.
        """
        # If already on a charger, switch to charging.
        floor = self._get_floor_here()
        if floor is not None and floor.state == "Charger":
            self.state = "charging"
            return

        hx, hy = self.home_cell.coordinate
        # Neighborhood is a Neighborhood object (Mesa 3 discrete_space)
        neighborhood = self.cell.neighborhood

        # Filter cells that are not obstacles
        candidate_cells: List = [
            c for c in neighborhood if not self._is_obstacle_cell(c)
        ]
        if not candidate_cells:
            # No way forward; just consume battery slowly.
            self._consume_battery()
            return

        # Choose neighbor that minimizes Manhattan distance to home
        best_cell = None
        best_dist = math.inf
        for c in candidate_cells:
            x, y = c.coordinate
            dist = abs(x - hx) + abs(y - hy)
            if dist < best_dist:
                best_dist = dist
                best_cell = c

        if best_cell is None:
            self._consume_battery()
            return

        # Move to best_cell
        self.cell = best_cell
        self.moves += 1
        self._consume_battery()

        # If we arrived to charger
        floor = self._get_floor_here()
        if floor is not None and floor.state == "Charger":
            self.state = "charging"

    def _clean_or_move(self) -> None:
        floor = self._get_floor_here()
        if floor is None:
            # Very weird, but don't crash
            self._move_random()
            return

        if floor.state == "Dirty":
            self._clean()
        else:
            self._move_random()

    def _clean(self) -> None:
        floor = self._get_floor_here()
        if floor is not None and floor.state == "Dirty":
            floor.state = "Clean"
            self.cleaned_cells += 1
            self._consume_battery()

    def _move_random(self) -> None:
        """
        Move randomly to a neighbor cell that is not an obstacle.
        """
        # Neighborhood is a Neighborhood object; we can filter it
        safe_cells = self.cell.neighborhood.select(
            lambda c: not self._is_obstacle_cell(c)
        )

        if len(safe_cells) == 0:
            # No safe moves
            self._consume_battery()
            return

        target = safe_cells.select_random_cell()
        if target is None:
            self._consume_battery()
            return

        self.cell = target
        self.moves += 1
        self._consume_battery()