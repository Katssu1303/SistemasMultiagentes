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
        #self.neighbors es la lista de todas las celdas vecinas (las 8 alrededor)
        #Si esta celda está viva, imprime las posiciones de todos sus vecinos (vivos o muertos)
        # if self.is_alive:
        #     for neighbor in self.neighbors:
        #         print(neighbor.pos)

        #Encontrar los 3 vecinos de arriba
        upper_neighbors = [neighbor for neighbor in self.neighbors if neighbor.y > self.y]
        #Encontrar cuantos vecinos de arriba están vivos -> checa si el vecino esta vivo (bool) y 
        #cuenta los True para ver cuantos están vivos
        alive_above = sum(neighbor.is_alive for neighbor in upper_neighbors)
        #Encontrar los vecinos muertos
        dead_above = len(upper_neighbors) - alive_above

        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        # iterar - como si se definiera una función de una suma completa, como si juntaras un if
        #live_neighbors = sum(neighbor.is_alive for neighbor in self.neighbors)


        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

        if self.is_alive:
            if live_neighbors < 2 or live_neighbors > 3:
                self._next_state = self.DEAD
        else:
            if live_neighbors == 3:
                self._next_state = self.ALIVE

    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state
