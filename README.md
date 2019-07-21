# MysqlDiff
自动检测新旧库表的差异以及字段差异,方便升级项目时更新旧表

## 安装
[需要python3.0以上]
 
```shell
pip install MysqlDiff
```


## 对比表结构
```python
>>> from MysqlDiff import MysqlDiff
>>> MysqlDiff.diff('127.0.0.1','root','password','db_test',3306,'127.0.0.1','root','password','db_test',3307)
>>> ====================db1[db_test] difference============================
>>> miss table t_test
>>> ====================db2[db_test] difference============================
>>> t_test2 miss column name
```

## 除了对比表结构，也对比表的内容
```python
>>> from MysqlDiff import MysqlDiff
>>> MysqlDiff.diff('127.0.0.1','root','password','db_test',3306,'127.0.0.1','root','password','db_test',3307,['t_config'])
>>> ====================db1[db_test] difference============================
>>> miss table t_test
>>> ====================db2[db_test] difference============================
>>> t_test2 miss column name

>>> ====================[t_config] content differesnce============================
>>> ====================db1[db_test.t_config] difference============================
>>> miss row 1,system.web.url,https://cs.xxx.com/,String,0,0,首页地址
>>> ====================db2[db_test.t_config] difference============================
>>> miss row 1,system.web.url,https://cs.xxx.cn/,String,0,0,首页地址

```
