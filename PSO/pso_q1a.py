from util import Graph, Particle, isValidSolu
import csv
import os
import imageio
import random, copy, itertools
from operator import attrgetter
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as ani

filename1 = 'cities_distance.csv'
filename2 = 'cities_status.csv'
with open(filename1, 'r') as file:
    Weights = [list(map(int, x)) for x in csv.reader(file, delimiter=',')]

with open(filename2, 'r') as file:
    # cities_status is list of two lists - (1) list of city names (2) list of color
    cities_status = list(csv.reader(file, delimiter=','))

total_cities= 9
graph = Graph(total_cities)
tot_particles = 2000
alfa = 0.9
beta = 0.9
iterations = 100
Particles = []

#Loop for making the graph
for i in range(total_cities):
    if(cities_status[1][i] == 'yellow'):
        for j in range(total_cities):
            if (cities_status[1][j]!='green' and j!=i):
                graph.addEdge(i,j)
    
    elif(cities_status[1][i]=='red'):
        for j in range(total_cities):
            if (cities_status[1][j]!='green' and cities_status[1][j]!='yellow' and j!=i):
                graph.addEdge(i,j)
            
    else:
         for j in range(total_cities):
            if (j!=i):
                graph.addEdge(i,j)

print("The network of cities represented using a graph having adjacency list : \n", graph.adjList)

current_total_particles = 0
# Loop to make random particles (path)
while(current_total_particles<tot_particles):
    try:
        temp_sol = []
        curr = random.randint(0,8)
        temp_sol.append(curr)
        temp_cost = 0
        for x in range(total_cities-1):
            temp = graph.adjList[curr]
            temp = temp - set(temp_sol)
            next = random.choice(tuple(temp))
            temp_cost = temp_cost + Weights[curr][next]
            temp_sol.append(next)
            curr=next
        Particles.append(Particle(temp_sol, temp_cost))
        current_total_particles+=1
        # print(Particles[len(Particles)-1].solution, Particles[len(Particles)-1].isValidSolution(graph))
    except IndexError:
        # print("Bad choice iterating again")
        continue

print("###### Generated {} random particles or path. #######".format(tot_particles))

gbest = min(Particles, key=attrgetter('cost_current_solution'))
print("gbest initially - ", gbest.cost_current_solution, gbest.solution)
objective_fun = [gbest.cost_current_solution]

Gbest_list = []
Gbest_list.append(gbest)

# The main iteration loop
for iter in range(1,iterations+1):
    for particle in Particles:
        solution_gbest = gbest.solution[:]
        solution_pbest = particle.pbest[:]
        solution_particle = particle.solution[:]
        tmp_velocity = []

        # Computing basic sequence pbest(t)i - x(t)i
        for i in range(total_cities):
            if(solution_pbest[i]!=solution_particle[i]):
                # generate swap operator
                swap_operator = (i, solution_particle.index(solution_pbest[i]), alfa)

                tmp_velocity.append(swap_operator)

                #Perform the swap
                foo = solution_particle[swap_operator[0]]
                solution_particle[swap_operator[0]]=solution_particle[swap_operator[1]]
                solution_particle[swap_operator[1]]=foo
        
        #Basic swap sequence for gbest(t)i - x(t)i
        solution_particle = particle.solution[:]
        for i in range(total_cities):
            if(solution_gbest[i]!=solution_particle[i]):
                #generate swap operator
                swap_operator = (i, solution_particle.index(solution_gbest[i]), beta)

                tmp_velocity.append(swap_operator)

                #Perform the swap
                foo = solution_particle[swap_operator[0]]
                solution_particle[swap_operator[0]]=solution_particle[swap_operator[1]]
                solution_particle[swap_operator[1]]=foo
        
        particle.velocity = tmp_velocity
        solution_particle = particle.solution[:]
        #Updating the particle accoriding to xi(t+1) = xi(t)+vi(t+1)
        for swap_operator in tmp_velocity:
            #swaps only when the path after swap is valid path
            if (random.random() <= swap_operator[2] and (solution_particle[swap_operator[0]] in graph.adjList[solution_particle[swap_operator[1]]])):
                #makes the temporary swap.
                tmp_solution = solution_particle[:]
                foo = tmp_solution[swap_operator[0]]
                tmp_solution[swap_operator[0]] = tmp_solution[swap_operator[1]]
                tmp_solution[swap_operator[1]]=foo
                #check if the proposed swap produces a valid path
                if (isValidSolu(tmp_solution, graph)):
                    foo = solution_particle[swap_operator[0]]
                    solution_particle[swap_operator[0]] = solution_particle[swap_operator[1]]
                    solution_particle[swap_operator[1]]=foo
        
        particle.solution = solution_particle[:]
        particle.updateCurrentCost(Weights)
        particle.update_pbest()

        # update gbest if
        if(particle.cost_pbest_solution <= gbest.cost_current_solution):
            gbest.cost_current_solution = particle.cost_pbest_solution
            gbest.solution = particle.solution[:]
        
    Gbest_list.append(copy.copy(gbest))

    # print(Particles[1].cost_pbest_solution)
    objective_fun.append(gbest.cost_current_solution)

