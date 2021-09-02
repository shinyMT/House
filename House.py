# -*- coding:utf-8 -*-
# Author:thy
import socket
import sys
import time

from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import sqlite3
import random

# 请求头
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 "
    "Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; "
    ".NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR "
    "2.0.50727)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR "
    "3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR "
    "3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 ("
    "Change: 287 c9dfb30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 "
    "Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

# 创建正则表达式对象
findName = re.compile(r'<a href="(.*?)">')
findStyle = re.compile(r'<span style="(.*?)">')
findAddress = re.compile(r'<a class="resblock-location"')
findPrice = re.compile(r'<div class="resblock-price"')

# 随机获取请求头，避免因多次访问被拒绝
def createHeader():
    headers = dict()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    headers["Referer"] = "http://www.ke.com"
    return headers
    pass


# 获取指定的url的html网页结构
def askUrl(url):
    '''
    :param url:要获取的url地址
    :return:返回网页结构
    '''
    # head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    #                       "Chrome/92.0.4515.159 " "Safari/537.36"}
    # 设置请求链接，url+头部信息
    req = urllib.request.Request(url, headers=createHeader())
    try:
        response = urllib.request.urlopen(req)
        # 读取响应内容
        html = response.read().decode('utf-8')
        # print(html)
        pass
    except urllib.error.URLError as msg:
        # 打印异常状态码和信息
        if hasattr(msg, "code"):
            print(msg.code)
            pass
        if hasattr(msg, "reason"):
            print(msg.reason)
            pass
        pass
    return html
    pass


# 解析网页结构获取数据
def getData(baseUrl):
    '''
    :param baseUrl: 不带参数的网页地址
    :return: 返回数据列表
    '''
    # 存放所有的楼盘数据
    dataList = []
    # 循环8次获取网页数据--因为网页一共只有8页
    for i in range(1, 9):
        # 拼接成完整的地址
        url = baseUrl + str(i) + '/'
        # 得到网页结构
        html = askUrl(url)
        # 解析获取到的html网页
        soup = BeautifulSoup(html, "html.parser")
        print(soup)
        # 根据网页源码，找到class=has-results的li
        for item in soup.select('li[class="resblock-list post_ulog_exposure_scroll has-results"]'):
            # print(item)
            # 保存一个楼盘的的数据
            houseList = []
            # 将html节点全部转化为字符串
            item = str(item)
            print(item)
            # 存放楼盘名字
            name = re.findall(findName, item)[0]
            houseList.append(name)
            print(name)
            # 存放楼盘类型
            style = re.findall(findStyle, item)[0]
            houseList.append(style)
            # 存放楼盘地址
            address = re.findall(findAddress, item)[0]
            houseList.append(address)
            # 存放楼盘价格
            price = re.findall(findPrice, item)[0]
            houseList.append(price)

            # 将处理好的单个楼盘信息存放到dataList中
            dataList.append(houseList)
            print(dataList)
            pass
        pass
    return dataList
    pass


# 为数据库建表
def initDB(dbPath):
    '''
    :param dbPath: 数据库路径
    '''
    # 创建数据库连接
    conn = sqlite3.connect(dbPath)
    print("数据库连接成功")
    # 获取数据库游标
    cursor = conn.cursor()
    # 书写sql语句
    sqlDrop = "drop table if exists house;"
    sql = '''
        create table house(
            id integer primary key autoincrement,
            name varchar,
            style varchar,
            address text,
            price numeric 
        );
    '''
    # 执行sql语句
    cursor.execute(sqlDrop)
    cursor.execute(sql)
    # 提交数据库操作
    conn.commit()
    # 关闭数据库连接
    conn.close()
    pass


# 保存数据到数据库
def saveData(dbPath, dataList):
    '''
    :param dbPath: 数据库保存路径
    :param dataList: 数据列表
    '''
    # 初始化数据库
    initDB(dbPath)
    # 创建新的数据库连接
    conn = sqlite3.connect(dbPath)
    # 获取操作游标
    cursor = conn.cursor()
    # 读取dataList的内容，并将其添加到数据库中
    for data in dataList:
        # 给每列的数据添加存储格式
        for i in range(len(data)):
            # 如果是价格就不添加双引号，进行下一次判断
            if i == 4:
                continue
                pass
            data[i] = '"' + str(data[i]) + '"'
            pass

        # 插入数据，值之间用逗号分隔
        sql = "insert into house(name,style,address,price) values (?)" \
            .format(data)
        # 执行sql语句
        cursor.execute(sql)
        # 提交数据库操作
        conn.commit()
        pass
    # 关闭数据库连接
    cursor.close()
    conn.close()
    pass


# 主函数
def main():
    # 不带参数值的url
    # 完整地址：https://dy.fang.ke.com/loupan/pg1/
    baseUrl = "https://dy.fang.ke.com/loupan/pg"
    # 爬取网页结构并解析数据
    dataList = getData(baseUrl)
    # askUrl(baseUrl)
    # 保存数据--在当前目录下生成一个名为house.db的数据库文件
    dbPath = "house.db"
    saveData(dbPath, dataList)
    pass


if __name__ == '__main__':
    main()
    pass
