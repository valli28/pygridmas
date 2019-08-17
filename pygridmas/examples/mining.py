from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random

# create world, torus or not
world = World(w=200, h=200, torus_enabled=True)


# extend the base Agent class
class Base(Agent):
    group_ids = {0}
    def initialize(self):
        # Called once when the agent enters a world.
        # After the agent is added to the world, a reference to the
        # world is stored in 'self.world'.
        self.color = Colors.YELLOW
        
        pass

    def step(self):
        # Called in 'world.step()' (at every step of the simulation).
        pass

    def receive_event(self, emitter_pos: Vec2D, data):
        # Handle events emitted from other agents.
        pass

    def cleanup(self):
        # Called when removed from the world,
        # or when 'world.cleanup()' is called.
        pass

class Ore(Agent):
    group_ids = {1}

    def initialize(self):
        self.color = Colors.BLUE
        
        pass

    def step(self):
        pass

    def receive_event(self, emitter_pos: Vec2D, data):
        pass

    def cleanup(self):

        pass

class Explorer(Agent):
    group_ids = {2}
    counter = 0
    destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))

    discovered_ore = set()

    stay = False

    def initialize(self):
        self.color = Colors.GREEN
        pass

    def step(self):

        if self.counter < 15 and self.stay != True :
            self.move_towards(self.destination)
            
        else:
            ores_found = self.box_scan(10, 1)
            if ores_found != None:
                # and emit an event to transporters for pickup
                self.discovered_ore.add(ore for ore in ores_found)
                self.emit_event(20, self.discovered_ore, 3)
                if len(self.discovered_ore) > 20:
                    self.stay = True
                else:
                    self.stay = False
                #print("Agent " + str(self.idx) + " has found " + str(len(self.discovered_ore)) + " ores")
            # Reset the counter and make a new destination
            self.counter = 0
            self.destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))

        self.counter = self.counter + 1
        pass

    def receive_event(self, emitter_pos: Vec2D, data):
        # Recieve an acknowledgement that a Transporter will pick up the ore and the explorer can delete it from its memory
        print("Explorer heard the transporter")
        self.discovered_ore.discard(ore for ore in data)
        pass

    def cleanup(self):

        pass

class Transporter(Agent):
    group_ids = {3}
    counter = 0
    destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))
    ore_to_pick_up = set()
    memory_capacity = 20
    inventory_capacity = 5

    def initialize(self):
        self.color = Colors.RED
        pass

    def step(self):
        if self.counter < 15:
            self.move_towards(self.destination)
            
        else:
            self.counter = 0
            self.destination = Vec2D(random.randint(0,world.h), random.randint(0,world.h))

        self.counter = self.counter + 1
        pass

    def receive_event(self, emitter_pos: Vec2D, data):
        print("Transporter got a message")
        if (len(self.ore_to_pick_up) + len(data)) < self.memory_capacity:
            self.ore_to_pick_up.add(ore for ore in data)
            self.emit_event(20, data, 2)
        pass

    def cleanup(self):
        pass

# Add the agent to the world.
# If no position is provided, a random position on the map is chosen.
world.add_agent(Base(), pos=Vec2D(x=50, y=50))
for i in range(2):
    world.add_agent(Explorer(), pos = world.agents[0].pos())
for i in range(2):
    world.add_agent(Transporter(), pos = world.agents[0].pos())
ore_total = world.w * world.h * 0.01
for i in range(int(ore_total)):
    world.add_agent(Ore())




# The world proceeds by calling 'world.step()'
world.step()

# Often, it's nice to visualize the world.
# The visualizer calls 'world.step()' and tries to maintain
# a certain speed (world steps per second).
vis = Visualizer(world, target_speed=100)
vis.start()