# Ploting the cost function with iteration
plt.show()
fig, ax = plt.subplots()
iterasons = [i for i in range(0,iterations+1)]
filenames = []
for i in range(0,iterations+1):
    ax.cla()
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Cost function")
    ax.plot(iterasons[:i], objective_fun[:i], color='r')
    ax.set_title("Iteration {}".format(i))


    filename=f'{i}.png'
    filenames.append(filename)

    # save frame
    plt.savefig(filename)
    # plt.close()
    plt.pause(0.001)

# build gif
with imageio.get_writer('Q1a-cost.gif', mode='I') as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)

# Remove files
for filename in set(filenames):
    os.remove(filename)

plt.close()

cities_status[1][:] =  ['grey', 'green', 'green', 'red', 'yellow', 'yellow', 'grey', 'green', 'green']

''' Visulizing the path with iteration ''' 
#Assigning random city coordinates. To represent cities as vertices of graph.
cities_coordinates = [[1,63,40,55,19,69,10,36,77],[1,1,6,69,35,19,80,46,53]]
fig, ax = plt.subplots()
ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

iter=0
filenames = []
for g in Gbest_list:
    # print(g.solution)
    plt.cla()
    for i in range(total_cities):
        ax.scatter(cities_coordinates[0][i], cities_coordinates[1][i], c=cities_status[1][i], s=100)
        ax.annotate(cities_status[0][i], (cities_coordinates[0][i]+2, cities_coordinates[1][i]+2))
    plt.title("Iteration {}".format(iter))
    iter+=1
    for j in range(1,len(g.solution)):
        # indices to be joined in cities_coordinates
        ii=g.solution[j-1]
        kk=g.solution[j]
        Line = [[cities_coordinates[0][ii], cities_coordinates[0][kk]], 
                [cities_coordinates[1][ii], cities_coordinates[1][kk]]]
        if(j==1):
            plt.annotate("Start",(cities_coordinates[0][ii]-4, cities_coordinates[1][ii]-4), fontweight="bold")
        if(j==len(g.solution)-1):
            plt.annotate("End", (cities_coordinates[0][kk]-4, cities_coordinates[1][kk]-4), fontweight="bold")
        plt.plot(Line[0],Line[1],color='blue')

    filename=f'{iter-1}.png'
    filenames.append(filename)

    # save frame
    plt.savefig(filename)
    plt.pause(0.001)
    if(iter==iterations+1):
        plt.show()

# build gif
with imageio.get_writer('Q1a-Path.gif', mode='I') as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)

# Remove files
for filename in set(filenames):
    os.remove(filename)

plt.close()
print("After {}-th iteration the best path found out has cost {}.".format(iterations, gbest.cost_current_solution), "The path is ", gbest.solution)