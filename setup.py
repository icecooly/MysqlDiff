#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
import sys, os
from os import path

"""
See https://github.com/icecooly/MysqlDiff
"""

VERSION = '1.10'

DESCRIPTION = (
    '自动检测新旧库表的差异以及字段差异,方便升级项目时更新旧表,支持Ssh隧道'
)

setup(
        name='MysqlDiff', 
        version=VERSION, 
        description="mysql表结构比较工具",
        long_description=DESCRIPTION,
        classifiers=[],
        keywords='mysql diff',
        include_package_data = True,
        author='skydu',
        author_email='icecooly.du@qq.com', 
        url='https://github.com/icecooly/MysqlDiff',
        license='MIT',
        packages=find_packages(),
        install_requires=['pymysql','sshtunnel'],
        extras_require={}
)
