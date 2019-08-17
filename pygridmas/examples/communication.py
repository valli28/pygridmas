from pygridmas import Agent, World, Visualizer, Colors
import random

world = World(100, 100)

comm_rng = 10


class LonelyAgent(Agent):
    state = "LONELY"
    friend = None
    agent_group_id = None
    friendship_patience = None

    def initialize(self):
        self.agent_group_id = 'AGENT:{}'.format(self.idx)
        self.group_ids.add(self.agent_group_id)

    def step(self):
        if self.state == "LONELY":
            self.color = Colors.RED
            if random.randint(0, 20) == 0:
                self.emit_event(comm_rng, ("ANYONE THERE?", self.agent_group_id))
                self.color = Colors.MAGENTA
        elif self.state == "HOPEFUL":
            self.color = Colors.BLUE
            self.friendship_patience -= 1
            if self.friendship_patience == 0:
                self.friend = None
                self.state = "LONELY"
        elif self.state == "HAPPY":
            self.color = Colors.GREEN

    def receive_event(self, _, data):
        mes, sender, *rest = data
        if mes == "ANYONE THERE?" and self.friend is None:
            self.emit_event(comm_rng, ("IM HERE, FRIENDS?", self.agent_group_id), sender)
            self.friend = sender
            self.friendship_patience = 3
            self.state = "HOPEFUL"
        elif mes == "IM HERE, FRIENDS?" and self.friend is None:
            self.friend = sender
            self.state = "HAPPY"
            self.emit_event(comm_rng, ("OKAY, FRIENDS", self.agent_group_id), sender)
        elif mes == "OKAY, FRIENDS":
            self.state = "HAPPY"


for _ in range(100):
    world.add_agent(LonelyAgent())

vis = Visualizer(world, target_speed=5)
vis.start()