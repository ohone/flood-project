import shapely
import fiona
import math
import decimal
import glob
import csv

file_list0 = glob.glob('./directory0/*.txt')
file_list1 = glob.glob('./directory1/*.txt')

count = 0
for i in file_list0:
    with open(i) as fin, open("csvdir1/outfile{}".format(count) + '.csv', 'w') as fout:
        o=csv.writer(fout)
        for line in fin:
            o.writerow(line.split())

    count = count + 1
count = 0
for i in file_list1:
    with open(i) as fin, open("csvdir2/outfile{}".format(count)+ '.csv', 'w') as fout:
        o=csv.writer(fout)
        for line in fin:
            o.writerow(line.split())
    count = count + 1
