from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid
from .agent import Cell


class ConwaysGameOfLife(Model):
    """Represents the 2-dimensional array of cells in Conway's Game of Life."""

    def __init__(self, width=50, height=50, initial_fraction_alive=0.2, seed=None):
        """Create a new playing area of (width, height) cells."""
        super().__init__(seed=seed)

        """Grid where cells are connected to their 8 neighbors.

        Example for two dimensions:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1),
        ]
        """
        self.grid = OrthogonalMooreGrid((width, height), capacity=1, torus=True)
        #capacity -> cuantos agentes pueden estar en una celda / torus como si se doblara en los bordes

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        # Recorre todas las celdas de la cuadrícula
        for cell in self.grid.all_cells:

            # Si la celda está en la fila superior (y == 49)
            # se inicializa con un estado aleatorio ALIVE o DEAD
            if cell.coordinate[1] == 49:
                Cell(
                    self, #referencia al mismo objeto que se esta creando
                    cell,
                    init_state=(
                        # La celda estará viva si el número aleatorio es menor
                        # que la fracción inicial de celdas vivas definida
                        Cell.ALIVE
                        if self.random.random() < initial_fraction_alive
                        else Cell.DEAD
                    ),
                )
            else:
                Cell(
                    self,
                    cell,
                    init_state=(
                        Cell.DEAD
                    ),
                )


        #correr simulación
        self.running = True

    def step(self):
        """Perform the model step in two stages:

        - First, all cells assume their next state (whether they will be dead or alive)
        - Then, all cells change state to their next state.
        """
        #cada step a todos los agentes que tengo definidos hacer: ver que estado les toca para despues aplicarlo
        self.agents.do("determine_state") #coincidir los nombres con los métodos
        self.agents.do("assume_state")
