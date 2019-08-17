from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import colorsys
import math

brush_radius = 5
size = 100
world = World(w=size, h=size, torus_enabled=True)


class Canvas(Agent):
    color = Colors.BLACK

    def initialize(self):
        # If there are many agents with no step method,
        # performance can be increased by deactivating them.
        self.deactivate()

    def step(self):
        # Will not be called because of deactivation.
        pass

    def receive_event(self, event_type, data):
        if event_type == "PAINT":
            emit_pos = data
            dir = -self.vec_to(emit_pos)
            dist = dir.magnitude()
            dir_angle = (dir.angle() + (self.world.time * 0.1)) % (math.pi * 2)
            hue = dir_angle / (2 * math.pi)

            if dist < brush_radius:
                self.color = colorsys.hsv_to_rgb(hue, 1, 1)
            if dist < brush_radius * 0.5:
                self.color = Colors.WHITE


for x in range(size):
    for y in range(size):
        world.add_agent(Canvas(), Vec2D(x, y))


class Brush(Agent):
    color = Colors.WHITE
    start_target: Vec2D = None
    reached_target = False

    def step(self):
        self.move_rel(Vec2D.random_grid_dir())
        self.emit_event(brush_radius, "PAINT", self.pos())


world.add_agent(Brush(), Vec2D(size // 2, size // 2))

vis = Visualizer(world, scale=3, target_speed=100)
vis.start()
