# parses VCF files containing SNP data from healthy controls

import re
import pymysql
import os
import time

# connect to database and set up table
conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
db_interface = conn.cursor()
db_interface.execute('CREATE TABLE IF NOT EXISTS control(sample_id INT, gene VARCHAR(50));')

# load gene table and create data structure
class GeneDictionary(object):
    def __init__(self, cursor):
        cursor.execute('SELECT name, chromosome, start, end FROM gene_reference')
        raw_data = cursor.fetchall()
        chromosomes = [str(num) for num in range(1,23)] + ['X', 'Y', 'MT']
        self.chromosomes = {item: [] for item in chromosomes}
        for item in raw_data:
            self.chromosomes[item[1]].append((item[0], item[2], item[3]))
        for item in chromosomes:
            self.chromosomes[item] = sorted(self.chromosomes[item], key = lambda x: x[1])  # sort by start positions
    def lookup(self, chromosome, position):
        pool = self.chromosomes[chromosome]
        while len(pool) > 15:
            if pool[int(len(pool)/2)][1] > position:
                pool = pool[:int(len(pool)/2)]
            else:
                pool = pool[int(len(pool)/2):]
        results = []
        for item in pool:
            if (position >= item[1]) and (position <= item[2]):
                results.append(item[0])
        return results

reference = GeneDictionary(db_interface)
print('done')

# retrieve data from files and add to table
files = os.listdir('./control')
print(files)
os.chdir('./control')
db_interface.execute('SELECT file_name FROM control_files;')
current_entries = [item[0] for item in db_interface.fetchall()]
sample_id = len(current_entries)
for file_name in files:
    if file_name in current_entries:
        print('{} already present'.format(file_name))
        continue
    file = open(file_name, 'r')
    previous = None  # for display purposes
    included_genes = []
    print('starting')
    to_insert = []
    for item in file.readlines():
        if item[0] == '#':
            continue  # exclude info lines
        fields = item.split()
        if ('PASS' not in fields[6]):
            continue
        try:
            chromosome = re.findall('\d{1,2}|MT|X|Y',fields[0])[0]
        except IndexError:
            print('error in chromosome field')
            continue
        if chromosome != previous:
            previous = chromosome
            print(chromosome)
        position = int(fields[1])
        gene_names = reference.lookup(chromosome, position)
        for name in gene_names:
            if name not in included_genes:
                #print('adding ' + name)
                to_insert.append((sample_id,name))
            included_genes.append(name)
    command = 'INSERT INTO control (sample_id,gene) VALUES '
    for item in to_insert:
        command += '({},"{}"),'.format(item[0],item[1])
    command = command[:-1]
    command += ';'
    db_interface.execute(command)
    db_interface.execute('INSERT INTO control_files (sample_id, file_name) VALUES ({}, "{}");'.format(sample_id, file_name))
    conn.commit()
    sample_id += 1
