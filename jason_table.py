""" This module will convert a Json to a CSV or a CSV to a Json
    The data (Json or Python) can be embedded dictionaries, lists, or python objects.

    Here is a list of data structures that Json Tables doesn't handle:
        list of list
        lists of difference sizes in the same dictionary
        embedded lists within two different keys

    The embedded object will be created by flattening the path, and repeating values of higher level.
    The magic happens in that you can then specify the mapping of the json path
    to the CSV header, and then the JsonTable will produce the smallest table by removing duplicates.

    Example:

"""

__author__ = "Ben Christenson"
__date__ = '2015-02-27'

import csv
import simplejson

class JsonTable(object):
    def __init__(self,json_data=None,csv_data=None,map=None,path_deliminator='.',csv_deliminator=','):
        self.json_data = json_data or None
        self.csv_data = csv_data or []
        self.json_path = {}
        self.map = map or {}
        self.path_deliminator = path_deliminator
        self.csv_deliminator=csv_deliminator

    def load_json_file(self,filename,path_deliminator=None):
        """
        This will load a ascii text file of json data and load it into a python object
        :param filename: str of the name of the file
        :return: csv_data
        """
        self.path_deliminator = path_deliminator or self.path_deliminator
        with open(filename,'r') as fn:
            self.json_data = simplejson.load(fn.read())
        self.csv_data = self.flatten_json(self.json_data, self.path_deliminator)
        return self.csv_data

    def flatten_json(self,obj,path_deliminator=None):
        """

        :param filename:
        :param path_deliminator:
        :return:
        """
        self.path_deliminator = path_deliminator or self.path_deliminator
        header,data = self._flatten(obj=obj,level=0,current_path='')
        self.csv_data = [header]+data
        return self.csv_data

    def _flatten(self,obj,level,current_path):
        if isinstance(obj,dict):
            return self._flatten_dict(obj,level,current_path)
        if isinstance(obj,list):
            return self._flatten_list(obj,level,current_path)
        if obj.get('items',None) or obj.get('__dict__',None):
            return self._flatten_dict(obj,level,current_path)
        if obj.get('__iter__',None):
            return self._flatten_list(obj,level,current_path)
        else:
            return [current_path],[str(obj)]

    def _flatten_dict(self,obj,level,current_path):
        """

        :param obj:
        :param level:
        :param current_path:
        :return:
        """
        items = obj.get('items',None) or obj.__dict__.items()
        cols = []
        data = []
        for k,v in items:
            flat_col, flat_data = self._flatten(v,level+1,current_path+self.path_deliminator+k)
            if flat_data:
                cols+= flat_col
                data = [data+row_v for row_v in flat_data]
        return cols,data

    def _flatten_list(self,obj,level,current_path):
        """

        :param obj:
        :param level:
        :param current_path:
        :return:
        """
        cols = []
        data = []
        for row in obj:
            flat_col,flat_data = self._flatten(row,level+1,current_path)
            if cols == flat_col:
                data.append(flat_data)
            else:
                cols += flat_col - cols
                data.append([c in flat_col and flat_data[flat_col.index(c) or None] for c in cols])
        return cols,data

    



