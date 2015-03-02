""" This module will convert a Json to a CSV or a CSV to a Json
    It can also auto generate strings from templates include repeating sub templates.

    The data (Json or Python) can be embedded dictionaries, lists, or python objects.
        * python objects have to have items,__dict__, or __iterator__
        * upon conversion of csv_data to json, python objects will be treated as list or dict

    The embedded object will be created by flattening the path, and repeating values of previous values
        * note a dictionary of lists will quickly explode as the lists get multiply every permutation,
            so this won't work for that situation

    It is recommended that complex json objects with multiple embedded lists be broken up into multiple
    csv sheets

    The magic happens that the col_map of the json path, will produce the smallest table by removing duplicates.

    Note, Json is a string that can, within constraints, be converted to a python dictionary / list combination.
    For this module the term json_data stands for the python object
"""

__author__ = "Ben Christenson"
__date__ = '2015-02-27'

import csv
import simplejson
from collections import OrderedDict
import os

class JsonTable(object):
    _list_head = 'LIST'
    _list_postfix = '[...]'

    def __init__(self, json_data=None, csv_data=None, col_map=None, path_deliminator='.', csv_deliminator=','):
        """
        :param json_data:
        :param csv_data:
        :param col_map:
        :param path_deliminator:
        :param csv_deliminator:
        :return:
        """
        self.path_deliminator = path_deliminator
        self.csv_deliminator = csv_deliminator
        self.json_path = OrderedDict()
        self.col_map = col_map or OrderedDict()
        self._list_label = OrderedDict()

        self.json_data = self.load_json_data(json_data)
        self.csv_data = self.load_csv_data(csv_data or [])

    @staticmethod
    def str_list_of_list(obj):
        try:
            if not obj: return str(obj)
            size = len(obj[0])

            data = []
            for row in obj:
                data.append([repr(r) for r in row])

            widths = []
            for col in range(size):
                widths.append(max([len(row[col]) for row in data]))

            ret = [','.join([data[r][c].rjust(widths[c] + 1) for c in range(size)]) for r in range(len(data))]
            return '[[' + ' ]\n ['.join(ret) + ' ]]'
        except Exception as e:
            print '[\n%s\n]' % ('\n'.join([str(o) for o in obj]))
            raise e


    def load_xls_file(self, filename):
        """
        This will dump every worksheet within the xls file and for
          every file that has a map pair, it will load them all into one JsonTable
        :param filename:
        :return:
        """
        raise NotImplemented

    def save_xls_file(self, worksheet_map, path=None, csv_data=None, path_deliminator=None, csv_deliminator=None):
        """
        This will save a single excel file with worksheets named after each key in the
        worksheet_map using the col_map of the value.
        It will also save a worksheet with the same name plus "_map" of the map for reload.
        :param worksheet_map:
        :param path: str of the path to put the xls file and csv files.
        :param csv_data:
        :param path_deliminator:
        :param csv_deliminator:
        :return:
        """
        path = path or os.getcwd()
        for ws, col_map in worksheet_map.items():
            self.save_csv_file(filename='%s/%s.csv' % (path, ws), col_map=col_map, csv_data=csv_data,
                               csv_deliminator=csv_deliminator)
            self.save_csv_file(filename='%s/%s_map.csv' % (path, ws), csv_data=[['Name', 'Path']] + col_map.items(),
                               csv_deliminator=csv_deliminator)

        raise NotImplemented


    def load_csv_file(self, filename, path_deliminator=None, csv_deliminator=None):
        """
        :param filename:
        :param csv_deliminator:
        :return:
        """
        self.csv_deliminator = csv_deliminator or self.csv_deliminator
        with open(filename, 'r') as fn:
            self.csv_data = [row for row in csv.reader(fn, delimiter=self.csv_deliminator)]

        # print 'load_csv_file '+filename+'\n'+self.str_list_of_list(self.csv_data)
        self.load_csv_data(self.csv_data, path_deliminator=path_deliminator, csv_deliminator=csv_deliminator)

    def load_csv_data(self, csv_data, path_deliminator=None, csv_deliminator=None):
        """
        :param csv_data:
        :param path_deliminator:
        :param csv_deliminator:
        :return:
        """
        self.csv_deliminator = csv_deliminator or self.csv_deliminator
        self.path_deliminator = path_deliminator or self.path_deliminator
        assert (self.csv_deliminator != self.path_deliminator)
        self.csv_data = csv_data
        if csv_data:
            self.json_data = self.unflatten_csv(self.csv_data)
        return self.csv_data

    def load_map_file(self, filename, csv_deliminator=None):
        """
        This will read a csv file to define the col_map
        :param filename: str of the file name
        :param csv_deliminator: str of the csv deliminator
        :return: dict of the col_map
        """
        self.csv_deliminator = csv_deliminator or self.csv_deliminator
        with open(filename, 'r') as fn:
            map = csv.reader(fn, delimiter=csv_deliminator)
        return OrderedDict(map)

    def load_json_file(self, filename, path_deliminator=None, csv_deliminator=None):
        """
        This will load a ascii text file of json data and load it into a python object
        :param filename: str of the name of the file
        :return: csv_data
        """
        with open(filename, 'r') as fn:
            self.json_data = simplejson.load(fn, object_pairs_hook=OrderedDict)
        self.load_json_data(self.json_data, path_deliminator=path_deliminator, csv_deliminator=csv_deliminator)

    def load_json_data(self, json_data, path_deliminator=None, csv_deliminator=None):
        """
        :param json_data:
        :param path_deliminator:
        :param csv_deliminator:
        :return:
        """
        self.csv_deliminator = csv_deliminator or self.csv_deliminator
        self.path_deliminator = path_deliminator or self.path_deliminator
        assert (self.csv_deliminator != self.path_deliminator)
        self.json_data = json_data
        if self.json_data:
            self.csv_data = self.flatten_json(self.json_data, self.path_deliminator)
        return self.json_data

    def save_csv_file(self, filename, keys=None, col_map=None, csv_data=None, csv_deliminator=None):
        """
        :param filename:
        :param csv_data:
        :param csv_deliminator:
        :return:
        """
        csv_deliminator = csv_deliminator or self.csv_deliminator
        keys = keys or col_map
        # print self.str_list_of_list(csv_data)
        csv_data = csv_data or self.get_value_set(keys=keys, col_map=col_map)
        # print 'csv_data'
        # print self.str_list_of_list(csv_data)
        with open(filename, 'w') as fn:
            csv.writer(fn, delimiter=csv_deliminator).writerows(csv_data)

    def save_json_file(self, filename, json_data=None,indent=2):
        """
        :param filename:
        :param json_data:
        :return:
        """
        json_data = json_data or self.json_data
        with open(filename, 'w') as fn:
            fn.write(simplejson.dumps(json_data,indent=indent))

    def flatten_json(self, obj, path_deliminator=None):
        """
        :param obj:
        :param path_deliminator:
        :return:
        """
        self.path_deliminator = path_deliminator or self.path_deliminator
        header, data = self._flatten(obj=obj, level=0, path='')
        self.csv_data = [header] + data
        print 'Done flatten Json','\n', self.str_list_of_list(self.csv_data),'\n'
        return self.csv_data

    def unflatten_csv(self, data, path_deliminator=None):
        """
        :param data:
        :param path_deliminator:
        :return:
        """
        self.path_deliminator = path_deliminator or self.path_deliminator
        self._list_label.clear()

        header = data[0]
        if header[0].startswith(self._list_head):
            ret, row, col = self._unflatten_list(header, data, row=1, col=0, path='')
        elif len(header) == 1 and header[0] == '' and len(data) == 2:
            ret, row = data[1][0], 1
        else:
            ret, row, col = self._unflatten_dict(header, data, row=1, col=0, path='')

        print 'Done unflattening CSV','\n', str(ret),'\n'
        assert (row+1 == len(data))
        return ret

    def _unflatten_dict(self, header, data, row, col, path):
        """
        :param header:
        :param data:
        :param row:
        :param path:
        :return: tuple of (dict of data, int of row_processed, int of col))
        """
        if path.startswith(self.path_deliminator):
            path = path.split(self.path_deliminator, 1)[-1]
        print 'Unflatten_Dict', 'path = "%s"' % path, 'row = ', row, 'col = ', col, '\n', str(
            self.str_list_of_list([header, data[row]])),'\n'
        ret = {}
        row_processed = 1
        while col < len(header):
            key, sub_path, remaining_path = self._get_key_path(header[col], path)
            # print 'header[col]',header[col]
            # print 'key',key
            # print 'sub_path',sub_path
            # print 'path',path
            # print 'remaining_path',remaining_path

            if not header[col].startswith(path):
                return ret, row_processed, col

            elif self.path_deliminator in remaining_path:
                value, _row_processed, col = self._unflatten_dict(header, data, row, col, sub_path)
                row_processed *= _row_processed
                ret[key] = value

            elif header[col].endswith(self._list_postfix):
                value, _row_processed, col = self._unflatten_list(header, data, row, col, sub_path)
                row_processed *= _row_processed
                ret[key] = value
            else:
                ret[key] = data[row][col]

            col += 1
        print 'Done with Unflatten_List', 'row_processed = ', row_processed, '_col = ', col, '\n', ret,'\n'
        return ret, row_processed, col

    def _unflatten_list(self, header, data, row, col, path):
        """
        :param header:
        :param data:
        :param row:
        :param path:
        :return: tuple of (dict of data, int of row_processed, int of col)
        :rtype : tuple
        """
        if path.startswith(self.path_deliminator):
            path = path.split(self.path_deliminator, 1)[-1]
        print 'Unflatten_List', 'path = "%s"' % path, 'row = ', row, 'col = ', col, '\n', str(
            self.str_list_of_list([header, data[row]])),'\n'
        ret = []
        _row = row
        _col = col
        key_value = data[row][col]

        while _row < len(data) and data[_row][col] == key_value:
            _col = col + 1
            row_processed = 1
            while _col < len(header):
                key, sub_path, remaining_path = self._get_key_path(header[col], path)
                # print 'key',key
                # print 'sub_path',sub_path
                # print 'remaining_path',remaining_path

                if not header[col].startswith(path):
                    break
                elif header[_col].endswith(self._list_postfix):  # list within a list
                    value, _row_processed, _col = self._unflatten_list(header, data, _row, _col, sub_path)
                    row_processed *= _row_processed
                    ret.append(value)

                elif key:
                    value, _row_processed, _col = self._unflatten_dict(header, data, _row, _col, sub_path)
                    row_processed = _row_processed
                    ret.append(value)

                else:
                    ret.append(data[_row][_col])

                _col += 1
            _row += row_processed
        print 'Done with Unflatten_List', 'row_processed = ', _row - row, '_col = ', _col, '\n', ret,'\n'
        return ret, _row - row, _col

    def _flatten(self, obj, level, path):
        """

        :param obj:
        :param level:
        :param path:
        :return:
        """
        if path.startswith(self.path_deliminator):
            path = path.split(self.path_deliminator, 1)[-1]

        if isinstance(obj, dict):
            ret = self._flatten_dict(obj, level, path)
        elif isinstance(obj, list):
            ret = self._flatten_list(obj, level, path)
        elif getattr(obj, 'items', None) or getattr(obj, '__dict__', None):
            ret = self._flatten_dict(obj, level, path)
        elif getattr(obj, '__iter__', None):
            ret = self._flatten_list(obj, level, path)
        else:
            # print 'Flatten_Value',level,path,obj
            ret = [path], [[obj]]  # repr(obj)]]
        assert isinstance(ret[0], list)
        assert isinstance(ret[0][0], str)
        assert isinstance(ret[1], list)
        assert isinstance(ret[1][0], list)
        # print 'Return:: \n%s[\n%s]'%(str(ret[0]),'\n'.join([str(row) for row in ret[1]]))
        return ret

    def _flatten_dict(self, obj, level, path):
        """

        :param obj:
        :param level:
        :param path:
        :return:
        """
        print 'Flatten_Dict', level, path,'\n', obj,'\n'
        # print self.table_str(self.csv_data)
        items = (getattr(obj, 'items', None) or obj.__dict__.items)()
        cols = []
        data = [[]]
        for k, v in items:
            _col, _data = self._flatten(v, level + 1, path + self.path_deliminator + k)
            # print '_col',_col
            # print 'cols',cols
            # print '_data',_data
            cols += _col
            if len(_data) == 1:
                for row in data:
                    row += _data[0]
            else:
                new_data = []
                for old_row in data:
                    for new_row in _data or [[]]:
                        new_data.append(old_row + new_row)
                data = new_data
                # print 'cols',cols
                # print 'data',data
        return cols, data

    def _flatten_list(self, obj, level, path):
        """

        :param obj:
        :param level:
        :param path:
        :return:
        """
        print 'Flatten_List', 'level = ',level,'path = ', path, '\n',obj,'\n'
        # print self.table_str(self.csv_data)
        list_label = self._get_list_label(path)
        cols = [path + self._list_postfix]
        data = []
        for row in obj:
            _col, _data = self._flatten(row, level + 1, path)
            # print 'data',_data
            # print 'col',_col
            # print 'cols',cols

            if cols[1:] == _col and len(data) == 1:
                data.append([list_label] + _data[0])
                # print 'data1',data[-1]
            else:
                cols += [c for c in _col if c not in cols]
                for d in data:  # noinspection PyUnusedLocal
                    d += [None] * (len(cols) - len(d))
                for row in _data:
                    data.append([list_label] + [c in _col and row[_col.index(c)] or None for c in cols[1:]])
                    # print 'data2',data[-1]
        return cols, data

    def _get_key_path(self, column, path):
        """
        :param column: str of current header column
        :param path: str of the current path
        :return: tuple of next key and next path and remaining path
        """
        if path: path += self.path_deliminator
        remaining_path = column[len(path):].replace(self._list_postfix, '')
        key = remaining_path.split(self.path_deliminator)[0]
        sub_path = path and (path + self.path_deliminator + key) or key
        return key, sub_path, remaining_path

    def _get_list_label(self, path):
        """
        This will both indicate the key is a list and group the items in the list together.
        :param path: current path of the list
        :return: str of the unique label
        """
        self._list_label.setdefault(path, -1)
        self._list_label[path] += 1
        return '%s_%s_%s' % (self._list_head, self._list_label.keys().index(path), self._list_label[path])

    def merge_csv(self, new_csv_data, col_ids=None, col_map=None):
        """
        This will add the keys based on common ids in col_ids
        If the same column is in both the new and old data then the column
        will be added with the '_' prefix, unless the data is the same
        :param new_csv_data:
        :param col_id: dict of new_csv col ids to old_csv col ids
        :param col_map:
        :return:
        """
        col_map = col_map or self.col_map
        old_csv_data = self.csv_data
        new_header = new_csv_data[0]
        old_header = old_csv_data[0]

        for col in new_header:
            old_col = col_map.get(col, col)
            if old_col not in old_header:
                old_header.append(old_col)
            else:
                old_header.append('_' + old_col)
                col_map[col] = '_' + old_col

        for row in old_csv_data[1:]:
            row += [None] * (len(old_header) - len(row))

        filter_indexes = dict([(k, new_header.index(k)) for k in col_ids])
        transfer_indexes = dict([(new_header.index(k), old_header.index(col_map.get(k, k))) for k in new_header])
        while len(new_csv_data) > 1:  # data other than header
            new_row = new_csv_data[-1]

            new_filter = OrderedDict([(col_ids[k], new_row[filter_indexes[k]]) for k in col_ids])
            old_filter = OrderedDict([(k, new_row[filter_indexes[k]]) for k in col_ids])

            old_filtered_data = self.get_filtered_data(data_filter=old_filter, header=old_header, data=self.csv_data)
            new_filtered_data = self.get_filtered_data(data_filter=new_filter, header=new_header, data=new_csv_data)

            if not old_filtered_data:
                for new_row in new_filtered_data:
                    row = [None] * (len(new_header) - len(new_row)) + new_row
                    for k in new_filter:
                        row[old_header.index(k)] = new_filter[k]
                    old_csv_data.append(row)

            elif len(new_filtered_data) == 1:  # then it can work in place for speed
                for old_row in old_filtered_data:
                    for old_i, new_i in transfer_indexes.items():
                        old_row[old_i] = new_row[new_i]

            else:
                for old_row in old_filtered_data:
                    old_csv_data.remove(old_row)
                    for new_row in new_filtered_data:
                        copied_row = old_row.copy()
                        for old_i, new_i in transfer_indexes.items():
                            copied_row[old_i] = new_row[new_i]
                        old_csv_data.append(copied_row)

            for new_row in new_filtered_data:
                new_csv_data.remove(new_row)

        data = new_csv_data[1:]
        data.sort()
        self.csv_data = [old_header] + data
        self.json_data = self.unflatten_csv(self.csv_data, self.path_deliminator)

    def merge_data(self, new_json_data, col_ids=None, path_deliminator=None):
        path_deliminator = path_deliminator or self.path_deliminator
        new_csv_data = self.flatten_json(new_json_data, path_deliminator=path_deliminator)
        self.merge_csv(new_csv_data, col_ids=col_ids)

    def get_column(self, column_name):
        """
        This will extract the column from the table
        :param column_name: str of the column name / path
        :return: list of values
        """
        index = self.csv_data[0].index(column_name)
        return [row[index] for row in self.csv_data[1:]]

    def create_key(self, name, keys, col_map=None, csv_data=None):
        """
        This will create a new column that is a combination of other columns.
        One use of this could be to use for sub_templates
        :param keys:
        :param csv_data:
        :return:
        """
        csv_data = csv_data or None
        col_map = col_map or self.col_map
        csv_data[0].append(name)
        indexes = [csv_data[0].index(col_map.get(k, k)) for k in keys]
        for row in csv_data[1:]:
            row.append('; '.join([row[i] for i in indexes]))

    def template(self, text, sub_template=None, col_map=None, csv_data=None):
        """
        This will use string formatting to fill out text with the answers from csv_data
        It will do this for each row in csv_data and return a unique set of those answers
        :param text: str with format signposts i.e. {variable_name}
        :param sub_template: dict of variable names and SubTemplate object
        :param col_map: dict of col_maps from csv_data names to the text names
        :return: list of unique strings
        """
        sub_template = sub_template or {}
        col_map = col_map or self.col_map
        template_col = set(self.get_template_keywords(text) + [sub.id_cols for sub in sub_template.values()])
        for sub in sub_template:
            sub.keys = self.get_template_keywords(sub.text)

        data = self.get_value_set_of_dict(keys=template_col, col_map=col_map, csv_data=csv_data)
        ret = []
        for row in data:
            for k, sub in sub_template:
                data_filter = dict([(col, row[col]) for col in sub.id_cols])
                row[k] = sub.join_str.join(sub_template(text=sub.text, col_map=col_map, data_filter=data_filter))
            ret.append(text.format(**row))
        return ret

    @staticmethod
    def get_template_keywords(text):
        """
        This will return all of the keyword in the string format
        :param text:
        :return: list of keyword
        """
        return [col for _, col, _, _ in text._formatter_parser() if col]

    def sub_template(self, text, col_map, data_filter=None):
        """
        :param text:
        :param col_map:
        :param data_filter:
        :return:
        """
        template_col = self.get_template_keywords(text)
        data = self.get_value_set_of_dict(keys=template_col, data_filter=data_filter, col_map=col_map)
        return [text.format(**row) for row in data]

    def get_value_set_of_dict(self, keys, data_filter=None, col_map=None, only_unique=True, csv_data=None):
        """
        
        :param keys: 
        :param data_filter: 
        :param col_map: 
        :param only_unique: 
        :param csv_data: 
        :return:
        """
        data = self.get_value_set(keys=keys, data_filter=data_filter, col_map=col_map, only_unique=only_unique,
                                  csv_data=csv_data)
        return [OrderedDict([(data[0][i], row[i]) for i in range(len(row))]) for row in data[1:]]

    def get_value_set(self, keys, data_filter=None, col_map=None, only_unique=True, csv_data=None):
        """
        :param keys: list of values to get
        :param col_map: dict of col_mapping of keys names to column names
        :param only_unique: bool if true will return a only_unique set of values
        :return: list of list for the keys
        """
        col_map = col_map or self.col_map
        csv_data = csv_data or self.csv_data
        keys = keys or col_map.keys() or csv_data[0]
        ret = [keys]
        header = csv_data[0]
        indexes = [header.index(col_map.get(k, k)) for k in keys]

        filtered_data = self.get_filtered_data(data_filter=data_filter, header=header, data=csv_data[1:],
                                               col_map=col_map)
        for row in filtered_data:
            # print 'row = ',row
            # print 'indexes = ',indexes
            reduced_row = [row[i] for i in indexes]
            if only_unique == False or (reduced_row != ret[-1:] or reduced_row not in ret[1:-1]):
                ret.append(reduced_row)
        return ret

    def get_filtered_data(self, data_filter=None, header=None, data=None, col_map=None):
        """
        This will data_filter the data and return only the columns that match the data_filter
        :param data_filter:
        :param data:
        :param col_map:
        :return: list of list
        """
        data = data or self.csv_data[1:]
        if data_filter is None: return data
        header = header or self.csv_data[0]
        col_map = col_map or self.col_map
        ret = []
        data_filter_index = dict([(header.index(col_map.get(k, k)), v) for k, v in data_filter.items()])
        for row in data:
            if False not in [row[k] == v for k, v in data_filter_index.items()]:
                ret.append(row)
        return ret

    def get_empty_json_structure(self, value=None):
        """
        :param value: obj of the value to put in the data structure
        :return: obj of the data structure without data
        """
        return self.unflatten_csv([self.csv_data[0], [value] * len(self.csv_data[0])])


    def __repr__(self):
        """
        This will return a unique entry count for each column
        :return: str
        """
        if not self.csv_data: return 'Data has not been loaded'
        ret = ''
        for i in range(len(self.csv_data)):
            values = [row[i] for row in self.csv_data[1:]]
            ret += str(len(set(values))).ljust(5) + ' ' + self.csv_data[0][i] + '\n'
        return ret.strip()


class SubTemplate(object):
    def __init__(self, id_cols, text, join_str='\n'):
        self.id_cols = id_cols
        self.join_str = join_str
        self.text = text

















