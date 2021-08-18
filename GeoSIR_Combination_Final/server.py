from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from model import InfectedModel, PersonAgent
from mesa_geo.visualization.MapModule import MapModule

class InfectedText(TextElement):
    def __init__(self):
        pass
    def render(self, model):
        return "Steps: " + str(model.steps)


model_params = {  
    "infection_risk": 0.2,
    "in_lockdown": UserSettableParameter(
        "choice", "Is there a full lockdown restrictions?",value = 'Yes', choices=['Yes','No']
    ),    
}


def infected_draw(agent):
    portrayal = dict()
    if isinstance(agent, PersonAgent):
        portrayal["radius"] = "2"
    if agent.atype in ["hotspot", "infected"]:
        portrayal["color"] = "Red"
    elif agent.atype in ["exposed"]:
        portrayal["color"] = "Yellow"
    # Color of the grid
    elif agent.atype in ["safe"]:
        if agent.Function in ["residential"]:
            portrayal["color"] = "Yellow"
        else:
            portrayal["color"] = "White"
    elif agent.atype in ["susceptible"]:
        portrayal["color"] = "Green"
    elif agent.atype in ["recovered"]:
        portrayal["color"] = "Blue"
    elif agent.atype in ["dead"]:
        portrayal["color"] = "Black"
    return portrayal


infected_text = InfectedText()
map_element = MapModule(infected_draw, InfectedModel.MAP_COORDS, 12, 600, 750)

infected_chart = ChartModule(
    [
        {"Label": "infected", "Color": "Red"},
        {"Label": "exposed", "Color": "Yellow"},
        {"Label": "susceptible", "Color": "Green"},
        {"Label": "recovered", "Color": "Blue"},
        {"Label": "dead", "Color": "Black"},
    ],
    data_collector_name='datacollector'
)

infected_agegroup_chart = ChartModule(
    [
        {"Label": "00to19", "Color": "Blue"},
        {"Label": "20to29", "Color": "Lime"},
        {"Label": "30to39", "Color": "Brown"},
        {"Label": "40to49", "Color": "Yellow"},
        {"Label": "50to59", "Color": "Cyan"},
        {"Label": "60to69", "Color": "Green"},
        {"Label": "70to79", "Color": "Magenta"},
        {"Label": "80toXX", "Color": "Black"},
        {"Label": "Allinfected", "Color": "Red"},
    ],
    data_collector_name='infectedgroupdatacollector'
)

death_agegroup_chart = ChartModule(
    [
        {"Label": "00to19", "Color": "Blue"},
        {"Label": "20to29", "Color": "Lime"},
        {"Label": "30to39", "Color": "Brown"},
        {"Label": "40to49", "Color": "Yellow"},
        {"Label": "50to59", "Color": "Cyan"},
        {"Label": "60to69", "Color": "Green"},
        {"Label": "70to79", "Color": "Magenta"},
        {"Label": "80toXX", "Color": "Black"},
        {"Label": "Alldeath", "Color": "Red"},
    ],
    data_collector_name='deathgroupdatacollector'
)

server = ModularServer(
    InfectedModel,
    [map_element, infected_text, infected_chart, infected_agegroup_chart,death_agegroup_chart],
    "Basic agent-based SIR model (Barking and Dagenham)",
    model_params,
)

server.launch()
