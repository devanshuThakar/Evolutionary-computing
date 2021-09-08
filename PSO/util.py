class Graph:

    def __init__(self, total_vertices):
        self.adjList = {} # dictionary of edges
        self.vertices = set() # set of vertices
        self.total_vertices = total_vertices
        self.weightMatrix =[]
    
    def addEdge(self, src, dest):
        try:
            self.adjList[src].add(dest)
        except KeyError:
            self.adjList[src] = {dest}
    
    def removeEdge(self, src, dest):
        if self.adjList[src]:
            self.addEdge.remove(dest)

class Particle:
    def __init__(self, solution, cost):
        # Current solution or sequence of vetices
        self.solution=solution

        #best solution of particle
        self.pbest = solution

        #set costs
        self.cost_current_solution = cost
        self.cost_pbest_solution = cost

        # velocity of particle as a tuple of 
        self.velocity = []
    
    def updateCurrentCost(self, Weights):
        newcost = 0
        for i in range(1,len(self.solution)):
            newcost += Weights[self.solution[i-1]][self.solution[i]]
        self.cost_current_solution = newcost

    def update_pbest(self):
        if(self.cost_current_solution <= self.cost_pbest_solution):
            self.pbest = self.solution[:]
            self.cost_pbest_solution = self.cost_current_solution

    def isValidSolution(self, graph):
        isvalid=True
        for i in range(1,len(self.solution)):
            if(self.solution[i] in graph.adjList[self.solution[i-1]]):
                continue
            else:
                isvalid = False
                break
        return isvalid

def isValidSolu(solution, graph):
    ans=True
    for i in range(1,len(solution)):
        if(solution[i] in graph.adjList[solution[i-1]]):
            continue
        else:
            return False
    return ans