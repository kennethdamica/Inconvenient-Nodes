#Using Djikstra's Algorithm to find inconvenient squares in a graph
#KJD Sept 2012

import pygame, sys, random, time
from copy import deepcopy
from pygame.locals import *

#COLORS
GRAY = (100,100,100)
RED = (200,20,20)
ORANGE = (255,128,0)
GREEN = (34,139,34)
WHITE = (255,255,255)
BROWN = (139,69,19)

#This is the dist assigned to mountainous regions
#At 20, we are willing to walk up to 20 regular squares to avoid one mountain
LARGE = 5

fpsClock = pygame.time.Clock()

def main():
    pygame.init()
    
    N = 15
    SCALE = 20
    DISPLAYSURF = pygame.display.set_mode((N*SCALE,N*SCALE))
    pygame.display.set_caption("Inconvenience")

    currentMap = generateMap(N)

    graph = convertMaptoGraph(currentMap)
    
    inconv_vertexes = Inconvenience(graph, (0,0), (N-1,N-1), 3)
    road, dist = dijkstra((0,0),graph)
    paths = get_Paths((N-1,N-1),road)
    
    while True:
        dt = fpsClock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        drawMap(currentMap,SCALE,DISPLAYSURF)
        draw_all_paths(paths,SCALE,DISPLAYSURF)
        draw_inconvenient_vertexes(inconv_vertexes, SCALE,DISPLAYSURF)
        pygame.display.update()
        

def Inconvenience(original_graph, start, end, num_Inconvenient):
    inconvenient_vertexes = []
    graph = deepcopy(original_graph)
    full_road, full_dist = dijkstra(start,graph)
    all_paths = get_Paths(end, full_road)
    path_vertexes = set([])
    for p in all_paths:
        path_vertexes = path_vertexes.union(set(p))
    graph['star'] = set([])
    for v in path_vertexes:
        graph['star'] = graph['star'].union(graph[v])
        del graph[v]
    for v, edges in yield_dict(graph):
        if v != 'star':
            edges_list = list(edges)
            for i, e, d in yield_edges_enum(edges_list):
                if e not in graph:
                    edges_list.remove((e,d))
                    edges_list.append(('star',d))
            graph[v] = set(edges_list) 
    while len(inconvenient_vertexes) < num_Inconvenient:
        reduced_road, reduced_dist = dijkstra(('star'),graph)
        new_max = 0
        for v, d in yield_dict(reduced_dist):
            if d > new_max:
                new_max = d
                high = v
        inconvenient_vertexes.append(high)
        for t in graph['star']:
            if t[0] == high:
                graph['star'].remove(t)
                break
        graph['star'].add((high,1))
    return inconvenient_vertexes  
        
#randomly generates the map
def generateMap(n):
    mymap = [None]*n
    for row in range(n):
        mymap[row] = [None]*n
        for col in range(n):
            rand = random.randrange(10)
            if rand < 3:
                mymap[row][col] = LARGE
            else:
                mymap[row][col] = 1
    return mymap

def walk_array(my_map):
    for i in range(len(my_map)):
        for j, value in enumerate(my_map[i]):
            yield i, j, value

def yield_dict(my_dict):
	for i in my_dict:
		yield i, my_dict[i]
		
def yield_edges(array):
	for a in array:
		yield a[0], a[1]

def yield_edges_enum(array):
    for i, a in enumerate(array):
        yield i, a[0], a[1]

#draws the map w mountains
def drawMap(board,scale,surf):
    for row in range(len(board)):
        locV = row*scale
        for col in range(len(board[row])):
            locH = col*scale
            if board[row][col] == LARGE:
                pygame.draw.rect(surf, GREEN, (locH,locV,scale,scale))
                pygame.draw.polygon(surf, BROWN, ((locH,locV+scale),(locH+scale,locV+scale), (locH+scale/2,locV)))
                pygame.draw.polygon(surf, WHITE, ((locH+((3.0/8)*scale),locV+(0.25*scale)),(locH+((5.0/8)*scale),locV+(0.25*scale)), (locH+scale/2.0,locV)))
            else:
                pygame.draw.rect(surf, GREEN, (locH,locV,scale,scale))

def dijkstra(start,graph):
    inf = float('inf')
    numV = len(graph)
    dist = {}
    pred = {}
    queue = []
    for v in graph:
        dist[v] = inf
        pred[v] = []
        queue.append(v)
    
    dist[start] = 0
    
    while queue:
        new_min = inf
        #find minimum distance in queue
        for e in queue:
            if dist[e] < new_min:
                new_min = dist[e]
                new = e
        #remove min from queue
        queue.remove(new)
        
        #relax neighbors
        for v, d in yield_edges(graph[new]):
            if v in queue and d + dist[new] < dist[v]:
                dist[v] = d + dist[new]
                pred[v] = [new]
            elif (v in queue) and (d + dist[new] == dist[v]):
                pred[v].append(new)
    return pred, dist

#returns all shortest paths 
def get_Paths(end, road):
    complete_paths = []
    paths = []
    paths.append([end])
    while True:
        p = paths.pop()
        last = last_elem(p)
        if not road[last]:
            complete_paths.append(p)
        else:
            for antecedent in road[last]:
                newp = [v for v in p]
                newp.append(antecedent)
                paths.append(newp)
        if not paths:
            break
    return complete_paths
	
def last_elem(a):
	return a[len(a)-1]

#draws a line between each member of the path
def draw_all_paths(paths,scale,surf):
	for path in paths:
		pygame.draw.lines(surf, ORANGE, False,
                [tuple(scale*i+scale/2 for i in v)[::-1] for v in path], 3)

def draw_inconvenient_vertexes(verts, scale, surf):
    for v in verts:
        pygame.draw.circle(surf, RED, tuple(i*scale+scale/2 for i in v)[::-1],
                           scale/4)

def convertMaptoGraph(m):
    graph = {}
    for row, col, val in walk_array(m):
        tup = (row, col)
        graph[tup] = set([])
        if row > 0:
            graph[tup].add(((row-1, col), m[row-1][col]))
        if row < len(m)-1:
            graph[tup].add(((row+1, col), m[row+1][col]))
        if col > 0:
            graph[tup].add(((row, col-1), m[row][col-1]))
        if col < len(m[row])-1:
            graph[tup].add(((row, col+1), m[row][col+1]))
    return graph 

if __name__ == '__main__':
    main()


