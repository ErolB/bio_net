# builds table mapping gene names to KEGG IDs

import requests
import pymysql
import re

# connect to database
conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
db_interface = conn.cursor()

# get list of genes in database
db_interface.execute('SELECT kegg_id from kegg_conversion;')
stored_genes = [item[0] for item in db_interface.fetchall()]

# load genes from KEGG
print('loading from KEGG...')
page = requests.get('http://rest.kegg.jp/list/hsa/')
genes = {}
for line in page.text.split('\n'):
    print(line)
    try:
        gene_id = line.split()[0]
        equivalents = re.search('RefSeq.*;', line).group()[8:-2]
        for item in equivalents.split(','):
            if len(item) > 50:
                continue
            genes[item.strip()] = gene_id
    except:
        pass

# find genes that are not in the database
unlisted_genes = [item for item in genes if item not in stored_genes]
print(len(unlisted_genes))

# add genes to database
for gene in unlisted_genes:
    db_interface.execute('INSERT INTO kegg_conversion(name, kegg_id) VALUES ("{}","{}");'.format(gene,genes[gene]))

conn.commit()
conn.close()

