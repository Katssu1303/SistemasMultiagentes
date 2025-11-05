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

        #Encontrar los 3 vecinos de arriba de la celula - lista (objetos)
        #upper_neighbors = [neighbor for neighbor in self.neighbors if neighbor.y > self.y + 1 ]
        upper_neighbors = [ neighbor for neighbor in self.neighbors if neighbor.y == self.y + 1 and neighbor.x in [self.x - 1, self.x, self.x + 1]]
        #print(upper_neighbors)

        #Encontrar cuantos vecinos de arriba están vivos -> checa si el vecino esta vivo (bool) y 
        #cuenta los True para ver cuantos están vivos
        #alive_above = sum(neighbor.is_alive for neighbor in upper_neighbors)
        #Encontrar los vecinos muertos
        #dead_above = len(upper_neighbors) - alive_above

        #Tendría que separar en que posición esta cual true y false para tener el orden y cumplir con las condiciones
        states = [1 if neighbor.is_alive else 0 for neighbor in upper_neighbors]
        print(states)
        alive_above = sum(states)
        dead_above = len(states) - alive_above
        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

        #si los 3 de arriba estan vivos, yo muero
        if alive_above == 3:
            self._next_state = self.DEAD
        #si los 3 de arriba estan muertos, yo vivo
        elif dead_above == 3:
            self._next_state = self.ALIVE
        elif states == [1,1,0]:
            self._next_state = self.ALIVE
        elif states == [1,0,1]:
            self._next_state = self.DEAD
        elif states == [1,0,0]:
            self._next_state = self.ALIVE
        elif states == [0,1,1]:
            self._next_state = self.ALIVE
        elif states == [0,1,0]:
            self._next_state = self.DEAD
        elif states == [0,0,1]:
            self._next_state = self.ALIVE


    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state
