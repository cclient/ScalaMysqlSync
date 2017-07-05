# -*- coding: utf-8 -*-

import table_pdf


def _create_peewee(tablename, columninfos):
    cstrings = []
    for columninfo in columninfos:
        cname = columninfo["k"]
        ctype = columninfo["v"]
        ptype = '%s(db_column="%s")' % (ctype, cname)
        cstrings.append("\t" + cname.replace("-", "_") + " = " + ptype)
    return "class %s(Model):" % (tablename[0].upper() + tablename[1:]) + "\n" + "\n".join(cstrings) + '''\n\tclass Meta:
        database = DB().mysql_db
        db_table = '%s'
    ''' % tablename


def generator_tables_peewee(tables):
    for t in tables:
        print generator_table_peewee(t)


def generator_table_peewee(tablestring):
    lines = filter(lambda k: len(k) > 0, tablestring.split("\n"))
    tablename = lines[0].split(" ")[2][1:-1]
    tablecolumns = []
    for i in xrange(1, len(lines) - 1):
        tablecolumns.append(filter(lambda k: len(k) > 0, lines[i].split(" ")))
    create_columns = filter(lambda k: "`" in k[0], tablecolumns)
    cinfos = []
    sqltypemap = {
        "char": "CharField",
        "int": "IntegerField",
        "timestamp": "DateTimeField",
        "date": "DateTimeField",
        "datetime": "DateTimeField",
        "text": "TextField",
        "blob": "BlobField",
    }
    for create_column in create_columns:
        name = create_column[0][1:-1]
        typestring = create_column[1]
        matched = False
        for k in sqltypemap:
            if k in typestring:
                cinfos.append({"k": name, "v": sqltypemap[k]})
                matched = True
                continue
        if not matched:
            print "error", typestring
    return _create_py(tablename, cinfos)


generator_table_peewee(table_pdf.tables)
