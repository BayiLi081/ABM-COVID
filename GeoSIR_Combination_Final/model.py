#%%
from mesa.datacollection import DataCollector
from mesa import Model
from enum import Enum
from mesa.time import BaseScheduler
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
from shapely.geometry import shape, GeometryCollection, Point
import random
import pandas as pd

class PersonAgent(GeoAgent):
    """Person Agent."""
    def __init__(
        self,
        unique_id,
        residence,
        model,
        shape,
        agent_type="susceptible",
        ageg="00to19",
        mort=0,
        StayatHome = False,
        exposedate = 0,
        recovery_rate = 0.1,
    ):
        super().__init__(unique_id, model, shape)
        # Agent parameters
        self.atype = agent_type
        self.age_group = ageg
        self.recovery_rate = recovery_rate
        self.death_risk = mort
        self.infect_risk = self.model.infection_risk
        self.inlock = StayatHome
        self.exposedate = exposedate
        self.residence = residence
        #for agent in model.schedule.agents:
        chance = self.random.random()
        if chance < 0.027:
            self.age_group = "80toXX"
            self.death_risk = 0.02376
            self.infect_risk = self.infect_risk*0.74
        # Random choose if dead
        elif chance < 0.065 and chance > 0.027:
            self.age_group = "70to79"
            self.death_risk = 0.00554
            self.infect_risk = self.infect_risk*0.74
        elif chance < 0.13 and chance > 0.065:
            self.age_group = "60to69"
            self.death_risk = 0.00193
            self.infect_risk = self.infect_risk*0.88
        elif chance < 0.238 and chance > 0.13:
            self.age_group = "50to59"
            self.death_risk = 0.00066
            self.infect_risk = self.infect_risk*0.82
        elif chance < 0.374 and chance > 0.238:
            self.age_group = "20to29"
            self.death_risk = 0.00002
            self.infect_risk = self.infect_risk*0.79
        elif chance < 0.513 and chance > 0.374:
            self.age_group = "40to49"
            self.death_risk = 0.00007
            self.infect_risk = self.infect_risk*0.8
        elif chance < 0.678 and chance > 0.513:
            self.age_group = "30to39"
            self.death_risk = 0.00007
            self.infect_risk = self.infect_risk*0.86
        else:
            self.age_group = "00to19"
            self.death_risk = 0
            self.infect_risk = self.infect_risk*0.4

        chance = self.random.random()
        # Random choose if infected
        #if self.random.random() < 0.000187:
        if chance < 0.0003:
            self.atype = "infected"
            self.model.counts["infected"] += 1
        # Random choose if dead
        elif chance < 0.000814 and chance > 0.0003 and self.age_group != "00to19":
            self.atype = "dead"
            self.model.counts["dead"] += 1
        elif chance < 0.004 and chance > 0.000814:
            self.atype = "recovered"
            self.model.counts["recovered"] += 1
        else:
            self.atype = "susceptible"
            self.model.counts["susceptible"] -= 1

    def step(self):
        """Advance one step."""
        tree = self.model.tree
        tree_loc = self.model.tree_loc
        Prob_infected = 0
        # If not dead, move
        if self.atype != "dead":
            self.inlock = False
            # in lockdown
            if self.model.in_lockdown == True:
                des_choice = random.choices(['rar','N_Grocery','N_Pharmacy','N_Green','N_Transport','stay'],[0.052, 0.158, 0.04, 0.312, 0.106, 0.332], k=1)
                if des_choice[0] == 'rar':
                    no_rar = random.randint(0,273)
                    rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'rar']['x'])[no_rar]
                    rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'rar']['y'])[no_rar]
                    self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                    Prob_infected=self.infect_risk*0.74
                elif des_choice[0] == 'N_Grocery':
                    self.shape = self.move_point(tree, tree_loc, 'N_Grocery')
                    Prob_infected=self.infect_risk*0.3
                elif des_choice[0] == 'N_Pharmacy':
                    self.shape = self.move_point(tree, tree_loc,'N_Pharmacy')
                    Prob_infected=self.infect_risk*0.3
                elif des_choice[0] == 'N_Green':
                    Prob_infected=self.infect_risk*0.44
                    if self.random.random() < 0.5:
                        self.shape = self.move_point(tree, tree_loc,'N_Green')
                    else:
                        no_green = random.randint(0,533)
                        rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'green']['x'])[no_green]
                        rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'green']['y'])[no_green]
                        self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                elif des_choice[0] == 'N_Transport':
                    Prob_infected=self.infect_risk*0.7
                    if self.random.random() < 0.5:
                        self.shape = self.move_point(tree, tree_loc,'N_Transport')
                    else:
                        no_trans = random.randint(0,14)
                        rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'transport']['x'])[no_trans]
                        rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'transport']['y'])[no_trans]
                        self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                else:
                    self.inlock=True
                    self.shape = self.SaHome(tree_loc)
            des_choice = []
            if self.model.in_lockdown == False:
                if (self.model.steps % 7 == 0 or self.model.steps % 7 == 6 or self.age_group == "00to19" or self.age_group == "70to79" or self.age_group == "80toXX"):                
                    des_choice = random.choices(['rar','N_Grocery','N_Pharmacy','N_Green','N_Transport','stay'],[0.131, 0.163, 0.082, 0.291, 0.137, 0.195], k=1)
                    if des_choice[0] == 'rar':
                        no_rar = random.randint(0,273)
                        rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'rar']['x'])[no_rar]
                        rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'rar']['y'])[no_rar]
                        self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                        Prob_infected=self.infect_risk*0.74
                    elif des_choice[0] == 'N_Green':
                        Prob_infected=self.infect_risk*0.44
                        if self.random.random() < 0.5:
                            self.shape = self.move_point(tree, tree_loc,'N_Green')
                        else:
                            no_green = random.randint(0,533)
                            rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'green']['x'])[no_green]
                            rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'green']['y'])[no_green]
                            self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                    elif des_choice[0] == 'N_Grocery':
                        self.shape = self.move_point(tree, tree_loc, 'N_Grocery')
                        Prob_infected=self.infect_risk*0.3
                    elif des_choice[0] == 'N_Pharmacy':
                        self.shape = self.move_point(tree, tree_loc,'N_Pharmacy')
                        Prob_infected=self.infect_risk*0.3
                    elif des_choice[0] == 'N_Transport':
                        Prob_infected=self.infect_risk*0.7
                        if self.random.random() < 0.5:
                            self.shape = self.move_point(tree, tree_loc,'N_Transport')
                        else:
                            no_trans = random.randint(0,14)
                            rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'transport']['x'])[no_trans]
                            rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'transport']['y'])[no_trans]
                            self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                    else:
                        self.inlock=True
                        self.shape = self.SaHome(tree_loc)
                # weekday activities:
                else:
                    des_choice = random.choices(['N_Grocery', 'N_Green', 'N_Transport','work'],[0.086, 0.331, 0.308, 0.275], k=1)
                    if des_choice[0] == 'N_Grocery':
                        self.shape = self.move_point(tree, tree_loc, 'N_Grocery')
                        Prob_infected=self.infect_risk*0.3
                    elif des_choice[0] == 'N_Green':
                        Prob_infected=self.infect_risk*0.44
                        if self.random.random() < 0.5:
                            self.shape = self.move_point(tree, tree_loc,'N_Green')
                        else:
                            no_green = random.randint(0,533)
                            rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'green']['x'])[no_green]
                            rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'green']['y'])[no_green]
                            self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                    elif des_choice[0] == 'N_Transport':
                        Prob_infected=self.infect_risk*0.7
                        if self.random.random() < 0.5:
                            self.shape = self.move_point(tree, tree_loc,'N_Transport')
                        else:
                            no_trans = random.randint(0,14)
                            rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'transport']['x'])[no_trans]
                            rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'transport']['y'])[no_trans]
                            self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
                    elif des_choice[0] == 'work':
                        Prob_infected=self.infect_risk*0.6
                        no_work = random.randint(0,218)
                        rar_x = list(tree_loc.loc[tree_loc['FUNCTION'] == 'work']['x'])[no_work]
                        rar_y = list(tree_loc.loc[tree_loc['FUNCTION'] == 'work']['y'])[no_work]
                        self.shape = Point(rar_x + random.randint(-50, 50), rar_y + random.randint(-50, 50))
        
        # If susceptible, check if exposed
        # 50m is the proximity distance between agents to be exposed to each other
        if (self.atype == "susceptible" and self.inlock == False):
            neighbors = self.model.grid.get_neighbors_within_distance(
                self, 50
            )
            for neighbor in neighbors:
                if neighbor.atype == "infected":
                    self.atype = "exposed"
                    break

        # If infected, check if it recovers or if it dies
        elif self.atype == "infected":
            self.exposedate += 1
            if self.exposedate > 3:
                if self.random.random() < self.recovery_rate:
                    self.atype = "recovered"
                elif self.random.random() < self.death_risk:
                    self.atype = "dead"

        elif self.atype == "exposed":
            self.exposedate += 1
            if self.exposedate == 3:
                if self.random.random() < Prob_infected:
                    self.atype = "infected"
                else:
                    self.atype = "susceptible"
                    self.exposedate = 0
                

        self.model.counts[self.atype] += 1  # Count agent type


    
    def move_point(self, tree, tree_loc, des_choice):      
        new_position_x = tree_loc.loc[tree_loc['GRID_ID'] == tree.loc[tree['GRID_ID'] == self.residence].iloc[0][des_choice]].iloc[0]['x'] + random.randint(-100, 100)
        new_position_y = tree_loc.loc[tree_loc['GRID_ID'] == tree.loc[tree['GRID_ID'] == self.residence].iloc[0][des_choice]].iloc[0]['y'] + random.randint(-100, 100)
        return Point(new_position_x, new_position_y)
    
    # set agent to stay at home
    def SaHome(self, tree_loc):      
        new_position_x = tree_loc.loc[tree_loc['GRID_ID'] == self.residence].iloc[0]['x']
        new_position_y = tree_loc.loc[tree_loc['GRID_ID'] == self.residence].iloc[0]['y']
        return Point(new_position_x, new_position_y)
    
    

    def __repr__(self):
        return "Person " + str(self.unique_id)


