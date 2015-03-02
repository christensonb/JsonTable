"""  This will test the json_table module by reading in
    every file in Test_Examples folder, and then writing them
    out as json and csv file in the Test_Examples/Answer folder
"""
__author__ = 'Ben Christenson'
__date__ = '2015-03-01'

from collections import OrderedDict
import pytest
import glob
import os
from json_table import JsonTable

switch={'.csv':'.json','.json':'.csv'}

examples = glob.glob(os.path.join(os.getcwd()+'test_examples/*.*'))

def test_simplest_dict():
    convert_example_file(os.getcwd()+'/test_examples/simplest_dict.json')

#@pytest.mark.parametrize(*(('filename'),examples))

def convert_example_file(filename):
    path,name = os.path.split(filename)
    name,ext = os.path.splitext(name)
    new_file = path+'/answer/'+name+switch[ext]
    new_file2 = path+'/answer/'+name+ext

    table = JsonTable()
    if(filename.endswith('csv')):
        table.load_csv_file(filename)
        table.save_json_file(new_file)
    else:
        table.load_json_file(filename)
        table.save_csv_file(new_file)

    table2 = JsonTable()
    if(filename.endswith('csv')):
        table.load_json_file(new_file)
        table.save_csv_file(new_file2)
    else:
        table.load_csv_file(new_file)
        table.save_json_file(new_file2)

    with open(filename,'r') as original:
        with open(new_file2,'r') as test:
            test = test.read()
            print 'Final Json','\n',test
            assert(original.read() == test)


