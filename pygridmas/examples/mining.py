from pygridmas import World, Agent, Vec2D, Colors, Visualizer

# create world, torus or not
world = World(w=100, h=100, torus_enabled=True)


# extend the base Agent class
class Base(Agent):

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

    def initialize(self):
        self.color = Colors.GREEN
        pass

    def step(self):
        pass

    def receive_event(self, emitter_pos: Vec2D, data):
        pass

    def cleanup(self):

        pass

class Transporter(Agent):

    def initialize(self):
        self.color = Colors.RED
        pass

    def step(self):
        pass

    def receive_event(self, emitter_pos: Vec2D, data):
        pass

    def cleanup(self):
        pass

# Add the agent to the world.
# If no position is provided, a random position on the map is chosen.
world.add_agent(Base(), pos=Vec2D(x=50, y=50))
for i in range(5):
    world.add_agent(Explorer())
for i in range(5):
    world.add_agent(Transporter())
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