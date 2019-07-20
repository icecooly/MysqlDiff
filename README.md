# MysqlDiff
自动检测新旧库表的差异以及字段差异,方便升级项目时更新旧表

## 安装
[需要python3.0以上]
 
```shell
pip install MysqlDiff
```


## 使用
```python
>>> from MysqlDiff import MysqlDiff
>>> MysqlDiff.diff('127.0.0.1','root','password','db_test',3306,'127.0.0.1','root','password','db_test',3307)
>>> ====================db1[db_test] difference============================
>>> miss table t_test
>>> ====================db2[db_test] difference============================
>>> t_test2 miss column name
```

```python
>>> from MysqlDiff import MysqlDiff
>>> MysqlDiff.diff('127.0.0.1','root','password','db_test',3306,'127.0.0.1','root','password','db_test',3307,['t_config'])
>>> ====================db1[db_test] difference============================
>>> miss table t_test
>>> ====================db2[db_test] difference============================
>>> t_test2 miss column name
```
