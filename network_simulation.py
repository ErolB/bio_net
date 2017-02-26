ITERATION_COUNT = 100000

import random
import pymysql

class Graph(object):
    def __init__(self, node_names):
        self.connections = {}  # dictionary of dictionaries
        self.nodes = {}
        for name in node_names:
            self.connections[name] = {}  # create a dictionary of connections for each node
            self.nodes[name] = False  # indicates whether a node has been reached
    # adds an edge to the graph
    def add_connection(self, source_names, target_names, probability):
        for source in source_names:
            for target in target_names:
                self.connections[source][target] = probability
    # perform a Monte Carlo simulation
    def simulate(self, source_names):
        visits = {}
        for node in self.nodes:
            visits[node] = 0.0
        # run simulations
        for num in range(ITERATION_COUNT):
            visited = set(source_names)  # tracks visited nodes, prevents cycles
            front = source_names
            while front:
                new_front = []
                for source in source_names:
                    for target in self.connections[source]:
                        if target in visited:
                            continue  # skip if already visited
                        if random.random() < self.connections[source][target]:
                            new_front.append(target)
                            visited.add(target)
                front = new_front
            for node in visited:
                visits[node] += 1
        # return data
        for node in visits:
            visits[node] /= ITERATION_COUNT
        return visits
    # remove all outgoing edges from a set of genes
    def knockout(self, gene_list):
        for gene in gene_list:
            self.connections[gene] = {}

def build_network(file_name):
    net_file = open(file_name)
    raw_text = net_file.readlines()
    # identify all nodes in the network
    node_names = set()
    for line in raw_text:
        for entry in line.split()[0:2]:
            nodes = set(entry.split('|'))
            node_names = node_names.union(nodes)
    graph = Graph(node_names)
    # identify connections
    for line in raw_text:
        entries = line.split()
        source_names = entries[0].split('|')
        target_names = entries[1].split('|')
        probability = float(entries[2])
        graph.add_connection(source_names, target_names, probability)
    return graph

def load_mutations(sample_id, db_cursor):
    db_cursor.execute('SELECT gene FROM mutations WHERE sample_id = {}'.format(str(sample_id)))
    affected_genes = [item[0] for item in db_cursor.fetchall()]
    # load reference table from database
    db_cursor.execute('SELECT * from kegg_conversion')
    conversion = []

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
    cursor = conn.cursor()
    graph = build_network('networks/cell_cycle.txt')
    load_mutations(0, cursor)

    '''
    for node in graph.nodes:
        data = graph.simulate([node])
        print(node)
        print(data)'''