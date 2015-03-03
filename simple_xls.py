"""
    This module is to handle excel and csv file manipulations.
    The builtin CSV module has problems with floats vs. int and with bools
"""

def read_csv(filename,deliminator=',',transpose=False):
    """ This will read in a csv file, as excel would write it.
    :param filename: this
    :return: list of list of the data
    """
    with open(filename,'r') as fn:
        text = fn.read()

    ret = []
    for row in text.split('\n'):
        ret.append([])
        for cell in row.split(deliminator):
            if cell.strip() == '':
                ret[-1].append(None)
            else:
                try:
                    ret[-1].append(eval(cell,{},{}))
                except:
                    ret[-1].append(cell)
    if transpose:
        trans_ret = []
        for i in range(len(ret[0])):
            trans_ret.append([ret[j][i] for j in range(len(ret))])
        return trans_ret
    return ret

def write_csv(filename,data,deliminator=',',space_column=None, transpose=False):
    """ This will write a list of list to a csv file
    :param filename: str of the file name
    :param data: list of list of objects
    :param deliminator:
    :return: None
    """
    space_column = space_column or not transpose
    str_data = [[xls_safe_str(cell) for cell in row] for row in data]
    if transpose:
        str_data = []
        for i in range(len(data[0])):
            str_data.append([xls_safe_str(data[j][i]) for j in range(len(data))])
    else:
        str_data = [[xls_safe_str(cell) for cell in row] for row in data]

    if space_column:
        widths = []
        for col in range(len(str_data[0])):
            widths.append(max([len(row[col]) for row in str_data]))
        str_data = [' '.join([(row[c]+deliminator).rjust(widths[c]+1) for c in range(len(str_data[0]))])[:-1] for row in str_data]
    else:
        str_data = [deliminator.join(row) for row in str_data]

    with open(filename,'w') as fn:
        fn.write('\n'.join(str_data))

def xls_safe_str(cell):
    """
    This will return a string that excel interprets correctly when importing csv
    :param cell:
    :return:
    """
    if cell is None: return ''
    ret =  repr(cell)
    if ret.startswith("u'"): ret = ret[1:]
    if ret and ret!= "''" and ret[0] == "'" and ret[-1] == "'":
        ret = ret.replace("'","~~~TEMP~~~")
        ret = ret.replace('"',"'")
        ret = ret.replace('~~~TEMP~~~','"')
    return ret

def str_list_of_list(obj,deliminator=','):
    """
    This will return the list of list as an evenly spaced columns
    :param obj:
    :return:
    """
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
        raise e

