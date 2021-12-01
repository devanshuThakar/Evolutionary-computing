import math
import random
import numpy as np
import matplotlib.pyplot as plt

class NSGA2:
    def __init__(self,max_gen, total_particles, crossover_probability, alpha, mutation_probability):
        self.max_gen=max_gen
        self.total_particles = total_particles
        self.pareto_fronts = []         # List to store f1 and f2 of all pareto-fronts over all generations
        self.rh_pareto_fronts=[]        # List to store r and h of all pareto-fronts over all generations
        self.Particles = None
        self.crossover_probability = crossover_probability
        self.alpha = alpha
        self.mutation_probability = mutation_probability

    def fast_non_domination_sorting(self):
        N=len(self.Particles)
        S=[[] for i in range(0,N)]  # S[i] contains the list of particles dominated by i-th individual
        front = [[]]  # f[i] contains the list of individuals in i-th front
        n=[0 for i in range(0,N)]      # n[i] contains the number of individuals which dominates the i-th individual
        rank=[0 for i in range(0,N)]   # rank[i] contains the rank of i-th individual

        for p in range(0,N):
            S[p]=[]
            n[p]=0
            for q in range(0,N):
                # check whether p dominates q or not
                # Minimize f1 ; Maximimze f2
                if(self.Particles[p].f1 <self.Particles[q].f1 and self.Particles[p].f2 > self.Particles[q].f2):
                    if q not in S[p]:
                        S[p].append(q)
                # Check whether q dominates p or not
                elif(self.Particles[q].f1<self.Particles[p].f1 and self.Particles[q].f2>self.Particles[p].f2):
                    # We found some q that dominates p
                    n[p]+=1
            
            if(n[p]==0):
                rank[p]=0
                if p not in front[0]:
                    front[0].append(p)

        i = 0
        while(front[i] != []):
            Q=[]
            for p in front[i]:
                for q in S[p]:
                    n[q]=n[q]-1
                    if(n[q] == 0):
                        rank[q]=i+1
                        if q not in Q:
                            Q.append(q)
            i = i+1
            front.append(Q)

        del front[len(front)-1]
        return front
    
    def crowding_distance(self, front):
        f1_list=[]
        f2_list=[]
        for p in front:
            f1_list.append(self.Particles[p].f1)
            f2_list.append(self.Particles[p].f2)

        sortedf1 = [x for (x,y) in sorted(zip(front, f1_list), key=lambda pair : pair[1], reverse=True) ]
        sortedf2 = [x for (x,y) in sorted(zip(front, f2_list), key= lambda pair : pair[1])]

        # Setting the crowding-distance of extreme particles to infinity
        self.Particles[sortedf1[0]].CD=self.Particles[sortedf2[0]].CD=math.inf
        self.Particles[sortedf1[len(front)-1]].CD=self.Particles[sortedf2[len(front)-1]].CD=math.inf
        
        for i in range(2, len(front)-1):
            # Since f1 has to be minimize. The denominator is min(f1)-max(f1)
            self.Particles[sortedf1[i]].CD = self.Particles[sortedf1[i]].CD + (self.Particles[sortedf1[i+1]].f1-self.Particles[sortedf1[i-1]].f1)/(min(f1_list)-max(f1_list))
        for i in range(2, len(front)-1):
            self.Particles[sortedf2[i]].CD = self.Particles[sortedf2[i]].CD + (self.Particles[sortedf2[i+1]].f2-self.Particles[sortedf2[i-1]].f2)/(max(f2_list)-min(f2_list))

    def crossover(self):
        # Particles = list(np.random.permutation(Particles))
        offsprings = []
        ''' Using a blend cross-over ''' 
        for i in range(0,int(self.crossover_probability*len(self.Particles)),2):
            # beta = random.random()
            x1=self.Particles[i].r
            x2=self.Particles[i+1].r
            if(x1>x2):
                x1=self.Particles[i+1].r
                x2=self.Particles[i].r
            left_r = x1 - self.alpha*(x2 - x1)
            left_r = left_r if left_r>=2 else 2
            right_r = x2 + self.alpha*(x2 - x1)
            right_r = right_r if right_r<=10 else 10

            x1=self.Particles[i].h
            x2=self.Particles[i+1].h
            if(x1>x2):
                x1=self.Particles[i+1].h
                x2=self.Particles[i].h
            left_h = x1 - self.alpha*(x2 - x1)
            left_h = left_h if left_h>=5 else 5
            right_h = x2 + self.alpha*(x2 - x1)
            right_h = right_h if right_h<=15 else 15

            r1 = left_r + (right_r-left_r)*random.random()
            r2 = left_r + (right_r-left_r)*random.random()
            h1 = left_h + (right_h-left_h)*random.random()
            h2 = left_h + (right_h-left_h)*random.random()
            
            offsprings.append(individual(r1,h1))
            offsprings.append(individual(r2,h2))
        
        #Shuffle the offsprings list
        offsprings = list(np.random.permutation(offsprings))
        # Perform mutation on offsprings
        ''' Using a random mutation - produce a random solution within the range '''
        for i in range(0,int(len(offsprings))):
            if (random.random() < self.mutation_probability):
                offsprings[i].r = 2 + (10-2)*random.random()
                offsprings[i].h = 5 + (15-5)*random.random()

        for offspring in offsprings:
            offspring.evaluate_fitness()
        return offsprings

    def run(self):
        # Generate random particles
        self.Particles = [individual(2+ (10-2)*random.random(), 5+(15-5)*random.random()) for i in range(self.total_particles)] 
        #Evaluating initial fitness
        for p in self.Particles:
            p.evaluate_fitness()

        # Finding the initial pareto front
        front = self.fast_non_domination_sorting()

        f1_temp = [] 
        f2_temp = []
        rh_pareto_front_temp = []   
        for p in front[0]:
            f1_temp.append(self.Particles[p].f1)
            f2_temp.append(self.Particles[p].f2)
            rh_pareto_front_temp.append((self.Particles[p].r, self.Particles[p].h))
        print('Len of current pareto-front ', len(front[0]))
        self.pareto_fronts.append([f1_temp,f2_temp])
        self.rh_pareto_fronts.append(rh_pareto_front_temp)

        #Generation loop starts 
        for g in range(self.max_gen):
            #Perform cross-over and generate offsprings
            Q = self.crossover()
            self.Particles += Q   # Merging parent pop and offspirng pop
            
            # Doing non-domination sorting on combined pop
            fronts = self.fast_non_domination_sorting()
            sorted_individuals = []
            for i in range(len(fronts)):
                self.crowding_distance(fronts[i])
                front_withdist = zip(fronts[i], [self.Particles[j].CD for j in fronts[i]])  
                # front_withdist containd the particles in front along with their crowding distance
                front_withdist = sorted(front_withdist, key= lambda p : p[1], reverse=True)  # sorting front_withdist based on crowding distance
                fronts[i] = [f[0] for f in front_withdist]
                sorted_individuals += fronts[i]

            self.Particles = [self.Particles[j] for j in sorted_individuals]

            # Storing the f1,f2 value and r,h of the pareto front in current generation.
            f1_temp = [] 
            f2_temp = []
            rh_pareto_front_temp = []
            for i in range(len(fronts[0])):
                p=fronts[0][i]
                if(i>=self.total_particles):
                    break
                f1_temp.append(self.Particles[p].f1)
                f2_temp.append(self.Particles[p].f2)
                rh_pareto_front_temp.append((self.Particles[p].r, self.Particles[p].h))
            print('Len of current pareto-front ', len(f1_temp))
            self.rh_pareto_fronts.append(rh_pareto_front_temp)
            self.pareto_fronts.append([f1_temp,f2_temp])

            self.Particles = self.Particles[:self.total_particles]
              
