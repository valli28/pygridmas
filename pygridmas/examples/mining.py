from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random

# Setting up the environment
C = 1000        # Base storage capacity
D = 0.01        # Percentage-wise density of ores on the map
E = 300         # Energy units of robots.
G = 200         # Gridsize of map
M = 1           # Coordination mode (1 = cooperative, 0 = competetive)
N = 1           # Number of bases

# Setting up the robots
I = int(G/5)    # Communication scope of robots
P = int(G/20)   # Perception scope of robots
Q = 1           # Cost of a move-action
X = 3           # Number of Explorers per base
Y = 3           # Number of Transporters per base
S = X + Y - 1   # Memory capacity of robots
W = 5           # Maximum inventory capacity of a Transporter

# Setting up simulation
T = 2500        # Maximum number of cycles


class Base(Agent):
    group_ids = {0}
    ore_capacity = C
    end_the_world = False
    ore_counter = 0

    def initialize(self):
        # Called once when the agent enters a world.
        # After the agent is added to the world, a reference to the
        # world is stored in 'self.world'.
        self.color = Colors.YELLOW
        self.ore_in_storage = []
        self.ore_counter = 0
        
        pass

    def deposit(self, ore):        
        if len(self.ore_in_storage) < self.ore_capacity:
            for i in range(len(ore)) :
                self.ore_in_storage.append(ore[i])
                self.ore_counter += 1
                if ore[i].idx in self.world.active_agents: 
                    self.world.remove_agent(ore[i].idx)
        else:
            #self.emit_event(2, "Base full", ore) #Send signal base is full and coordinates to next base
            self.end_the_world = True
        

        pass
        
    def step(self):
        # Called in 'world.step()' (at every step of the simulation).
        if self.end_the_world:
            self.world.end()
        pass

    def receive_event(self, event_type, data):
        # Handle events emitted from other agents.
        pass

    def cleanup(self):
        # Called when removed from the world,
        # or when 'world.cleanup()' is called.
        print("Base " + str(self.idx) + " has recieved " + str(len(self.ore_in_storage)) + " ore in total")
        pass

class Ore(Agent):
    group_ids = {1}
    
    def initialize(self):
        self.color = Colors.BLUE
        self.picked = False
        self.current_agent = 0

        pass
    
    def pickup(self, picking_agent):
        self.picked = True
        self.color = Colors.BLACK
        self.current_agent = picking_agent
        
        pass

    def step(self):
        pass

    def receive_event(self, event_type, data):
        pass

    def cleanup(self):
        self.color = Colors.BLACK
        pass

