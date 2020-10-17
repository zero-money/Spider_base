import urllib.request
import urllib.parse
import xlwt
import re
import sqlite3
from bs4 import BeautifulSoup


def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getData(baseurl)
    # savepath = u".\\豆瓣电影Top250.xls"、
    dbpath = "movie.db"
    # saveData(datalist, savepath)
    saveData2DB(datalist, dbpath)
    # askURL("https://movie.douban.com/top250?start=")


# 影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')  # 生成正则表达式，表示规则（字符串的模式）
# 影片图片
findImgSrc = re.compile(r'<img.*?src="(.*?)"', re.S)  # re.S忽略出现的换行符
# 影片的片名
findTitle = re.compile(r'<span class="title">(.*?)</span>')
# 影片的评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
# 评价人数
findPeople = re.compile(r'<span>(\d*)人评价</span>')
# 找到概况
findInq = re.compile(r'<span class="inq">(.*?)</span>')
# 找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0, 10):  # 调用页面信息的函数 10次
        url = baseurl + str(i * 25)
        html = askURL(url)  # 保存获取到的网页源码

        # 逐一进行解析
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):  # 查找符合要求的字符串，形成列表
            # print(item)
            # 测试：查看电影item的全部信息
            data = []  # 保存一部电影的所有信息
            item = str(item)

            # 影片详情链接
            link = re.findall(findLink, item)[0]  # re库通过正则表达式的模式查找指定的字符串
            data.append(link)  # 添加链接
            imgSrc = re.findall(findImgSrc, item)[0]
            data.append(imgSrc)  # 添加图片
            titles = re.findall(findTitle, item)
            if len(titles) == 2:
                ctitle = titles[0]  # 添加中文名
                data.append(ctitle)
                otitle = titles[1].replace("/", "")
                data.append(otitle)  # 添加外国名
            else:
                data.append(titles[0])
                data.append(' ')  # 留空
            # 评分
            rating = re.findall(findRating, item)[0]
            data.append(rating)
            # 评价人数
            people = re.findall(findPeople, item)[0]
            data.append(people)
            # 添加概述
            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")  # 去掉句号
                data.append(inq)  # 添加概述
            else:
                data.append(" ")
            bd = re.findall(findBd, item)[0]
            bd = re.sub(r'<br(\s+)?/>(\s+)?', " ", bd)  # 去掉<br/>
            bd = re.sub(r'/', " ", bd)  # 替换\
            data.append(bd.strip())  # 去掉前后空格

            datalist.append(data)  # 把电影放入datalist
    # print(datalist)       # 打印全部内容
    return datalist


# 得到指定的网页内容
def askURL(url):
    headers = {
        "User-Agent": "abc"
    }  # 用户代理
    request = urllib.request.Request(url, headers=headers)
    html = ''
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 保存数据
def saveData(datalist, savepath):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)  # 创建工作表
    col = '电影详情链接', "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息"
    for i in range(0, 8):
        sheet.write(0, i, col[i])  # 列名
    for i in range(0, 250):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 8):
            sheet.write(i + 1, j, data[j])
    book.save(savepath)  # 保存


def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 5 or index == 4:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
            insert into movie250(
            info_link, pic_link,cname,ename,score,rated,introduction,info)
            values(%s)''' % ",".join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()
    print("...")


def init_db(dbpath):
    sql = '''
        create table movie250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        introduction text,
        info text
        )'''
    # 创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    # cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
    # init_db("movie_test.db")
    print("爬取完毕")
