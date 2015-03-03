"""  This will test the json_table module by reading in
    every file in Test_Examples folder, and then writing them
    out as json and csv file in the Test_Examples/Answer folder
"""
__author__ = 'Ben Christenson'
__date__ = '2015-03-01'

import pytest
import glob
import os
import sys
from json_table import JsonTable
import shutil

switch = {'.csv': '.json', '.json': '.csv'}

file_filter = len(sys.argv) < 2 and '*.*' or sys.argv[1].split('test_examples/')[-1]
test_path = shutil.abspath(os.path.split(__file__)[0]) + '/test_examples/' + file_filter
examples = glob.glob(test_path)
assert examples


@pytest.mark.parametrize("filename", examples)
def test_convert_example_file(filename):
    path, name = os.path.split(filename)
    name, ext = os.path.splitext(name)
    new_file = path + '/answer/' + name + switch[ext]
    new_file2 = path + '/answer/' + name + ext
    new_file_trans = path + '/answer/' + name+'_trans' + switch[ext]

    transpose = False
    table = JsonTable()
    if (filename.endswith('csv')):
        table.load_csv_file(filename,transpose=transpose)
        table.save_json_file(new_file)
    else:
        table.load_json_file(filename)
        table.save_csv_file(new_file,transpose=transpose)
        table.save_csv_file(new_file_trans,space_column=False,transpose=True)

    table2 = JsonTable()
    if (filename.endswith('csv')):
        table2.load_json_file(new_file)
        table2.save_csv_file(new_file2,transpose=transpose)
    else:
        table2.load_csv_file(new_file,transpose=transpose)
        table2.save_json_file(new_file2)

    with open(filename, 'r') as original:
        with open(new_file2, 'r') as test:
            original_text = original.read()
            test_text = test.read()
            print original_text
            print test_text
            assert (original_text == test_text)


if __name__ == '__main__':
    print sys.argv
    sys.exit(pytest.main(['json_table_test.py'] + sys.argv[3:]))
    # test_convert_example_file(examples[0])
