# builds table containing locations for each gene

import pymysql
import csv

db_conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
db_interface = db_conn.cursor()

db_interface.execute('DROP TABLE IF EXISTS gene_reference')
db_interface.execute('CREATE TABLE gene_reference(name VARCHAR(50), chromosome VARCHAR(0), start INT, end INT);')

with open('genes.csv', 'r') as gene_file:
    gene_reader = csv.DictReader(gene_file)
    for gene_data in gene_reader:
        # ignore "patch" contigs
        if len(gene_data['Chromosome/scaffold name']) > 2:
            continue
        # extract data
        gene_name = gene_data['Associated Gene Name']
        chromosome = gene_data['Chromosome/scaffold name']
        start = int(gene_data['Gene Start (bp)'])
        end = int(gene_data['Gene End (bp)'])
        # insert data into database
        db_interface.execute('INSERT INTO gene_reference(name, chromosome, start, end) VALUES ("{}", "{}", {}, {});'.format(gene_name, chromosome, start, end))

db_conn.commit()