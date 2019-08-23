from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import matplotlib.pyplot as plt
import random
import numpy as np

import mining


class AgentCountLogger:
    count = 0

    def bind(logger, agent_class):
        class CountLoggingAgentClass(agent_class):
            def initialize(self):
                super().initialize()
                logger.count += 1

            def cleanup(self):
                super().cleanup()
                logger.count -= 1

        return CountLoggingAgentClass


def draw_sample(T):
    #world = World(200, 200, max_steps=T)
    world = World(w=mining.G, h=mining.G, torus_enabled=True, max_steps=T)
    # Add the agents to the world.
    base_logger = AgentCountLogger()
    BaseLog = base_logger.bind(mining.Base)
    for _ in range(mining.N):
        world.add_agent(BaseLog(), pos = Vec2D(random.randint(0,world.h), random.randint(0,world.h)))

    # Dispurse robots equally amongst bases initially
    explorer_logger = AgentCountLogger()
    ExplorerLog = explorer_logger.bind(mining.Explorer)
    for _ in range(mining.X):
        for j in range(mining.N):
            world.add_agent(ExplorerLog(), pos = world.agents[j].pos())

    transporter_logger = AgentCountLogger()
    TransporterLog = transporter_logger.bind(mining.Transporter)
    for _ in range(mining.Y):
        for j in range(mining.N):
            world.add_agent(TransporterLog(), pos = world.agents[j].pos())

    # Add ore on the map (as agents)
    ore_total = world.w * world.h * mining.D # The density of ores is multiplied with the mapsize to make the correct amount of ore
    ore_logger = AgentCountLogger()
    OreLog = ore_logger.bind(mining.Ore)
    for _ in range(int(ore_total)):
        world.add_agent(OreLog())

    explorer_counts = []
    transporter_counts = []
    base_counts = []
    ore_counts = []
    while not world.ended:
        explorer_counts.append(explorer_logger.count)
        transporter_counts.append(transporter_logger.count)
        base_counts.append(base_logger.count)
        ore_counts.append(ore_logger.count)
        world.step()
        #vis = Visualizer(world, target_speed=25)
        #vis.start()


    return [explorer_counts, transporter_counts, ore_counts] # [explorer_counts, transporter_counts, base_counts]


def main():
    T = mining.T
    n = 10
    data1 = np.empty((n, T))
    data2 = np.empty((n, T))
    data3 = np.empty((n, T))
    for i in range(n):
        print(i)
        [data1[i], data2[i], data3[i]] = draw_sample(T)

    mean1 = data1.mean(axis=0)
    std1 = data1.std(axis=0)
    mean2 = data2.mean(axis=0)
    std2 = data2.std(axis=0)
    mean3 = data3.mean(axis=0)
    std3 = data3.std(axis=0)

    t = list(range(T))
    f = plt.figure(1)
    plt.plot(t, mean1, 'k', label='mean')
    plt.fill_between(t, mean1 - std1, mean1 + std1, label='+- 1 std')
    plt.xlabel('time')
    plt.ylabel('number of agents')
    plt.legend()
    
    g = plt.figure(2)
    plt.plot(t, mean2, 'k', label='mean')
    plt.fill_between(t, mean2 - std2, mean2 + std2, label='+- 1 std')
    plt.xlabel('time')
    plt.ylabel('number of agents')
    plt.legend()
    
    h = plt.figure(3)
    plt.plot(t, mean3, 'k', label='mean')
    plt.fill_between(t, mean3 - std3, mean3 + std3, label='+- 1 std')
    plt.xlabel('time')
    plt.ylabel('number of agents')
    plt.legend()

    plt.show()


if __name__ == '__main__':
    main()
