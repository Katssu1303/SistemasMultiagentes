from mesa.discrete_space import CellAgent, FixedAgent

class RoomCell(CellAgent):
    """
    Cell en el cuarto.
    Estados:
        - "Dirty"
        - "Clean"
        - "Charger"
        - "Obstacle"
    """

    def __init__(self, unique_id, model, pos, state="Dirty"):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = state

    def step(self):
        pass


class RoombaAgent(CellAgent):
    """
    Agente Roomba.
    States:
        - "cleaning"
        - "returning"
        - "charging"
        - "idle"
        - "communicating"
    """

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.battery = 100
        self.state = "cleaning"
        self.moves = 0  # Count of movements

    def step(self):
        """Main decision logic based on current state."""
        # Battery behavior
        if self.state == "charging":
            self.charge_battery()
            return

        # If battery is low, start returning
        # Calcular distancia en steps para regrresar a mi estacion
        # Si estoy a 10 steps necesito x batería
        if self.battery <= 10 and self.state != "returning":
            self.state = "returning"

        if self.state == "returning":
            self.return_to_charger()
            return

        if self.state == "cleaning":
            self.clean_or_move()


    def charge_battery(self):
        """Increase battery while at charger."""
        cell = self.model.grid.get_cell_list_contents([self.pos])[0]
        if cell.state == "Charger":
            # cargar lo minimo para recoger las basuras que viste 
            self.battery = min(100, self.battery + 5)
            if self.battery == 100:
                self.state = "cleaning"
        else:
            # If Roomba somehow is not on charger while charging
            self.state = "returning"


    def return_to_charger(self):
        """Move toward (1,1) to recharge."""

        # tanto moverse como limpiar quita batería
        target = (1, 1)

        x, y = self.pos
        tx, ty = target

        # Simple greedy movement
        next_pos = (
            x - 1 if x > tx else x + 1 if x < tx else x,
            y - 1 if y > ty else y + 1 if y < ty else y
        )

        # If obstacle or invalid position, stay still
        if self.model.grid.is_cell_empty(next_pos):
            self.model.grid.move_agent(self, next_pos)
            self.pos = next_pos
            self.moves += 1
            self.battery -= 1

        # If reached charger
        if self.pos == target:
            self.state = "charging"


    def clean_or_move(self):
        """Clean if dirty, otherwise move randomly."""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        cell = cell_contents[0]  # RoomCell

        # Separar funcion clean y regresando

        # Clean
        if cell.state == "Dirty":
            cell.state = "Clean"
            self.battery -= 1
            return

        # Otherwise move randomly
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
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass

    # definir random la ubicación de los obstaculos y que sean fijos

    # usar dfs paera ir descartando y encontrar el optimo