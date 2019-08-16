#!/usr/bin/python
#-*-coding:utf-8-*-

import os
import json
import pymysql
import hashlib
from sshtunnel import SSHTunnelForwarder
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

    @staticmethod
    def diff(dbHost, dbUser, dbPassword, dbName, dbPort,
             db2Host, db2User, db2Password, db2Name,db2Port,
             contentTables=None, debug=False,
             dbSshHost=None,dbSshPort=0,dbSshUserName=None,dbSshPassword=None,
             db2SshHost=None,db2SshPort=0,db2SshUserName=None,db2SshPassword=None,
             ):
        instance=MysqlDiff()
        if debug:
            print("dbHost:%s,dbUser:%s,dbPassword:%s,dbName:%s,dbPort:%d dbSshHost:%s dbSshPort:%d dbSshUserName:%s dbSshPassword:%s" %
              (dbHost, dbUser, dbPassword, dbName, dbPort,dbSshHost,dbSshPort,dbSshUserName,dbSshPassword))
            print("db2Host:%s,db2User:%s,db2Password:%s,db2Name:%s,db2Port:%d db2SshHost:%s db2SshPort:%d db2SshUserName:%s db2SshPassword:%s" %
              (db2Host, db2User, db2Password, db2Name, db2Port,db2SshHost,db2SshPort,db2SshUserName,db2SshPassword))
            print("contentTables:%s"%contentTables)
        #
        if (dbSshHost != None):
            server = SSHTunnelForwarder(
                (dbSshHost, dbSshPort),
                ssh_username=dbSshUserName,
                ssh_password=dbSshPassword,
                remote_bind_address=(dbHost, dbPort))
            server.start()
            print('server.local_bind_port:%d'%server.local_bind_port)
            db = pymysql.connect('127.0.0.1', dbUser, dbPassword, dbName, server.local_bind_port, charset="utf8")
        else:
            db = pymysql.connect(dbHost, dbUser, dbPassword, dbName, dbPort, charset="utf8")
        #
        if (db2SshHost != None):
            server2 = SSHTunnelForwarder(
                (db2SshHost, db2SshPort),
                ssh_username=db2SshUserName,
                ssh_password=db2SshPassword,
                remote_bind_address=(db2Host, db2Port))
            server2.start()
            db2 = pymysql.connect('127.0.0.1', db2User, db2Password, db2Name, server2.local_bind_port, charset="utf8")
        else:
            db2 = pymysql.connect(db2Host, db2User, db2Password, db2Name, db2Port, charset="utf8")
        #
        tables = instance.getTables(db,dbName,debug);
        tables2 = instance.getTables(db2,db2Name,debug);
        instance.diffTables(1,db2,db,db2Name,dbName,tables2,tables)
        instance.diffTables(2,db,db2,dbName,db2Name,tables,tables2)
        print("\n\n")
        if(contentTables!=None):
            for tableName in contentTables:
                instance.diffTableContent(db,db2,dbName,db2Name,tableName,debug)
        #
        os._exit(0)

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
