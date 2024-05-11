#python crawling/crawling_by_file.py --id [id] --pw [pw] --i [강의명 목록 저장된 파일 이름] --out [내보낼 파일 이름]
# -*- coding: utf-8 -*-

import argparse
import os
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--pw', required=True)

parser.add_argument('--i', required=True)
parser.add_argument('--out', required=True)

data_path = 'crawling/data/'
id = parser.parse_args().id
pw = parser.parse_args().pw
in_file = data_path + parser.parse_args().i +'.csv'
out_file = parser.parse_args().out

with open(in_file,'r') as f:
    csv_reader = csv.reader(f)
    subjects = dict()
    for row in csv_reader:
        subjects[row[0]] = row[1]


for subject in subjects.keys():
    if subject.startswith('\ufeff'): subject = subject[1:]
    os.system('python crawling/crawling_module.py --id {} --pw {} --subject \'{}\' --out {}'.format(id,pw,subject,out_file))