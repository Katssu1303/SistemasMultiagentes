from mesa.visualization import (
    SolaraViz,
    make_space_component,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.user_param import Slider

from simulacion1.model import RoombaModel
from simulacion1.agents import FloorCell, RoombaAgent


# Portrayal
COLORS = {
    "Dirty": "#AA7700",
    "Clean": "#FFFFFF",
    "Obstacle": "#000000",
    "Charger": "#00FF00",
}

def roomba_portrayal(agent):
    if agent is None:
        return None

    if isinstance(agent, RoombaAgent):
        return AgentPortrayalStyle(
            color="#FF00FF",
            marker="o",
            size=80,
        )

    if isinstance(agent, FloorCell):
        color = COLORS.get(agent.state, "#CCCCCC")
        return AgentPortrayalStyle(
            color=color,
            marker="s",
            size=80,
        )

    return AgentPortrayalStyle()


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def post_process_plot(ax):
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))


# Space component
space_component = make_space_component(
    agent_portrayal=roomba_portrayal,
    post_process=post_process_space,
)

# Plot component
lineplot_component, _ = make_plot_component(
    COLORS,
    post_process=post_process_plot,
)

# Parámetros del modelo
#model = RoombaModel()
model_params = {
    "width":        Slider("Width", value=20, min=5, max=50, step=1, dtype=int),
    "height":       Slider("Height", value=20, min=5, max=50, step=1, dtype=int),
    "dirt_prob":    Slider("Dirt probability", value=0.3, min=0.0, max=1.0, step=0.05),
    "obstacle_prob": Slider("Obstacle probability", value=0.1, min=0.0, max=0.5, step=0.05),
    "num_agents":   Slider("Number of agents", value=1, min=1, max=10, step=1, dtype=int),
}


# Solara page
page = SolaraViz(
    RoombaModel, 
    components=[space_component, lineplot_component],
    model_params=model_params,
    name="Roomba Simulation 1",
)