cancer_type = ''
min_genes = 3000

import selenium.webdriver as driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import csv
import pymysql

def retireve():
    browser = driver.Chrome('./chromedriver')
    wait = WebDriverWait(browser, 10)
    credentials_file = open('cosmic_credentials')

    #log into database
    credentials = credentials_file.readlines()
    browser.get('https://cancer.sanger.ac.uk/cosmic/login')
    email_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="email"]')))
    pwd_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="pass"]')))
    email_field.send_keys('eroljb@ufl.edu')
    pwd_field.send_keys(credentials[1])
    time.sleep(0.25)
    browser.find_element_by_xpath('//input[@type="submit"]').click()

    # retrieve data
    browser.get('http://cancer.sanger.ac.uk/wgs/search?q=' + cancer_type + '#samp')
    while True:  # relies on break statement
        rows = wait.until(EC.presence_of_element_located('//tr[@role="row"]'))
    # unfinished...

def update():
    conn = pymysql.connect(host='localhost', user='root', password='admin', db='bio')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS mutations')
    cursor.execute('CREATE TABLE mutations(sample_id INT, gene VARCHAR(20))')
    os.chdir('./snp')
    files = os.listdir('.')
    counter = 0  # used as an arbitrary ID number
    for file_name in files:
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
                cursor.execute('INSERT INTO mutations(sample_id, gene) VALUES ("' + str(counter) + '","' + item + '")')
        counter += 1
    conn.commit()

if __name__ == '__main__':
    update()