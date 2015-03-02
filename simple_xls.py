"""
    This module is to handle excel and csv file manipulations.
    The builtin CSV module has problems with floats vs. int and with bools
"""

def read_csv(filename,deliminator=','):
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
    return ret

def write_csv(filename,data,deliminator=','):
    """ This will write a list of list to a csv file
    :param filename: str of the file name
    :param data: list of list of objects
    :param deliminator:
    :return: None
    """
    with open(filename,'w') as fn:
        fn.write('\n'.join([deliminator.join([xls_safe_str(cell) for cell in row]) for row in data]))

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

