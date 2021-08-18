#%%
from mesa.datacollection import DataCollector
from mesa import Model
from mesa.time import BaseScheduler
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
from shapely.geometry import shape, GeometryCollection, Point
import random
import pandas as pd

#%%
class PersonAgent(GeoAgent):
    """Person Agent."""

    def __init__(
        self,
        unique_id,
        model,
        shape,
        agent_type="susceptible",
        mobility_range=100,
        recovery_rate=0.2,
        death_risk=0.1,
        init_infected=0.1,
        residence='',
    ):
        """
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param shape:       Shape object for the agent
        :param agent_type:  Indicator if agent is infected ("infected", "susceptible", "recovered" or "dead")
        :param mobility_range:  Range of distance to move in one step
        """
        super().__init__(unique_id, model, shape)
        # Agent parameters
        self.atype = agent_type
        self.mobility_range = mobility_range
        self.recovery_rate = recovery_rate
        self.death_risk = death_risk
        #self.residence = self.grid.   

        # Random choose if infected
        if self.random.random() < init_infected:
            self.atype = "infected"
            self.model.counts["infected"] += 1  # Adjust initial counts
            self.model.counts["susceptible"] -= 1


    def step(self):
        """Advance one step."""
        tree = pd.read_csv('tree.csv')
        # If susceptible, check if exposed
        if self.atype == "susceptible":
            neighbors = self.model.grid.get_neighbors_within_distance(
                self, self.model.exposure_distance
            )
            for neighbor in neighbors:
                if (
                    neighbor.atype == "infected"
                    and self.random.random() < self.model.infection_risk
                ):
                    self.atype = "infected"
                    break

        # If infected, check if it recovers or if it dies
        elif self.atype == "infected":
            if self.random.random() < self.recovery_rate:
                self.atype = "recovered"
            elif self.random.random() < self.death_risk:
                self.atype = "dead"

        # If not dead, move
        if self.atype != "dead":
            #self.move()
            # move_x = random.randint(-50, 50)
            # move_y = random.randint(-50, 50)
            # move point to Retail and Recreation on weekend
            #random.randint(0, 273)
            # move point to Grocery everyday
            # move point to Pharmacy on weekend
            # move point to Parks on weekend
            # move point to Transit stations on weekdays
            # move point to Workplaces on weekdays
            #random.randint(0, 218)
            #new_position = Point(1+move_x,2+move_y)
            new_position = self.random.choice(allother)
            self.shape = new_position  # Reassign shape

        self.model.counts[self.atype] += 1  # Count agent type
    
    # def move(self):
        
    #     new_position = self.random.choice(allother)

    #     self.model.grid.move_agent(self, new_position)

    def __repr__(self):
        return "Person " + str(self.unique_id)


class NeighbourhoodAgent(GeoAgent):
    """Neighbourhood agent. Changes color according to number of infected inside it."""

    def __init__(self, unique_id, model, shape, agent_type="safe", hotspot_threshold=1):
        """
        Create a new Neighbourhood agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param shape:       Shape object for the agent
        :param agent_type:  Indicator if agent is infected ("infected", "susceptible", "recovered" or "dead")
        :param hotspot_threshold:   Number of infected agents in region to be considered a hot-spot
        """
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

model_params = {
    "pop_size": 2000,
    "init_infected": 0.2,
    "exposure_distance": 50,
    "infection_risk": 0.1,
}

class InfectedModel(Model):
    """Model class for a simplistic infection model."""
    # Geographical parameters for desired map
    MAP_COORDS = [51.553, 0.136]  # Centre of Barking and Dagenham
    geojson_regions = "ABMGRIDWGS.geojson"   
    unique_id = "GRID_ID"

    def __init__(self, pop_size, init_infected, exposure_distance, infection_risk):
        """
        Create a new InfectedModel
        :param pop_size:        Size of population
        :param init_infected:   Probability of a person agent to start as infected
        :param exposure_distance:   Proximity distance between agents to be exposed to each other
        :param infection_risk:      Probability of agent to become infected, if it has been exposed to another infected
        """
        self.schedule = BaseScheduler(self)
        self.grid = GeoSpace()
        self.steps = 0
        self.counts = None
        self.reset_counts()

        # SIR model parameters
        self.pop_size = pop_size
        self.counts["susceptible"] = pop_size
        self.exposure_distance = exposure_distance
        self.infection_risk = infection_risk

        self.running = True
        self.datacollector = DataCollector(
            {
                "infected": get_infected_count,
                "susceptible": get_susceptible_count,
                "recovered": get_recovered_count,
                "dead": get_dead_count,
            }
        )

        # Set up the Neighbourhood patches for every region in file (add to schedule later)
        AC = AgentCreator(NeighbourhoodAgent, {"model": self})
        neighbourhood_agents = AC.from_file(
            self.geojson_regions, unique_id=self.unique_id
        )
        #neighbors = self.model.grid.get_neighbors_within_distance(self, 1000)
        n=0
        # work=[]
        # rar=[]
        allother=[]
        for neighbourhood_agent in neighbourhood_agents:
            if neighbourhood_agent.Function == "residential":
                agent_size = neighbourhood_agent.Agent
                res_id = neighbourhood_agent.unique_id
                ac_population = AgentCreator(
                    PersonAgent, {"model": self, "init_infected": init_infected}
                )                
                for i in range(int(agent_size/300)):
                    this_person = ac_population.create_agent(
                        neighbourhood_agent.shape.centroid, "P" + str(n)
                    )
                    print(this_person.atype)
                    n=n+1
                    self.grid.add_agents(this_person)
                    self.schedule.add(this_person)
            else:
                allother.append(neighbourhood_agent.shape.centroid)
            # elif neighbourhood_agent.Function == "green":
            #     neighbourhood_agent.shape.centroid
            # elif neighbourhood_agent.Function == "grocery":
            #     neighbourhood_agent.shape.centroid
            # elif neighbourhood_agent.Function == "transport":
            #     neighbourhood_agent.shape.centroid
            # elif neighbourhood_agent.Function == "pharmacy":
            #     neighbourhood_agent.shape.centroid
            # elif neighbourhood_agent.Function == "rar":
            #     rar.append(neighbourhood_agent.shape.centroid)          
            # elif neighbourhood_agent.Function == "work":
            #     work.append(neighbourhood_agent.shape.centroid)

        # Add the neighbourhood agents to schedule AFTER person agents,
        # to allow them to update their color by using BaseScheduler
        for agent in neighbourhood_agents:
            self.schedule.add(agent)

        self.datacollector.collect(self)

    def reset_counts(self):
        self.counts = {
            "susceptible": 0,
            "infected": 0,
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

        # Run until no one is infected
        if self.counts["infected"] == 0:
            self.running = False

# %%
