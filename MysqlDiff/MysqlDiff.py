#!/usr/bin/python
#-*-coding:utf-8-*-

import json
import pymysql
import hashlib
# import sys;
# sys.path.append(".")
from . import Table
from . import Column

__author__ = 'skydu'

class MysqlDiff(object):
    #
    def md5(self,string):
        """
        计算字符串md5值
        :param string: 输入字符串
        :return: 字符串md5
        """
        m = hashlib.md5()
        m.update(string.encode())
        return m.hexdigest()
    #
    def getComment(self,comment):
        if comment==None:
            return ""
        try:
            data=json.loads(comment)
            return data[0]['value']
        except:
            return comment

    def getTables(self,db,dbName,debug):
        sql = "select table_name, TABLE_COMMENT from information_schema.tables " \
              "where table_schema = '%s' and table_type = 'base table'"%dbName
        cursor=db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        tables={}
        for table in data:
            t=Table(table[0], self.getComment(table[1]));
            tables[table[0]]=t
        cursor.close()
        if debug:
            print('sql:%s\ntables:%d\n%s'%(sql,len(tables),tables))
        return tables

    def getTableRows(self,db,dbTableName,debug):
        sql = "select * from %s"%dbTableName
        cursor=db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        rows=[]
        for row in data:
            rowContent=''
            for value in row:
                rowContent=rowContent+str(value)+',';
            rows.append(rowContent[:-1]);
        cursor.close()
        if debug:
            print('sql:%s\nrows:%d\n%s'%(sql,len(rows),rows))
        return rows

    def getColumns(self,db,dbName,tableName):
        sql = "SELECT  " \
              "COLUMN_NAME 列名,  " \
              "COLUMN_TYPE 数据类型,  " \
              "IS_NULLABLE 是否为空,    " \
              "COLUMN_DEFAULT 默认值,    " \
              "COLUMN_COMMENT 备注   " \
              "FROM  INFORMATION_SCHEMA.COLUMNS  " \
              "where  table_schema ='%s'  AND   table_name  = '%s';" % (dbName, tableName)
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        columns={}
        for column in data:
            c=Column(column[0],column[1],column[2],column[3],self.getComment(column[4]))
            columns[column[0]]=c
        cursor.close()
        return columns

    def diff(self,dbHost, dbUser, dbPassword, dbName, dbPort,dbHost2, dbUser2, dbPassword2, db2Name,
             dbPort2,contentTables=None,debug=False):
        if debug:
            print("dbHost:%s,dbUser:%s,dbPassword:%s,dbName:%s,dbPort:%d contentTables:%s" %
              (dbHost, dbUser, dbPassword, dbName, dbPort,contentTables))
            print("dbHost2:%s,dbUser2:%s,dbPassword2:%s,dbName2:%s,dbPort2:%d" %
              (dbHost2, dbUser2, dbPassword2, db2Name, dbPort2))
        db = pymysql.connect(dbHost, dbUser, dbPassword, dbName, dbPort, charset="utf8")
        db2 = pymysql.connect(dbHost2, dbUser2, dbPassword2, db2Name, dbPort2, charset="utf8")
        tables = self.getTables(db,dbName,debug);
        tables2 = self.getTables(db2,db2Name,debug);
        self.diffTables(1,db2,db,db2Name,dbName,tables2,tables)
        self.diffTables(2,db,db2,dbName,db2Name,tables,tables2)
        print("\n\n")
        if(contentTables!=None):
            for tableName in contentTables:
                self.diffTableContent(db,db2,dbName,db2Name,tableName,debug)

    def diffTables(self,index,db,db2,dbName,dbName2,tables,tables2):
        print("====================db%d[%s] difference============================"%(index,dbName2))
        for tableName, table in tables.items():
            if tableName in tables2:
                table2 = tables2[tableName]
                table.columns = self.getColumns(db, dbName, tableName)
                table2.columns = self.getColumns(db2, dbName2, tableName)
                for columnName, column in table.columns.items():
                    if columnName in table2.columns:
                        continue
                    print("%s miss column %s" % (tableName, columnName))
            else:
                print("miss table %s" % (tableName))

    def diffTableContent(self, db, db2,dbName,db2Name,tableName,debug):
        print("====================[%s] content differesnce============================" % (tableName))
        dbTableRows=self.getTableRows(db,tableName,debug)
        db2TableRows=self.getTableRows(db2, tableName,debug)
        dbTableRowMd5Map = {};
        db2TableRowMd5Map = {};
        for row in dbTableRows:
            dbTableRowMd5Map[self.md5(row)]=row;
        for row in db2TableRows:
            db2TableRowMd5Map[self.md5(row)]=row;
        self.diffTableRows(1,dbName,tableName,dbTableRowMd5Map,db2TableRowMd5Map)
        self.diffTableRows(2, db2Name, tableName, db2TableRowMd5Map, dbTableRowMd5Map)
        print("\n\n")

    def diffTableRows(self,index,dbName,tableName,dbTableRowMd5Map,db2TableRowMd5Map):
        print("====================db%d[%s.%s] difference============================"%(index,dbName,tableName))
        for md5, row in db2TableRowMd5Map.items():
            if md5 not in dbTableRowMd5Map:
                print("miss row %s" % (row))
        print("\n")