class Explorer(Agent):
    group_ids = {2}
    memory_capacity = S 
    energy_capacity = E

    def initialize(self):
        self.group_collision_ids = {2, 3}
        self.color = Colors.GREEN
        self.destination = Vec2D(random.randint(0,self.world.h), random.randint(0,self.world.h))
        self.temp_ore = []
        self.discovered_ore = []
        self.ore_to_forget = []
        self.current_energy = self.energy_capacity
        self.state = "Exploring"
        self.counter = 0
        self.bases = []
        self.perception_radius = P
        self.communication_radius = I
        self.current_friend = None
        self.exploration_radius = random.randint(15, 30)


        for i in range(len(self.world.agents)):
            if self.world.agents[i].group_ids == {0}:
                self.bases.append(self.world.agents[i])
        self.memory_capacity = self.memory_capacity - len(self.bases)

        pass

    def find_nearest_base(self):
        distances = []
        for i in range(len(self.bases)):
            distances.append(self.dist(self.bases[i].pos()))
        return distances.index(min(distances))

    def consume_energy(self, amount):
        self.current_energy = self.current_energy - amount
    
    def step(self):
        if not self.world.ended: 
    #####################################################################################
            if self.dist(self.bases[self.find_nearest_base()].pos()) + 15 > self.current_energy:
                self.state = "Returning"

            if self.state == "Exploring":
                if self.counter < self.exploration_radius :
                    self.move_towards(self.destination)
                    self.group_collision_ids = {2, 3}
                    self.consume_energy(Q)

                else:
                    self.temp_ore = self.box_scan(rng = self.perception_radius, group_id = 1) #Only performs scans when moving
                    self.consume_energy(self.perception_radius) #Consuming energy due to perception radius
                    for i in range(len(self.temp_ore)):         # Add ore into memory until cap.
                        if len(self.discovered_ore) <= self.memory_capacity and self.temp_ore[i] not in self.discovered_ore:
                            self.discovered_ore.append(self.temp_ore[i])
                    if self.discovered_ore != None:
                        self.emit_event(self.communication_radius, "Pickup request", self.discovered_ore + [self.idx])
                        self.consume_energy(1) # Consume 1 energy unit due to communication
                    if len(self.discovered_ore) == self.memory_capacity:
                        self.state = "Requesting"                
                    
                    # Reset the counter and make a new destination
                    self.counter = 0
                    self.destination = Vec2D(random.randint(0,self.world.h), random.randint(0,self.world.h))
    #####################################################################################
            elif self.state == "Requesting":
                # Counter has just been set to zero and we already have a new destionation, 
                # but we stay (using that counter) until a Transporter has releived us of some memory-space
                if self.counter % 5 == 0: # Tries 10 times every fifth step to make pickup-request
                    self.emit_event(self.communication_radius, "Pickup request", self.discovered_ore)
                    self.consume_energy(1) # Consume 1 energy unit due to communication
                if self.counter > 50 : # Give up and go exploring again... will in reality only move once and try again
                    self.counter = 0
                    self.state = "Exploring"
                    self.discovered_ore = []
    #####################################################################################
            elif self.state == "Choosing":
                if self.discovered_ore != []:
                    for i in range(len(self.ore_to_forget)):
                        if self.ore_to_forget[i] in self.discovered_ore:
                            self.discovered_ore.remove(self.ore_to_forget[i])
                    self.emit_event(self.communication_radius, "Choose transporter", [self.current_friend, self.idx])
                self.current_friend = None
                self.state = "Exploring" # Now the explorers should not get stuck....
                
    #####################################################################################
            elif self.state == "Returning":
                self.destination = self.world.agents[self.find_nearest_base()].pos()
                self.move_towards(self.destination)
                self.consume_energy(Q)
                if self.pos() == self.destination: # Maybe change this into dist(pos, base)< 1.5 (lidt snyd)
                    self.group_collision_ids = set()
                    self.current_energy = self.energy_capacity
                    self.exploration_radius = random.randint(15, 30)
                    self.counter = 0
                    self.destination = Vec2D(random.randint(0,self.world.h), random.randint(0,self.world.h))
                    self.discovered_ore = []
                    self.current_friend = None
                    self.state = "Exploring"        
            
            if self.current_energy <= 0:
                print("Agent " + str(self.idx) + " died")
                self.world.remove_agent(self.idx)
            
            self.counter = self.counter + 1
            pass

    def receive_event(self, event_type, data):
        if event_type == "Pickup acknowledgement":
            if data[len(data)-2] == self.idx and self.current_friend == None: # My ID
                self.ore_to_forget = []
                self.state = "Choosing"
                self.current_friend = data[len(data) - 1] #Choose friend... No, it's just the first one. 
                for i in range(len(data) - 2):
                    self.ore_to_forget.append(data[i])
        pass

    def cleanup(self):
        self.color = Colors.GREY50
        self.group_collision_ids = set()
        pass


