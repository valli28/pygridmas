from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random

# create world, torus or not
world = World(w=200, h=200, torus_enabled=True)


# extend the base Agent class
class Base(Agent):
    group_ids = {0}
    #ore_capacity = 400
    def initialize(self):
        # Called once when the agent enters a world.
        # After the agent is added to the world, a reference to the
        # world is stored in 'self.world'.
        self.color = Colors.YELLOW
        self.ore_in_storage = []
        
        pass

    def deposit(self, ore):
        for i in range(len(ore)) :
           # if self.ore_in_storage < ore_capacity:
                self.ore_in_storage.append(ore[i])
           # else
            #    self.emit_event(20, "Base full", world.agents[0].pos()) #Send signal base is full and coordinates to next base


        pass
        

    def step(self):
        # Called in 'world.step()' (at every step of the simulation).
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
        print("Agent " + str(self.current_agent.idx) + " has picked me up")
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
    group_collision_ids = {2, 3}

    energy_capacity = 1000


    def initialize(self):
        self.color = Colors.GREEN
        self.destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))
        self.temp_ore = set()
        self.current_energy = self.energy_capacity
        self.state = "Exploring"
        self.counter = 0
        self.bases = []

        for i in range(len(world.agents)):
            if world.agents[i].group_ids == {0}:
                self.bases.append(world.agents[i])

        pass

    def find_nearest_base(self):
        distances = []
        for i in range(len(self.bases)):
            distances.append(self.dist(self.bases[i].pos()))
        return distances.index(min(distances))

    def consume_energy(self, amount):
        self.current_energy = self.current_energy - amount
    
    def step(self):
#####################################################################################
        if self.dist(world.agents[0].pos()) + 10 > self.current_energy:
            print("Explorer " + str(self.idx) + " almost out of energy. Returning to base")
            self.state = "Returning"

        if self.state == "Exploring":
            if self.counter < 20 :
                self.move_towards(self.destination)
                self.consume_energy(1)
                self.counter = self.counter + 1
            else:
                energy_capacity_percent = (self.current_energy/self.energy_capacity)
                perception_radius = int((world.w/20)*energy_capacity_percent) #Perception radius dependent on energy left
                self.temp_ore = self.box_scan(rng = perception_radius, group_id = 1) #Only performs scans when moving
                self.consume_energy(perception_radius) #Consuming energy due to perception radius
                if self.temp_ore != None:
                    self.emit_event(20, "Pickup request", self.temp_ore)
                    self.consume_energy(1) # Consume energy due to communication
                # Reset the counter and make a new destination
                self.counter = 0
                self.destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))
#####################################################################################
        elif self.state == "Returning":
            self.destination = world.agents[self.find_nearest_base()].pos()
            self.move_towards(self.destination)
            self.consume_energy(1)
            if self.pos() == self.destination:
                print("Explorer reached base. Recharging energy")
                self.current_energy = self.energy_capacity
                self.state = "Exploring"        

        pass

    def receive_event(self, event_type, data):

        pass

    def cleanup(self):

        pass

class Transporter(Agent):
    group_ids = {3}
    group_collision_ids = {2, 3}
    memory_capacity = 20
    inventory_capacity = 5
    energy_capacity = 1000

    def initialize(self):
        self.color = Colors.RED
        self.destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))
        self.current_ore = []
        self.ore_to_pick_up = []
        self.ore_in_inventory = []
        self.state = "Searching"
        self.counter = 0
        self.current_energy = self.energy_capacity

        self.bases = []
        for i in range(len(world.agents)):
            if world.agents[i].group_ids == {0}:
                self.bases.append(world.agents[i])

        pass

    def consume_energy(self, amount):
        self.current_energy = self.current_energy - amount

    def find_nearest_base(self):
        distances = []
        for i in range(len(self.bases)):
            distances.append(self.dist(self.bases[i].pos()))
        return distances.index(min(distances))

    def step(self):
