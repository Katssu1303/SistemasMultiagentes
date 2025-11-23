from simulacion1.model import RoombaModel
from simulacion1.agent import FloorCell, RoombaAgent

from mesa.visualization import (
    SolaraViz,
    make_plot_component,
    make_space_component,
    Slider,
)

COLORS = {
    "Dirty": "#8B4513",
    "Clean": "#FFFFFF",
    "Obstacle": "#000000",
    "Charger": "#00FF00",
}

def portrayal(agent):
    if isinstance(agent, FloorCell):
        return {
            "color": COLORS.get(agent.state, "#CCCCCC"),
            "marker": "s",
            "size": 50,
            "zorder": 0,
        }
    elif isinstance(agent, RoombaAgent):
        if agent.state == "dead":
            color = "#FF0000"
        elif agent.state == "charging":
            color = "#FFFF00"
        elif agent.state == "returning":
            color = "#FFA500"
        elif agent.state == "cleaning":
            color = "#0000FF"
        else:
            color = "#808080"

        return {
            "color": color,
            "marker": "o",
            "size": 80,
            "zorder": 1,
            "alpha": 0.8,
        }
    return {}

def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

space_component = make_space_component(
    portrayal,
    draw_grid=False,
    post_process=post_process_space,
)

lineplot_component = make_plot_component(
    ["CleanPct", "AvgBattery"],
    post_process=post_process_lines,
)

model_params = {
    "width": Slider("Ancho", 20, 10, 50, 5),
    "height": Slider("Alto", 20, 10, 50, 5),
    "dirt_prob": Slider("Probabilidad de suciedad", 0.3, 0.0, 1.0, 0.05),
    "obstacle_prob": Slider("Probabilidad de obstáculos", 0.1, 0.0, 0.5, 0.05),
    "num_agents": Slider("Número de Roombas", 1, 1, 10, 1),
}

# 👇 CREA UNA INSTANCIA del modelo
initial_model = RoombaModel()

# 👇 Pasa la INSTANCIA, no la CLASE
page = SolaraViz(
    initial_model,
    components=[space_component, lineplot_component],
    model_params=model_params,
    name="Roomba Cleaning Simulation",
)