class NeighbourhoodAgent(GeoAgent):
    """Neighbourhood agent. Changes color according to number of infected inside it."""

    def __init__(self, unique_id, model, shape, agent_type="safe", hotspot_threshold=1):
        super().__init__(unique_id, model, shape)
        self.atype = agent_type
        self.hotspot_threshold = (
            hotspot_threshold
        )  # When a neighborhood is considered a hot-spot
        self.color_hotspot()

    def step(self):
        """Advance agent one step."""
        self.color_hotspot()
        self.model.counts[self.atype] += 1  # Count agent type

    def color_hotspot(self):
        # Decide if this region agent is a hot-spot (if more than threshold person agents are infected)
        neighbors = self.model.grid.get_intersecting_agents(self)
        infected_neighbors = [
            neighbor for neighbor in neighbors if neighbor.atype == "infected"
        ]
        if len(infected_neighbors) >= self.hotspot_threshold:
            self.atype = "hotspot"
        else:
            self.atype = "safe"

    def __repr__(self):
        return "Neighborhood " + str(self.unique_id)


class InfectedModel(Model):
    """As 10 percent of the global population may have been infected by COVID-19, predicting and controlling for a pandemic has been the priority of public health since 2020. National and local governments worldwide have taken a series of measures to prevent unsafe contact. It is critical to develop effective intervention strategies and prevent future emerging infectious diseases. Therefore, an effective mathematical model is needed to capture the complex diffusion. In term of epidemic research, many compartmental models have been applied to study this pandemic and suggest public health policies"""
    # Geographical parameters for desired map
    MAP_COORDS = [51.553, 0.136]  # Centre of Barking and Dagenham
    geojson_regions = "ABMGRIDWGS.geojson"   
    unique_id = "GRID_ID"
    tree = pd.read_csv('tree.csv')
    tree_loc = pd.read_csv('tree_loc.csv')
    

    def __init__(self, infection_risk,in_lockdown, pop_size=0):
        #age_data = pd.read_csv('AgeData.csv')
        self.schedule = BaseScheduler(self)
        self.grid = GeoSpace()
        self.steps = 0
        self.counts = None
        self.reset_counts()
        # SIR model parameters
        self.infection_risk = infection_risk
        if in_lockdown == 'Yes':
            self.in_lockdown = True
        else:
            self.in_lockdown = False

        self.running = True
        self.datacollector = DataCollector(
            {
                "infected": get_infected_count,
                "exposed": get_exposed_count,
                "susceptible": get_susceptible_count,
                "recovered": get_recovered_count,
                "dead": get_dead_count,
            }
        )

        self.infectedgroupdatacollector = DataCollector(
            {
                "00to19": compute__infectedgroupAgeGroupC00to19,
                "20to29": compute__infectedgroupAgeGroupC20to29,
                "30to39": compute__infectedgroupAgeGroupC30to39,
                "40to49": compute__infectedgroupAgeGroupC40to49,
                "50to59": compute__infectedgroupAgeGroupC50to59,
                "60to69": compute__infectedgroupAgeGroupC60to69,
                "70to79": compute__infectedgroupAgeGroupC70to79,
                "80toXX": compute__infectedgroupAgeGroupC80toXX,
                "Allinfected": get_infected_count,
            }
        )

        self.deathgroupdatacollector = DataCollector(
            {
                "00to19": compute__deathgroupAgeGroupC00to19,
                "20to29": compute__deathgroupAgeGroupC20to29,
                "30to39": compute__deathgroupAgeGroupC30to39,
                "40to49": compute__deathgroupAgeGroupC40to49,
                "50to59": compute__deathgroupAgeGroupC50to59,
                "60to69": compute__deathgroupAgeGroupC60to69,
                "70to79": compute__deathgroupAgeGroupC70to79,
                "80toXX": compute__deathgroupAgeGroupC80toXX,
                "Alldeath": get_dead_count,
            }
        )

        # Set up the Neighbourhood patches for every region in file (add to schedule later)
        AC = AgentCreator(NeighbourhoodAgent, {"model": self})
        neighbourhood_agents = AC.from_file(
            self.geojson_regions, unique_id=self.unique_id
        )
        self.grid.add_agents(neighbourhood_agents)
        n=0
        for neighbourhood_agent in neighbourhood_agents:
            self.schedule.add(neighbourhood_agent)
            if neighbourhood_agent.Function == "residential":
                agent_size = neighbourhood_agent.Agent
                num_agents = agent_size
                num_agents = int(round(agent_size/50))
                ac_population = AgentCreator(PersonAgent, {"model": self,"residence":neighbourhood_agent.unique_id})
                pop_size += num_agents
                for k in range(num_agents):
                    this_person = ac_population.create_agent(neighbourhood_agent.shape.centroid, "P" + str(n))
                    n=n+1
                    self.grid.add_agents(this_person)
                    self.schedule.add(this_person)                
        self.counts["susceptible"] = pop_size-self.counts["infected"]-self.counts["dead"]-self.counts["recovered"]
        #self.counts["susceptible"] = 327-self.counts["infected"]
        # Add the neighbourhood agents to schedule AFTER person agents,
        # to allow them to update their color by using BaseScheduler
        self.datacollector.collect(self)
        self.infectedgroupdatacollector.collect(self)
        self.deathgroupdatacollector.collect(self)

    def reset_counts(self):
        self.counts = {
            "susceptible": 0,
            "infected": 0,
            "exposed": 0,
            "recovered": 0,
            "dead": 0,
            "safe": 0,
            "hotspot": 0,
        }

    def step(self):
        """Run one step of the model."""
        self.steps += 1
        self.reset_counts()
        self.schedule.step()
        self.grid._recreate_rtree()  # Recalculate spatial tree, because agents are moving
        self.datacollector.collect(self)
        self.infectedgroupdatacollector.collect(self)
        self.deathgroupdatacollector.collect(self)
        data = self.datacollector.get_model_vars_dataframe()
        infectedbyage = self.infectedgroupdatacollector.get_model_vars_dataframe()
        deathbyage = self.deathgroupdatacollector.get_model_vars_dataframe()
        data.to_csv (r'datax.csv', index = False, header=True)
        infectedbyage.to_csv (r'infectedbyage.csv', index = False, header=True)
        deathbyage.to_csv (r'deathbyage.csv', index = False, header=True)
        # Run until no one is infected
        if self.counts["infected"] == 0:
            self.running = False

