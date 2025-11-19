from simulacion1.model import RoombaModel

from mesa.visualization import (
    SolaraViz,
    make_plot_component,
    make_space_component,
)

from mesa.visualization.user_param import (
    Slider,
)

from mesa.visualization.components import AgentPortrayalStyle

from simulacion1.model import RoombaModel
from  simulacion1.agent import RoomCell, RoombaAgent


COLORS = {
    "Dirty": "#AA7700",     # café
    "Clean": "#FFFFFF",     # blanco
    "Obstacle": "#000000",  # negro
    "Charger": "#00FF00",   # verde
}


def roomba_portrayal(agent):
    if agent is None:
        return
    
    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
    )

    if isinstance(agent, RoombaAgent):
        portrayal.color = "#0000FF";
    elif isinstance(agent, RoomCell):
        portrayal.color=COLORS[agent.state],
        portrayal.marker="s",
        portrayal.size=50,
    
    return portrayal



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
    COLORS,
    post_process=post_process_lines,
)

model_params = {
    "width": 200,
    "height": 200,
    "dirt_prob": Slider("Dirt Probability", 0.3, 0.0, 1.0, 0.05),
    "obstacle_prob": Slider("Obstacle Probability", 0.1, 0.0, 0.5, 0.05),
    "max_steps": Slider("Max Steps", 500, 50, 2000, 50),
}

model = RoombaModel()

page = SolaraViz(
    model,
    components=[space_component, lineplot_component],
    model_params=model_params,
    name="Roomba Simulation",
)
