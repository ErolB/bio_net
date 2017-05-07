from network_simulation import *
from sklearn.svm import SVC

conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
cursor = conn.cursor()
node_set = ['hsa:4088', 'hsa:5933', 'hsa:5001', 'hsa:4087', 'hsa:4173', 'hsa:1028', 'hsa:9232', 'hsa:4616', 'hsa:990', 'hsa:10459']

if __name__ == '__main__':
    data_set = []
    categories = []
    graph = build_network('networks/cell_cycle.txt')
    for num in range(5):
        # apply mutations from control sample
        control = load_mutations(num, cursor, 'control')
        graph.knockout(control)
        data = [item for item in graph.simulate(node_set).values()]
        data_set.append(data)
        categories.append(0)
        graph.restore()
        # apply mutations from diseased sample
        cancer = load_mutations(num, cursor, 'mutations')
        graph.knockout(cancer)
        data = [item for item in graph.simulate(node_set).values()]
        data_set.append(data)
        categories.append(1)
        graph.restore()
    svm = SVC()
    svm.fit(data_set, categories)
    test_mutations = load_mutations(5, cursor, 'mutations')
    graph.knockout(test_mutations)
    data = [item for item in graph.simulate(node_set).values()]
    print(svm.predict(data))

