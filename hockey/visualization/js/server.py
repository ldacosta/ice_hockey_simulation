from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from mesa.visualization.TextVisualization import (
    TextData, TextGrid, TextVisualization
)

# from examples.ice_hockey.model import HockeyHalfRink, Forward, Defense, Puck
from examples.ice_hockey.half_rink import HockeyHalfRink
from examples.ice_hockey.player import Player, Forward, Defense
from examples.ice_hockey.puck import Puck
from examples.ice_hockey.SimpleContinuousModule import SimpleCanvas


# class IceHockeyTextVisualization(TextVisualization):
#     '''
#     ASCII visualization for schelling model
#     '''
#
#     def __init__(self, model):
#         '''
#         Create new Schelling ASCII visualization.
#         '''
#         super().__init__(model)
#         self.model = model
#
#         grid_viz = TextGrid(self.model.grid, self.ascii_agent)
#         happy_viz = TextData(self.model, 'happy')
#         self.elements = [grid_viz, happy_viz]
#
#     @staticmethod
#     def ascii_agent(a):
#         '''
#         Minority agents are X, Majority are O.
#         '''
#         if a.type == 0:
#             return 'O'
#         if a.type == 1:
#             return 'X'


class HappyElement(TextElement):
    '''
    Display a text count of how many happy agents there are.
    '''
    def __init__(self):
        super().__init__()
        pass

    def render(self, model):
        return "Happy agents: " + str(model.happy)


def hockey_rink_draw(agent):
    '''
    Portrayal Method for canvas
    '''
    if agent is None:
        return
    # Players
    portrayal = {
        "Shape": "circle",
        "r": 1,
        "Filled": "true",
        "Layer": 0
    }
    if isinstance(agent, Player):
        portrayal = {
            "Shape": "circle",
            "r": agent.reach,
            "Filled": "true",
            "Layer": 0
        }
        # portrayal = {
        #     "Shape": "arrowHead",
        #     "scale": 2,
        #     "Filled": "true",
        #     "Layer": 0,
        #     "Color": "Red",
        #     "heading_x": 1,
        #     "heading_y": 0
        # }
        heading_x, heading_y = agent.vector_looking_at().tip
        portrayal["heading_x"] = heading_x
        portrayal["heading_y"] = heading_y
        # Colors
        if isinstance(agent, Forward):
            portrayal["Color"] = "Red"
            portrayal["text"] = "F"
        elif isinstance(agent, Defense):
            portrayal["Color"] = "Blue"
            portrayal["text"] = "D"
        portrayal["text_color"] = "white"
    elif isinstance(agent, Puck):
        portrayal = {
            "Shape": "circle",
            "r": 1,
            "Filled": "true",
            "Layer": 0
        }
        portrayal["Color"] = "Black"
    return portrayal

#

model_params = {
    "how_many_defense": 1,
    "how_many_offense": 0
    # ,
    # "density": UserSettableParameter("slider", "Agent density", 0.8, 0.1, 1.0, 0.1),
    # "minority_pc": UserSettableParameter("slider", "Fraction minority", 0.2, 0.00, 1.0, 0.05),
    # "homophily": UserSettableParameter("slider", "Homophily", 3, 0, 8, 1)
}

# happy_element = HappyElement()
# happy_chart = ChartModule([{"Label": "happy", "Color": "Black"}])
canvas_element = SimpleCanvas(hockey_rink_draw, canvas_height=500, canvas_width=500)
# canvas_element = CanvasGrid(
#     portrayal_method=hockey_rink_draw,
#     grid_height=HockeyHalfRink.HEIGHT_ICE,
#     grid_width=HockeyHalfRink.WIDTH_HALF_ICE,
#     canvas_height=500,
#     canvas_width=500)

server = ModularServer(HockeyHalfRink,
                       [canvas_element], # happy_element, happy_chart],
                       "Ice Rink", model_params)
server.launch()
