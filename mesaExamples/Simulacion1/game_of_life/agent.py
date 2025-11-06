# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    #constructor
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate 
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """

        #La primera línea debe mantenerse igual
        if self.y == 49:
            self._next_state = self.state
            return

        #self.neighbors es la lista de todas las celdas vecinas (las 8 alrededor)
        #Si esta celda está viva, imprime las posiciones de todos sus vecinos (vivos o muertos)
        # if self.is_alive:
        #     for neighbor in self.neighbors:
        #         print("En celda:", self.pos, "vecino x:", neighbor.x, "vecino y:", neighbor.y)

        neighborRight = False
        neighborCenter = False
        neighborLeft = False

        #Encontrar los 3 vecinos de arriba de la celda - lista (objetos)
        for neighbor in self.neighbors:
            #Obtener solo los de arriba
            if neighbor.y == self.y + 1:
                # Buscar el de la izquierda (x - 1)
                if (neighbor.x == self.x - 1):
                    neighborLeft = neighbor.is_alive
                # Buscar el del centro (x igual)
                elif (neighbor.x == self.x):
                    neighborCenter = neighbor.is_alive
                # Buscar el de la derecha (x + 1)
                elif (neighbor.x == self.x + 1):
                    neighborRight = neighbor.is_alive

        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

        #si los 3 de arriba estan vivos, yo muero
        if neighborRight and neighborCenter and neighborLeft:
            self._next_state = self.DEAD
        elif neighborRight and neighborCenter and not neighborLeft:
            self._next_state = self.ALIVE
        elif neighborRight and not neighborCenter and neighborLeft:
            self._next_state = self.DEAD
        elif neighborRight and not neighborCenter and not neighborLeft:
            self._next_state = self.ALIVE
        elif not neighborRight and neighborCenter and neighborLeft:
            self._next_state = self.ALIVE
        elif not neighborRight and neighborCenter and not neighborLeft:
            self._next_state = self.DEAD
        elif not neighborRight and not neighborCenter and neighborLeft:
            self._next_state = self.ALIVE
        elif not neighborRight and not neighborCenter and not neighborLeft:
            self._next_state = self.DEAD


    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state
