from OpenNero import *
from common import *

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

class IdaStarSearchAgent(SearchAgent):
    """
    IDA* algorithm
    """
    def __init__(self):
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.visited = set([])
        self.adjlist = {}
        self.parents = {}
        self.cost = {}
        self.threshold = 0
        self.heuristic = manhattan_heuristic

    def mark_path(self, r, c):
	get_environment().mark_maze_white(r, c)

    def reset(self):
        """
        Reset the agent
        """
        self.heuristic = manhattan_heuristic

    def minimum(cost):
        smallest = 1000000
        for elt in cost:
           if cost[elt] < smallest:
             smallest = cost[elt]
        return smallest

    def ida_action(self, observations):
        r = observations[0]
        c = observations[1]

        if (r, c) not in self.visited:
           tovisit = []
           for m, (dr, dc) in enumerate(MAZE_MOVES):
            r2, c2 = r + dr, c + dc
            if not observations[2 + m]:
                if (r2, c2) not in self.visited:
                #get cost
                  self.cost[(r2, c2)] = self.getCost(r2, c2)
                #if cost is below threshold, add to nodes to visit
                  if self.cost[(r2, c2)] <= self.threshold:
                    tovisit.append((r2, c2))
                    self.parents[(r2, c2)] = (r, c)
            self.adjlist[(r, c)] = tovisit
        adjlist = self.adjlist[(r, c)]
	v = self.action_info.get_instance()
	if self.parents:
		k = 0
		while k < len(adjlist) and adjlist[k] in self.visited:
		  k += 1
		if k == len(adjlist):
		  current = self.parents[(r, c)]
		else:
		  current = adjlist[k]
		self.visited.add((r, c))
		get_environment().mark_maze_blue(r, c)
		dr, dc = current[0] - r,  current[1] - c
		v[0] = get_action_index((dr, dc))
		if (r + dr, c + dc) not in self.backpointers:
		  self.backpointers[(r + dr, c + dc)] = (r, c)
        #check if all nodes under cost have been visited
	print(self.threshold , "is the threshold and " , self.cost)
        exhausted = True
        for elt in self.parents:
          if elt not in self.visited:
            exhausted = False
	#reset data and teleport back to start with new threshold
        if exhausted:
          self.visited = set([])
          self.adjlist = {}
          self.parents = {}
          self.threshold += 1  # minimum(self.cost)
          self.cost = {}
          self.backpointers = {}
          get_environment().teleport(self, 0, 0)
          v[0] = 4
        return v
    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.action_info = init_info.actions
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        self.threshold = 0#self.getCost(observations[0], observations[1])
        return self.ida_action(observations)
    
    def act(self, time, observations, reward):
        """
        Called every time the agent needs to take an action
        """
        return self.ida_action(observations)

    def end(self, time, reward):
        """
        at the end of an episode, the environment tells us the final reward
        """
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        self.reset()
        return True

    def destroy(self):
        """
        After one or more episodes, this agent can be disposed of
        """
        return True

    def getCost(self, r, c):
        return self.get_distance(r, c) + self.heuristic(r, c)
