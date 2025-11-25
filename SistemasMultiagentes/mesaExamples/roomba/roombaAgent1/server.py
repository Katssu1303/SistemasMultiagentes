# app.py  (en la carpeta roombaAgent1/)
from __future__ import annotations

from mesa.visualization import (
    SolaraViz,
    make_space_component,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.user_param import Slider

from simulacion1.model import RoombaModel
from simulacion1.agents import FloorCell, RoombaAgent

# -------------------------------------------------------------------
# Portrayal
# -------------------------------------------------------------------
COLORS = {
    "Dirty": "#AA7700",      # brown
    "Clean": "#FFFFFF",      # white
    "Obstacle": "#000000",   # black
    "Charger": "#00FF00",    # green
}


def roomba_portrayal(agent):
    if agent is None:
        return None

    # Roomba agents: blue circles
    if isinstance(agent, RoombaAgent):
        return AgentPortrayalStyle(
            color="#F50DBB",
            marker="o",
            size=80,
        )

    # Floor cells: colored squares by state
    if isinstance(agent, FloorCell):
        color = COLORS.get(agent.state, "#CCCCCC")
        return AgentPortrayalStyle(
            color=color,
            marker="s",
            size=80,
        )

    # Default style (should not really happen here)
    return AgentPortrayalStyle()


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def post_process_plot(ax):
    ax.set_xlabel("Step")
    ax.set_ylabel("Value")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))


# Space component (matplotlib backend)
space_component = make_space_component(
    agent_portrayal=roomba_portrayal,
    post_process=post_process_space,
)

# Plot component: show cleanliness, remaining dirty cells, and avg battery
plot_component, _ = make_plot_component(
    [
        "CleanPct",
        "DirtyCells",
        "AvgBattery",
    ],
    post_process=post_process_plot,
)

# -------------------------------------------------------------------
# User-adjustable parameters (Mesa >= 3 style)
# -------------------------------------------------------------------
model_params = {
    "width":        Slider("Width", value=20, min=5, max=50, step=1, dtype=int),
    "height":       Slider("Height", value=20, min=5, max=50, step=1, dtype=int),
    "dirt_prob":    Slider("Dirt probability", value=0.3, min=0.0, max=1.0, step=0.05),
    "obstacle_prob": Slider("Obstacle probability", value=0.1, min=0.0, max=0.5, step=0.05),
    "num_agents":   Slider("Number of agents", value=1, min=1, max=10, step=1, dtype=int),
    "max_steps":    Slider("Max steps", value=1000, min=100, max=5000, step=100, dtype=int),

    # fixed_start no es slider: queda como parámetro fijo.
    # Cambia esto a False si quieres que en la UI se comporte como Simulación 2.
    "fixed_start": True,
}

# Modelo inicial
initial_model = RoombaModel(
    width=model_params["width"].value,
    height=model_params["height"].value,
    dirt_prob=model_params["dirt_prob"].value,
    obstacle_prob=model_params["obstacle_prob"].value,
    num_agents=model_params["num_agents"].value,
    max_steps=model_params["max_steps"].value,
    fixed_start=model_params["fixed_start"],
)

# Solara page
page = SolaraViz(
    initial_model,
    components=[space_component, plot_component],
    model_params=model_params,
    name="Roomba Simulation (Mesa 3.x)",
)