from OpenNero import *
from common import *

import Maze
from Maze.constants import *
import Maze.agent
from Maze.agent import *

def manhattan_heuristic(r, c):
    return abs(ROWS - r) + abs(COLS - c) 

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
        self.heuristic = manhattan_heuristic
        self.limit = 0
        self.min_heuristic = float('inf')
        self.choices_remaining = 0

    def reset(self):
        """
        Reset the agent
        """
        self.visited = set([])
        self.adjlist = {}
        self.parents = {}
        self.backpointers = {}
        self.min_heuristic = float('inf')
        self.choices_remaining = 0

    def initialize(self, init_info):
        """
        Initializes the agent upon reset
        """
        self.constraints = init_info.actions
        return True

    def start(self, time, observations):
        """
        Called on the first move
        """
        self.limit = self.heuristic(observations[0], observations[1]) + self.get_distance(observations[0], observations[1])

        print ('limit is {0}'.format(self.limit))
        return self.dfs_action(observations)
    
    def act(self, time, observations, reward):
        """
        Called every time the agent needs to take an action
        """
        return self.dfs_action(observations)

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

    def mark_path(self, r, c):
        get_environment().mark_maze_white(r, c)

    def get_cost(self, r, c, parent_row, parent_col):
        added_backpointer = False
        if (r, c) not in self.backpointers:
            self.backpointers[(r,c)] = (parent_row, parent_col)
            added_backpointer = True

        heuristic = self.heuristic(r, c)
        distance = self.get_distance(r, c)
        
        if added_backpointer:
            self.backpointers.pop((r,c))
        
        return (heuristic + distance)
   
    def dfs_action(self, observations):
        r = observations[0]
        c = observations[1]
        # if we have not been here before, build a list of other places we can go
        if (r, c) not in self.visited: #check heuristic cost of (r,c)
            tovisit = []
            for m, (dr, dc) in enumerate(MAZE_MOVES):
                r2, c2 = r + dr, c + dc
                if not observations[2 + m]: # can we go that way?
                    if (r2, c2) not in self.visited:
                        cost_of_move = self.get_cost(r2, c2, r, c)
                        if cost_of_move <= self.limit:
                            tovisit.append((r2, c2))
                            self.parents[(r2,c2)] = (r,c)
                            self.choices_remaining += 1
                            print ('added move to {0} with cost {1}'.format((r2,c2), cost_of_move))
                        else:
                            print ('skipped move to {0} with cost {1}'.format((r2,c2), cost_of_move))
                            """
                            if cost_of_move < self.min_heuristic:
                                self.min_heuristic = cost_of_move
                                print 'min is now {0}'.format(self.min_heuristic)
                            """
            # remember the cells that are adjacent to this one
            self.adjlist[(r, c)] = tovisit
        # if we have been here before, check if we have other places to visit
        #check heuristic against limit
        adjlist = self.adjlist[(r, c)]
        k = 0
        while k < len(adjlist) and adjlist[k] in self.visited: 
            k += 1
        
        v = self.constraints.get_instance()  # make the action vecotr to return
        if self.choices_remaining:
            # if we don't have other neighbors to visit, back up
            if k == len(adjlist):
                current = self.parents[(r, c)]
            else: # otherwise visit the next place
                current = adjlist[k]
                self.choices_remaining -= 1

            self.visited.add((r, c)) # add this location to visited list
            get_environment().mark_maze_blue(r, c) # mark it as blue on the maze
            dr, dc = current[0] - r, current[1] - c # the move we want to make
            v[0] = get_action_index((dr, dc))
            # remember how to get back
            if (r + dr, c + dc) not in self.backpointers:
                self.backpointers[(r + dr, c + dc)] = (r, c)
            print ('chose move to {0} with cost {1}'.format(
                (current[0], current[1]),
                self.get_cost(current[0], current[1], r, c)))
        else:    
            self.limit += 1 
            # self.limit = self.min_heuristic
            # reset the agents previous DFS data
            self.reset()
            # teleport back to 0 and return null move to restart dfs search with new llimit
            get_environment().teleport(self, 0, 0)
            v[0] = 4
            print ('teleported back to 0,0 and restarted DFS with limit = {0}'.format(self.limit))
        
        return v