class individual:
    '''
    individual class can be instantiated by individual(r,h)
    Use evaluate_fitness to evalute fitness
    '''
    def __init__(self, r,h):
        self.solution=(r,h)
        self.CD=0
        self.r=r
        self.h=h
        self.f1=0
        self.f2=0

    def func1(self):
        ## Surface Area
        self.f1 = (2*math.pi*self.r**2) + (2*math.pi*self.r*self.h) + (math.pi*self.r*math.sqrt(self.r**2 + (self.h/3)**2))
    
    def func2(self):
        ## Volume
        self.f2 = (2*math.pi*(self.r**3)/3)+(math.pi*(self.r**2)*self.h)+(math.pi*(self.r**2) * self.h/(3*3))

    def evaluate_fitness(self):
        self.func1()
        self.func2()

'''  Note - Range of 2<=r<=10 and 5<=h<=15 is hard-code in class NSGA-II '''
Problem = NSGA2(max_gen=5,total_particles=500, crossover_probability=1, alpha=0.5, mutation_probability=0.1)
Problem.run()
last_front=Problem.pareto_fronts[len(Problem.pareto_fronts)-1]
last_rh = Problem.rh_pareto_fronts[len(Problem.pareto_fronts)-1]

plt.show()
fig, ax = plt.subplots()
for i in range(len(Problem.pareto_fronts)):    
    ax.cla()
    ax.set_xlabel('f1 (Area)')
    ax.set_ylabel('f2 (volume)')
    ax.scatter(Problem.pareto_fronts[i][0], Problem.pareto_fronts[i][1], color='b', s=5)
    ax.set_title("Iteration {}".format(i))
    plt.pause(1)


ind = last_front[0].index(min(last_front[0]))
print("index of min(f1) : " , ind)
print(" Min f1(area) - ", last_front[0][ind], " for r=", last_rh[ind][0], " and h=", last_rh[ind][1], '\n')

ind = last_front[1].index(min(last_front[1]))
print("index of min(f2) : " , ind)
print(" Min f2(Volume) - ", last_front[1][ind], " for r=", last_rh[ind][0], " and h=", last_rh[ind][1], '\n')

ind = last_front[0].index(max(last_front[0]))
print("index of max(f1) : " , ind)
print(" Max f1(area) - ", last_front[0][ind], " for r=", last_rh[ind][0], " and h=", last_rh[ind][1], '\n')

ind = last_front[1].index(max(last_front[1]))
print("index of max(f2) : " , ind)
print(" Max f2(Volume) - ", last_front[1][ind], " for r=", last_rh[ind][0], " and h=", last_rh[ind][1], '\n')