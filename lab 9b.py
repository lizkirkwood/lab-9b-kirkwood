"""
Simple implementation of the Schelling model of segregation in Python
(https://www.uzh.ch/cmsssl/suz/dam/jcr:00000000-68cb-72db-ffff-ffffff8071db/04.02%7B_%7Dschelling%7B_%7D71.pdf)
For use in classes at the Harris School of Public Policy
"""

from numpy import random, mean

#note: update out_path to point to somewhere on your computer
params = {'world_size':(20,20),
          'num_agents':10,
          'max_iter'  :10,
          'out_path'  :r'C:\Users\ekirkwood\Documents\GitHub\lab-9b-kirkwood\results.csv' }

class Agent():
    def __init__(self, world):        
        self.world = world
        self.location = None

    def move(self):
        ## move to an empty path
       vacancies = self.world.find_vacant(return_all=True)
       for patch in vacancies:
           self.world.grid[self.location] = None #move out of current patch
           self.location = patch                 #assign new patch to myself
           self.world.grid[patch] = self         #update the grid
           return 1

class World():
    def __init__(self, params):
        assert(params['world_size'][0] * params['world_size'][1] > params['num_agents']), 'Grid too small for number of agents.'
        self.params = params
        self.reports = {}
        self.grid = self.build_grid(params['world_size'])
        self.agents = self.build_agents(params['num_agents'])
        self.init_world()

    def build_grid(self, world_size):
        """create the world that the agents can move around on"""
        locations = [(i,j) for i in range(world_size[0]) for j in range(world_size[1])]
        return {l:None for l in locations}
    
    def build_agents(self, num_agents): 
        agents = [Agent(self) for i in range(num_agents)]
        random.shuffle(agents)
        return agents


    def init_world(self):
        """a method for all the steps necessary to create the starting point of the model"""
        for agent in self.agents:
            loc = self.find_vacant()
            self.grid[loc] = agent
            agent.location = loc
        assert(all([agent.location is not None for agent in self.agents])), "Some agents don't have homes!"
        assert(sum([occupant is not None for occupant in self.grid.values()]) == self.params['num_agents']), 'Mismatch between number of agents and number of locations with agents.'


    def find_vacant(self, return_all=False):
        """finds all empty patches on the grid and returns a random one, unless kwarg return_all==True,
        then it returns a list of all empty patches"""
        empties = [loc for loc, occupant in self.grid.items() if occupant is None]
        if return_all:
            return empties
        else:
            choice_index = random.choice(range(len(empties)))
            return empties[choice_index]

    def report_integration(self):
        diff_neighbors = []
        for agent in self.agents:
            diff_neighbors.append(sum(
                    [not a for a in agent.am_i_happy(neighbor_check=True)]
                                ))
        self.reports['integration'].append(round(mean(diff_neighbors), 2))
 
    def run(self):
        """handle the iterations of the model"""
        log_of_moved = []
        log_of_stay  = []

        self.report_integration()
        log_of_moved.append(0) #no one moved at startup
        log_of_stay.append(0) #no one stayed at startup

        for iteration in range(self.params['max_iter']):

            random.shuffle(self.agents) #randomize agents before every iteration
            move_results = [agent.move() for agent in self.agents]
            self.report_integration()

            num_moved          = sum([r==1 for r in move_results])
            num_stayed_unhappy = sum([r==2 for r in move_results])

            log_of_moved.append(num_moved)
            log_of_stay.append(num_stayed_unhappy)

            if log_of_moved[-1] == log_of_stay[-1] == 0:
                print('Everyone is happy!  Stopping after iteration {}.'.format(iteration))
                break
            elif log_of_moved[-1] == 0 and log_of_stay[-1] > 0:
                print('Some agents are unhappy, but they cannot find anywhere to move to.  Stopping after iteration {}.'.format(iteration))
                break

        self.reports['log_of_moved'] = log_of_moved
        self.reports['log_of_stay']  = log_of_stay

        self.report()

    def report(self, to_file=True):
        """report final results after run ends"""
        reports = self.reports

        print('\nAll results begin at time=0 and go in order to the end.\n')
        print('The number of moves per turn:', reports['log_of_moved'])
        print('The number of agents who failed to find a new home:', reports['log_of_stay'])

        if to_file:
            out_path = self.params['out_path']
            with open(out_path, 'w') as f:
                headers = 'turn,integration,num_happy,num_moved,num_stayed\n'
                f.write(headers)
                for i in range(len(reports['log_of_happy'])):
                    line = ','.join([str(i),
                                     str(reports['integration'][i]),
                                     str(reports['log_of_happy'][i]),
                                     str(reports['log_of_moved'][i]),
                                     str(reports['log_of_stay'][i]),
                                     '\n'
                                     ])
                    f.write(line)
            print('\nResults written to:', out_path)

world = World(params)
world.run()