class Transporter(Agent):
    group_ids = {3}

    memory_capacity = S 
    inventory_capacity = W
    energy_capacity = E

    def initialize(self):
        self.group_collision_ids = {2, 3}
        self.color = Colors.RED
        self.destination = Vec2D(random.randint(0,self.world.h), random.randint(0,self.world.h))
        self.current_ore = []
        self.ore_to_pick_up = []
        self.ore_in_inventory = []
        self.temp_ore = []
        self.state = "Searching"
        self.counter = 0
        self.current_energy = self.energy_capacity
        self.communication_radius = I
        self.current_friend = None

        self.bases = []
        for i in range(len(self.world.agents)):
            if self.world.agents[i].group_ids == {0}:
                self.bases.append(self.world.agents[i])
        self.memory_capacity = self.memory_capacity - len(self.bases)
        pass

    def consume_energy(self, amount):
        self.current_energy = self.current_energy - amount
        pass

    def pick_base(self):
        distances = []
        for i in range(len(self.bases)):
            distances.append(self.dist(self.bases[i].pos()))
        distances[distances.index(min(distances))] = 1000
        return distances.index(min(distances))

    def find_nearest_base(self):
        distances = []
        for i in range(len(self.bases)):
            distances.append(self.dist(self.bases[i].pos()))
        return distances.index(min(distances))

    def step(self):
        if not self.world.ended:
            if self.dist(self.bases[self.find_nearest_base()].pos()) + 15 > self.current_energy:
                self.destination = self.bases[self.find_nearest_base()].pos()
                self.state = "Returning"

    #####################################################################################            
            if self.state == "Searching":
                self.group_collision_ids = {2, 3}
                if self.counter < 20 :
                    self.move_towards(self.destination)
                    self.consume_energy(Q)
                else:
                    self.counter = 0
                    self.destination = Vec2D(random.randint(0,self.world.h), random.randint(0,self.world.h))
    #####################################################################################
            elif self.state == "Pickup" :
                if len(self.ore_in_inventory) >= self.inventory_capacity: # Inventory full
                    self.destination = self.bases[self.find_nearest_base()].pos()
                    self.state = "Returning"
                elif len(self.ore_to_pick_up) < 1:
                    self.state = "Searching"
                else:
                    # Picking a new target
                    self.current_ore = self.ore_to_pick_up[0] #random.randint(0, len(self.ore_to_pick_up)-1)
                    if self.current_ore.idx in self.world.active_agents: #if self.current_ore.picked == False:
                        self.destination = self.current_ore.pos()
                        self.move_towards(self.destination)
                        self.consume_energy(Q)
                        self.state = "Moving"
                    else: 
                        self.ore_to_pick_up.remove(self.current_ore)
                        self.state = "Pickup"
    #####################################################################################
            elif self.state == "Moving":
                self.move_towards(self.destination)
                self.consume_energy(Q)
                if self.pos() == self.destination:
                    #deactive ore and remove from memory
                    self.ore_to_pick_up.remove(self.current_ore)
                    if self.current_ore.idx in self.world.active_agents: #if self.current_ore.picked == False:
                        self.current_ore.pickup(self) # Tell the ore that it has been picked up
                        self.ore_in_inventory.append(self.current_ore)
                        self.consume_energy(1) #Picking an ore costs 1 energy
                    self.state = "Pickup"
    #####################################################################################
            elif self.state == "Acknowledging":
                # self.temp_ore now has as many ores as I can handle. Acknowledge back with my and friend's ID
                self.emit_event(self.communication_radius, "Pickup acknowledgement", self.temp_ore + [self.current_friend, self.idx])
                self.consume_energy(1)
                self.state = "Pickup" 
                
    #####################################################################################
            elif self.state == "Returning":
                self.move_towards(self.destination)
                self.consume_energy(Q)
                if self.pos() == self.destination :
                    self.group_collision_ids = set()
                    self.bases[self.find_nearest_base()].deposit(self.ore_in_inventory) # Depositing ore into base
                    self.ore_in_inventory = []# Removing ore from inventory'
                    self.current_energy = self.energy_capacity #Recharging
                    #if self.ore_to_pick_up != []:
                    #    self.destination = self.ore_to_pick_up[0].pos()
                    #else:
                    # This is not very smart... 
                    self.destination = Vec2D(random.randint(0,self.world.h), random.randint(0,self.world.h))
                    self.state = "Pickup"
    #####################################################################################
            
            self.counter = self.counter + 1

            if self.current_energy <= 0:
                print("Agent " + str(self.idx) + " died")
                self.world.remove_agent(self.idx)
            pass

    def receive_event(self, event_type, data):
        # We have to have a big IF around this whole thing checking whether it is from one of our own agents
        # if ... maybe in the event_type? (some string manipulation) so that we won't fuck with the data!
        if event_type == "Pickup request" and (self.state == "Searching" or self.state == "Moving"): 
            self.state = "Acknowledging"
            self.current_friend = data[len(data)-1]
            self.temp_ore = []
            for i in range(self.memory_capacity - len(self.ore_to_pick_up)): # Memory left
                if i < len(data) - 1:
                    if data[i] not in self.ore_to_pick_up: # Make sure there are no duplicates
                        self.temp_ore.append(data[i])

        if event_type == "Choose transporter":
            if data[0] == self.idx and data[1] == self.current_friend:
                self.ore_to_pick_up += self.temp_ore
                self.state = "Pickup"
                self.current_friend = None

        if event_type == "Base full":
            self.destination = self.bases[self.pick_base()].pos()
            self.current_energy = self.energy_capacity
            self.state = "Returning"      
        pass

    def cleanup(self):
        pass

def main():
    world = World(w=G, h=G, torus_enabled=True, max_steps=T) # create world, torus or not
    # Add the agents to the world.
    for _ in range(N):
        world.add_agent(Base(), pos = Vec2D(random.randint(0,world.h), random.randint(0,world.h)))

    # Dispurse robots equally amongst bases initially
    for _ in range(X):
        for j in range(N):
            world.add_agent(Explorer(), pos = world.agents[j].pos())

    for _ in range(Y):
        for j in range(N):
            world.add_agent(Transporter(), pos = world.agents[j].pos())

    # Add ore on the map (as agents)
    ore_total = world.w * world.h * D # The density of ores is multiplied with the mapsize to make the correct amount of ore
    for _ in range(int(ore_total)):
        world.add_agent(Ore())

    # The world proceeds by calling 'world.step()'
    while not world.ended:
        world.step()

    # Often, it's nice to visualize the world.
    # The visualizer calls 'world.step()' and tries to maintain
    # a certain speed (world steps per second).
    #vis = Visualizer(world, target_speed=25)
    #vis.start()


if __name__ == '__main__':
    main()




