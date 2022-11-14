import pycxsimulator
from pylab import *

import networkx as nx

import csv

def initialize():
    global g
    #g = nx.karate_club_graph()
    g = nx.barabasi_albert_graph(300, 5) 
    # Use seed for reproducibility
    #g = nx.gnm_random_graph(300, 1500, 20160)
    # try diff networks
    #g.pos = nx.spring_layout(g)
    g.pos = nx.circular_layout(g)
    for i in g.nodes:
        g.nodes[i]['state'] = 1 if random() < .5 else 0
    
    print("num edges before", g.number_of_edges())
    
def observe():
    global g
    cla()
    nx.draw(g, cmap = cm.Wistia, vmin = 0, vmax = 1,
            node_color = [g.nodes[i]['state']*1 for i in g.nodes],
            pos = g.pos)

alpha = 0.2 # severance probability
p_i = 1 - alpha # infection probability
# p_r = 0.1 # recovery probability

ticks = 0
infected = []
susceptible = []
is_pairs = []
ss_pairs = []
ii_pairs = []

csv_path = './simulation_data_' + str(alpha) 
header = ['t', 'infected', 'susceptible', '[IS]', '[SS]', '[II]']
# open the file in the write mode
f = open(csv_path, 'w')

# create the csv writer
writer = csv.writer(f)

# write a row to the csv file
writer.writerow(header)

def update():
    global ticks
    global infected
    global susceptible
    global is_pairs
    global ss_pairs
    global ii_pairs
    ticks += 1
    global g

    infected = []
    susceptible = []
    is_pairs = []
    ss_pairs = []
    ii_pairs = []
    for n in g.nodes:
        sus = False
        if g.nodes[n]['state'] == 0:
            sus = True
            susceptible.append(n)
        else:
            infected.append(n)
        for m in g.neighbors(n):
            if g.nodes[m]['state'] == 0:
                if sus:
                    ss_pairs.append(tuple([n,m]))
                else:
                    is_pairs.append(tuple([n,m]))
            else:
                if sus:
                    is_pairs.append(tuple([n,m]))
                else:
                    ii_pairs.append(tuple([n,m]))
    data = [ticks, len(infected), len(susceptible), len(is_pairs)/2, len(ss_pairs)/2, len(ii_pairs)/2]
    writer.writerow(data)
    
    a = choice(list(g.nodes))

    """if g.nodes[a]['state'] == 0: # if susceptible
        if g.degree(a) > 0:
            b = choice(list(g.neighbors(a)))
            if g.nodes[b]['state'] == 1: # if neighbor b is infected
                if random() < p_s:
                    g.remove_edge(a, b)
                else:
                    g.nodes[a]['state'] = 1 if random() < p_i else 0
    else: # if infected
        g.nodes[a]['state'] = 0 if random() < p_r else 1"""
    
    if g.nodes[a]['state'] == 1: # if a infected
        if g.degree(a) > 0:
            b = choice(list(g.neighbors(a)))
            if g.nodes[b]['state'] == 0: # if neighbor b is susceptible
                if random() <= p_i: # a infect b
                    g.nodes[b]['state'] = 1
                else: # a and b sever ties
                    g.remove_edge(a,b)
                    # infected rewire to infected, susceptible rewire to susceptible
                    c = choice(list(g.nodes))
                    if g.nodes[c]['state'] == 0: # if c is susceptible
                        g.add_edge(b,c)
                    else:
                        g.add_edge(a,c)

    elif g.nodes[a]['state'] == 0: # if a is susceptible
        if g.degree(a) > 0:
            b = choice(list(g.neighbors(a)))
            if g.nodes[b]['state'] == 1: # if neighbor b is infected
                if random() <= p_i: # b infect a
                    g.nodes[a]['state'] = 1
                else: # a and b sever ties
                    g.remove_edge(a,b)
                    # infected rewire to infected, susceptible rewire to susceptible
                    c = choice(list(g.nodes))
                    if g.nodes[c]['state'] == 0: # if c is susceptible
                        g.add_edge(a,c)
                    else:
                        g.add_edge(b,c)

    if len(is_pairs) == 0 or len(infected) == 0 or len(susceptible) == 0:
        pycxsimulator.GUI().quitGUI()
    

pycxsimulator.GUI().start(func=[initialize, observe, update])

global g

print("number of components: ", len(list(nx.connected_components(g))))

print("number of infecteds: ", len(infected))
print("number of susceptibles: ", len(susceptible))
print("[II]: ", len(ii_pairs)/2)
print("[SS]: ", len(ss_pairs)/2)
print("[IS]: ", len(is_pairs)/2)
print("steps: ", ticks)
print("num edges after", g.number_of_edges())

# close the file
f.close()