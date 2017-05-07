ITERATION_COUNT = 10000

import random
import pymysql

class Graph(object):
    def __init__(self, node_names):
        self.connections = {}  # dictionary of dictionaries
        self.original_connections = {}  # used to restore original settings
        self.nodes = {}
        for name in node_names:
            self.connections[name] = {}  # create a dictionary of connections for each node
            self.nodes[name] = False  # indicates whether a node has been reached
    # adds an edge to the graph
    def add_connection(self, source_names, target_names, probability):
        for source in source_names:
            for target in target_names:
                self.connections[source][target] = probability
    # sets the current state as the original
    def sync(self):
        self.original_connections = self.connections
    # restores original state
    def restore(self):
        self.connections = self.original_connections
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
    graph.sync()  # define the current state as the original state
    return graph

def load_mutations(sample_id, db_cursor, db_name):
    db_cursor.execute('SELECT gene FROM {} WHERE sample_id = {}'.format(db_name, str(sample_id)))
    affected_genes = [item[0] for item in db_cursor.fetchall()]
    # load reference table from database
    db_cursor.execute('SELECT * from kegg_conversion')
    conversion = {item[0]:item[1] for item in db_cursor.fetchall()}
    affected_genes_kegg = {}
    for item in affected_genes:
        try:
            affected_genes_kegg[item] = conversion[item]
        except KeyError:
            pass
    print(affected_genes_kegg)
    return affected_genes_kegg

if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
    cursor = conn.cursor()
    graph = build_network('networks/cell_cycle.txt')
    mutations = load_mutations(0, cursor, 'mutations')
    control = load_mutations(0, cursor, 'control')
    node_set = ['hsa:4088', 'hsa:5933', 'hsa:5001', 'hsa:4087', 'hsa:4173', 'hsa:1028', 'hsa:9232', 'hsa:4616', 'hsa:990', 'hsa:10459']
    print(node_set)
    print(graph.simulate(node_set))
    graph.knockout(control)
    print(graph.simulate(node_set))
    '''
    for node in graph.nodes:
        data = graph.simulate([node])
        print(node)
        print(data)'''