#####################################################################################
        if self.dist(world.agents[0].pos()) + 10 > self.current_energy:
            print("Transporter " + str(self.idx) + " almost out of energy. Returning to base")
            self.state = "Returning"
        if self.state == "Searching":
            if self.counter < 15 :
                self.move_towards(self.destination)
                self.consume_energy(1)
            else:
                self.counter = 0
                self.destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))
#####################################################################################
        elif self.state == "Pickup" :
            if len(self.ore_in_inventory) > self.inventory_capacity:
                print("Inventory full on " + str(self.idx) + ". Returning to base")
                self.state = "Returning"
            elif len(self.ore_to_pick_up) < 2:
                print("Ran out of ore to find. Searching for an Explorer")
                self.state = "Searching"
            else:
                # Picking a new target
                self.current_ore = self.ore_to_pick_up[0] #random.randint(0, len(self.ore_to_pick_up)-1)
                if self.current_ore.picked == False:
                    self.destination = Vec2D(self.current_ore.pos().x, self.current_ore.pos().y)
                    self.move_towards(self.destination)
                    self.consume_energy(1)
                    self.state = "Moving"
                else: 
                    self.ore_to_pick_up.remove(self.current_ore)
                    self.state = "Pickup"
#####################################################################################
        elif self.state == "Moving":
            self.move_towards(self.destination)
            self.consume_energy(1)
            if self.pos() == self.destination:
                #deactive ore and remove from memory
                self.ore_to_pick_up.remove(self.current_ore)
                if self.current_ore.picked == False:
                    print("Found valid ore. Picking ore from world.")
                    self.current_ore.pickup(self) # Tell the ore that it has been picked up
                    self.ore_in_inventory.append(self.current_ore)
                    self.consume_energy(1) #Picking an ore costs 1 energy
                self.state = "Pickup"
#####################################################################################
        elif self.state == "Returning":
            self.destination = world.agents[self.find_nearest_base()].pos()
            self.move_towards(self.destination)
            self.consume_energy(1)
            if self.pos() == self.destination :
                world.agents[self.find_nearest_base()].deposit(self.ore_in_inventory) # Depositing ore into base
                self.ore_in_inventory = []# Removing ore from inventory'
                self.current_energy = self.energy_capacity #Recharging
                self.state = "Searching"
        
        #print("Agent number " + str(self.idx) + " has " + str(len(self.ore_to_pick_up)) + " to pick up")

        self.counter = self.counter + 1

        pass

    def receive_event(self, event_type, data):
        if event_type == "Pickup request" and (self.state == "Searching" or self.state == "Moving"): 
            if (len(self.ore_to_pick_up) + len(data)) < self.memory_capacity: # Currently does not take partial orders, only complete dumps.
                for i in range(len(data)):
                    if data[i] not in self.ore_to_pick_up:# Make sure there are no duplicates
                        self.ore_to_pick_up.append(data[i]) 
                self.state = "Pickup" 
        #if event_type == "Base full": 
         #   self.state = "Returning"      
        pass

    def cleanup(self):
        pass

# Add the agents to the world.
world.add_agent(Base(), pos=Vec2D(x=50, y=50))
world.add_agent(Base(), pos=Vec2D(x=150, y=150))
world.add_agent(Base(), pos=Vec2D(x=150, y=50))

# Dispurse robots equally amongst bases initially
for i in range(2):
    world.add_agent(Explorer(), pos = world.agents[0].pos())
    world.add_agent(Explorer(), pos = world.agents[1].pos())
    world.add_agent(Explorer(), pos = world.agents[2].pos())
for i in range(2):
    world.add_agent(Transporter(), pos = world.agents[0].pos())
    world.add_agent(Transporter(), pos = world.agents[1].pos())
    world.add_agent(Transporter(), pos = world.agents[2].pos())

# Add ore on the map (as agents)
ore_total = world.w * world.h * 0.01
for i in range(int(ore_total)):
    world.add_agent(Ore())


# The world proceeds by calling 'world.step()'
world.step()

# Often, it's nice to visualize the world.
# The visualizer calls 'world.step()' and tries to maintain
# a certain speed (world steps per second).
vis = Visualizer(world, target_speed=25)
vis.start()