from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.user_param import Slider

from simulacion1.model import RoombaModel
from  simulacion1.agent import RoomCell, RoombaAgent


COLORS = {
    "Dirty": "#AA7700",     # café
    "Clean": "#FFFFFF",     # blanco
    "Obstacle": "#000000",  # negro
    "Charger": "#00FF00",   # verde
    "Roomba": "#0000FF",    # azul
}


def roomba_portrayal(agent):
    if agent is None:
        return

    # Room cells
    if isinstance(agent, RoomCell):
        return AgentPortrayalStyle(
            color=COLORS[agent.state],
            marker="+",   # marcador + para celdas
            size=8,
        )

    # Roomba agent
    if isinstance(agent, RoombaAgent):
        return AgentPortrayalStyle(
            color=COLORS["Roomba"],
            marker="+",
            size=12,
        )


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))


space_component = make_space_component(
    roomba_portrayal,
    draw_grid=False,
    post_process=post_process_space,
)

lineplot_component = make_plot_component(
    {
        "CleanPct": "#00AA00",
        "Battery": "#0000FF",
        "Moves": "#AA0000",
    },
    post_process=post_process_lines,
)


model_params = {
    "width": Slider("Room Width", 20, 5, 50, 1),
    "height": Slider("Room Height", 20, 5, 50, 1),
    "dirt_prob": Slider("Dirt Probability", 0.3, 0.0, 1.0, 0.05),
    "obstacle_prob": Slider("Obstacle Probability", 0.1, 0.0, 0.5, 0.05),
    "max_steps": Slider("Max Steps", 500, 50, 2000, 50),
}


page = SolaraViz(
    RoombaModel,
    components=[space_component, lineplot_component],
    model_params=model_params,
    name="Roomba Simulation",
)
