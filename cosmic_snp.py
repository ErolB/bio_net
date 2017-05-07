# parses SNP data from COSMIC and organizes it into a table in MySQL

cancer_type = ''
min_genes = 3000

import time
import os
import csv
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS mutations(sample_id INT, gene VARCHAR(20));')
os.chdir('./cancer')
files = os.listdir('.')
cursor.execute('SELECT DISTINCT sample_id FROM mutations;')
included_samples = [int(entry[0]) for entry in cursor.fetchall()]
sample_id = len(included_samples)
for file_name in files:
    # check if sample is already included
    if (sample_id in included_samples):
        continue
    # open file and read
    print('processing ' + file_name)
    with open(file_name) as current_file:
        cin = csv.DictReader(current_file)
        data = [row for row in cin if ('silent' not in row['Type'])]  # non-silent mutations
        genes = set()
        for item in data:
            gene_name = item['Gene']
            if '_' in gene_name:
                gene_name = gene_name.split('_')[0]
            genes.add(gene_name)
        for item in genes:
            cursor.execute('INSERT INTO mutations(sample_id, gene) VALUES ("' + str(sample_id) + '","' + item + '")')
    cursor.execute('INSERT INTO mutation_files(sample_id,file_name) VALUES ({},"{}")'.format(sample_id,file_name))
    conn.commit()
    sample_id += 1