# Functions needed for datacollector
def get_infected_count(model):
    return model.counts["infected"]

def get_exposed_count(model):
    return model.counts["exposed"]

def get_susceptible_count(model):
    return model.counts["susceptible"]


def get_recovered_count(model):
    return model.counts["recovered"]


def get_dead_count(model):
    return model.counts["dead"]

def compute__infectedgroupAgeGroupC00to19(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "00to19"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC00to19(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "00to19"):
            dead_count = dead_count + 1
    return dead_count

def compute__infectedgroupAgeGroupC20to29(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "20to29"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC20to29(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "20to29"):
            dead_count = dead_count + 1
    return dead_count

def compute__infectedgroupAgeGroupC30to39(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "30to39"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC30to39(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "30to39"):
            dead_count = dead_count + 1
    return dead_count

def compute__infectedgroupAgeGroupC40to49(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "40to49"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC40to49(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "40to49"):
            dead_count = dead_count + 1
    return dead_count

def compute__infectedgroupAgeGroupC50to59(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "50to59"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC50to59(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "50to59"):
            dead_count = dead_count + 1
    return dead_count

def compute__infectedgroupAgeGroupC60to69(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "60to69"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC60to69(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "60to69"):
            dead_count = dead_count + 1
    return dead_count

def compute__infectedgroupAgeGroupC70to79(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "70to79"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC70to79(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "70to79"):
            dead_count = dead_count + 1
    return dead_count

def compute__infectedgroupAgeGroupC80toXX(model):
    infected_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "infected") and (agent.age_group == "80toXX"):
            infected_count = infected_count + 1
    return infected_count

def compute__deathgroupAgeGroupC80toXX(model):
    dead_count = 0
    for agent in model.schedule.agents:
        if (agent.atype == "dead") and (agent.age_group == "80toXX"):
            dead_count = dead_count + 1
    return dead_count

# %%
