import os
import re
import time
import pymysql
import requests
import numpy as np

import fine_function as ff

from bs4 import BeautifulSoup
from urllib.request import urlopen


if os.name == 'nt':
    conn = pymysql.connect(host='127.0.0.1', port=3306,
                           user='root', password='<password>',
                           db='mysql', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute('USE webscraping')
elif os.name == 'posix':
    conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock',
                           user='root', password='<password>',
                           db='mysql', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute('USE webscraping')


class Website:
    def __init__(self, country_code, name, url, titleTag, bodyTag):
        self.country_code = country_code
        self.name = name
        self.url = url
        self.titleTag = titleTag
        self.bodyTag = bodyTag


class SearchSite:
    def __init__(self, searchUrl, resultListing, resultUrl, absoluteUrl,
                 url, titleTag, bodyTag):
        self.searchUrl = searchUrl
        self.resultListing = resultListing
        self.resultUrl = resultUrl
        self.absoluteUrl = absoluteUrl
        self.url = url
        self.titleTag = titleTag
        self.bodyTag = bodyTag


class Reuters(Website):
    def __init__(self, country_code, name, url, targetPattern, absoluteUrl,
                 titleTag, bodyTag):
        Website.__init__(self, country_code, name, url, titleTag, bodyTag)
        self.targetPattern = targetPattern
        self.absoluteUrl = absoluteUrl


class Content:
    def __init__(self, url, title, body):
        self.url = url
        self.title = title
        self.body = body

    def printing(self):
        print('URL : {}'.format(self.url))
        print('TITLE : {}'.format(self.title))
        print('BODY : \n {}'.format(self.body))


class Crawler:

    def __init__(self, site):
        self.site = site
        self.visited = []
        self.pages = set()
        self.count_end = 0

    def country_code(self):
        cur.execute("SELECT * FROM country_code WHERE country = %s",
                         (self.site.country_code))
        if cur.rowcount != 0:
            country_id = cur.fetchone()[0]
            return country_id
        else:
            cur.execute("INSERT INTO country_code (country) VALUES (%s)",
                             (self.site.country_code))
            conn.commit()
            return cur.lastlowid

    def website_id(self):
        cur.execute("SELECT * FROM website_id WHERE website_name = %s AND web_url = %s",
                    (self.site.name, self.site.url))
        if cur.rowcount != 0:
            websiteId = cur.fetchone()[0]
            return websiteId
        else:
            cur.execute("INSERT INTO website_id (website_name, web_url) VALUES (%s, %s)",
                        (self.site.name, self.site.url))
            conn.commit()
            return cur.lastlowid

    def news_categories(self):
        cur.execute("SELECT * FROM news_categories WHERE category_tag = %s",
                    (self.site.targetPattern))
        if cur.rowcount != 0:
            newsCategories = cur.fetchone()[0]
            return newsCategories
        else:
            cur.execute("INSERT INTO news_categories (category_tag) VALUES (%s)",
                        (self.site.targetPattern))
            conn.commit()
            return cur.lastlowid

    def middle_table(self, country_code, website_id, news_categories):
        cur.execute("SELECT * FROM middle_table WHERE country_code = %s AND website_id = %s AND nwes_categories = %s",
                         (country_code, website_id, news_categories))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO middle_table (country_code, website_id, nwes_categories) VALUES (%s, %s, %s)",
                             (country_code, website_id, news_categories))
            conn.commit()
            print('ALL_Insert : complete')
            return cur.lastlowid
        else:
            return cur.fetchone()[0]

    def website(self, bs, title, content, middle_table, pageUrl):
        try:
            timestamp = bs.find_all('a', {'span' 'timestamp'})
            if not timestamp:
                cur.execute('SELECT * FROM website WHERE middle_table_id = %s AND title = %s AND content = %s',
                            (middle_table, title, content))
                if cur.rowcount == 0:
                    cur.execute('INSERT INTO website (middle_table_id, title, content, url) VALUES (%s, %s, %s, %s)',
                                (middle_table, title, content, pageUrl))
                    conn.commit()
            else:
                cur.execute(
                    'SELECT * FROM website WHERE middle_table_id = %s AND title = %s AND content = %s AND timestamp = %s',
                    (middle_table, title, content, timestamp))
                if cur.rowcount == 0:
                    cur.execute(
                        'INSERT INTO website (middle_table_id, title, content, timestamp, url) VALUES (%s, %s, %s, %s, %s)',
                        (middle_table, title, content, timestamp, pageUrl))
                    conn.commit()
        except AttributeError as AT:
            print('Attribute error :', AT)

    def page_Url(self, url):
        cur.execute('SELECT * FROM page_url WHERE url = %s', (url))
        if cur.rowcount != 0:
            # print('Not INSERT url')
            return url
        else:
            cur.execute('INSERT INTO page_url (url) VALUES (%s)', (url))
            conn.commit()
            return url

    def url_Insert(self, url):
        cur.execute('SELECT * FROM page_url WHERE url = %s', (url))
        if cur.rowcount == 0:
            return 0
        else:
            return 1

    def server_Query(self, ac):
        global content
        if ac == 'ymd':
            print('ymd test')
            f_year_ymd, f_month_ymd, f_day_ymd = ff.year_month_day_ymd()
            cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_ymd}-{f_month_ymd}-{f_day_ymd}%'"
                        f" AND content NOT LIKE 'skip%'")
            content = cur.fetchall()
        elif ac == 'ym':
            print('ym test')
            f_year_ym, f_month_ym = ff.year_month_day_ym()
            cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_ym}-{f_month_ym}%'"
                        f" AND content NOT LIKE 'skip%'")
            content = cur.fetchall()
        elif ac == 'y':
            print('y test')
            f_year_y = ff.year_month_day_y()
            cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_y}%'"
                        f" AND content NOT LIKE 'skip%'")
            content = cur.fetchall()
        elif ac == 'st':
            print('st test')
            f_year_ymdst, f_month_ymdst, f_day_ymdst, f_st_ymdst = ff.year_month_day_ymdst()
            cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_ymdst}-{f_month_ymdst}-{f_day_ymdst}%'"
                        f" AND content NOT LIKE '{f_st_ymdst}%'")
            content = cur.fetchall()
        return content

    def getURLBS(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, 'html.parser')

    def getURLBS_a(self, pageUrl):
        session = requests.Session()
        # -----　Reuters Login ----------
        params = {'email': '<ID>', 'password': '<password>'}
        session.post('<LOGIN:URL>', data=params)
        # ------------------------------
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        html = session.get("{}{}".format(self.site.url, pageUrl), headers=headers,
                           allow_redirects=True)
        # html = urlopen('{}{}'.format(self.site.url, pageUrl))
        return BeautifulSoup(html.text, 'html.parser')

    def getURLBS_b(self, pageUrl):
        """
        Default URL Open
        :param pageUrl:
        :return:
        """
        html = urlopen('{}{}'.format(self.site.url, pageUrl))
        return BeautifulSoup(html, 'html.parser')

    def safeGet(self, pageObj, selector):
        childObj = pageObj.select(selector)
        if childObj is not None and len(childObj) > 0:
            return childObj[0].get_text()
        return ""

    def parse(self, url):
        bs = self.getURLBS(url)
        if bs is not None:
            title = self.safeGet(bs, self.site.titleTag)
            body = self.safeGet(bs, self.site.bodyTag)
            if title != '' and body != '':
                content = Content(url, title, body)
                content.printing()

    def crawl(self):
        """start crawl get_link"""
        self.getLinks('')

    def getLinks(self, pageUrl):
        """
        :param pageUrl:
        :return:
        """
        print('Pages ADDED : ', self.pages)
        numb = np.random.randint(5, 11)
        time.sleep(numb)
        bs = self.getURLBS_a(pageUrl)
        r_count = self.url_Insert(pageUrl)
        if r_count == 1:
            for link in bs.find_all('a', href=re.compile(self.site.targetPattern)):
                print('r_count1 : FOR')
                if 'href' in link.attrs:
                    self.pages.add(pageUrl)
                    print('Pages r_count_1 : ', self.pages)
                    if link.attrs['href'] not in self.pages:
                        if self.count_end != 20:
                            url = link.attrs['href']
                            self.count_end += 1
                            print('=' * 30)
                            print('r_count 1. count_end+1. Not content insert. getLinks next')
                            print('Already Scraped. The URL already exists in the Server')
                            print('Child Process', os.getpid())
                            print('Count_END', self.count_end)
                            print('pages Count_end Not 20 ', self.pages)
                            print('Next getLinks URL', url)
                            print('=' * 30)
                            print('\n')
                            time.sleep(10)

                            self.getLinks(url)
                        elif self.count_end == 20:
                            print('Count 5 end')
                            exit()
                    else:
                        print('Not in href pages')
                else:
                    print('href Error')
        elif r_count == 0:
            self.count_end -= self.count_end
            print('Count Reset : ', self.count_end)

        try:
            print('try in : safe get in')
            time.sleep(numb)
            title = self.safeGet(bs, self.site.titleTag)
            content = self.safeGet(bs, self.site.bodyTag)
            print('title and content , safeGet Complete')
            if title == '':
                print('Title Error : system exit')
                print('Process ID : ', os.getpid())
                # exit()
            elif title != '' and content == '':
                for script in bs(["script", "style"]):
                    script.extract()
                text = bs.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                for len_text in text.splitlines():
                    if len(len_text) > 300:
                        content = len_text

                web_insert = self.middle_table(self.country_code(), self.website_id(), self.news_categories())
                self.website(bs, title, content, web_insert, pageUrl)
                print('=' * 30)
                print('Process ID : ', os.getpid())
                print('URL : ', pageUrl)
                print('***Tag is not working properly. Please check the tag on the target site. Not Content.***')
                print('title : ', title)
                print('content: ', content)

                self.count_end -= self.count_end
                pageUrl = self.page_Url(pageUrl)
                self.pages.add(pageUrl)
                bs = self.getURLBS_a(pageUrl)
                print('*' * 30)
                print('=' * 30)
                print('\n')
                print('pages', self.pages)
                print('*' * 30)
                print('\n')

            elif title != '' or content != '':

                web_insert = self.middle_table(self.country_code(), self.website_id(), self.news_categories())
                self.website(bs, title, content, web_insert, pageUrl)
                print('=' * 30)
                print('title, content IN.')
                print('pageUrl : ', pageUrl)
                print('Process ID : ', os.getpid())
                print('title : ', title)
                print('content : ', content)
                print('*' * 30)
                print('=' * 30)
                print('\n')

                self.count_end -= self.count_end
                pageUrl = self.page_Url(pageUrl)
                self.pages.add(pageUrl)
                print('pages', self.pages)
                print('*' * 30)
                print('\n')

        except AttributeError:
            print('This Page is missing something! Continuing')
            print('AttributeError: "Cursor" object has no attribute "lastlowid"')

        for link in bs.find_all('a', href=re.compile(self.site.targetPattern)):
            if 'href' in link.attrs:
                if link.attrs['href'] not in self.pages:
                    url = link.attrs['href']

                    time.sleep(5)
                    newpage = self.page_Url(pageUrl)
                    print('-' * 30)
                    print('End for. New Loop.')
                    print('Child Process : ', os.getpid())
                    print('Loop INSERT : ', newpage)
                    print('new URL. NEXT getLinks : ', url)
                    print('-' * 30)
                    print('\n')
                    self.getLinks(url)

    def search(self, topic):
        print(self.site.searchUrl)
        if self.site.searchUrl and self.site.resultListing and self.site.resultUrl is not None:
            global url
            bs = self.getURLBS(self.site.searchUrl + topic)
            searchResults = bs.select(self.site.resultListing)
            for result in searchResults:
                try:
                    url = result.select(self.site.resultUrl)[0].attrs["href"]
                    print('url :', url)
                except IndexError as ie:
                    print('Index Error {No href Error} :', ie)
                    continue

                if (self.site.absoluteUrl):
                    bs = self.getURLBS(url)
                else:
                    bs = self.getURLBS(self.site.url + url)
                if bs is None:
                    print("Something was wrong with that page or URL. Skipping!")
                    return

                title = self.safeGet(bs, self.site.titleTag)
                body = self.safeGet(bs, self.site.bodyTag)
                if title != '' and body != '':
                    content = Content(url, title, body)
                    content.printing()
        else:
            print("None")
            pass

    def search_1(self, topic):
        bs = self.getURLBS(self.site.searchUrl + topic)
        searchResults = bs.select(self.site.resultListing)
        for results in searchResults:
            url = results.select(self.site.resultUrl)[0].attrs["href"]
            print('url :', url)
            print('Bool:', (self.site.absoluteUrl))
            if (self.site.absoluteUrl):
                bs = self.getURLBS(url)
                print('Bs')
            else:
                bs = self.getURLBS(self.site.url + url)
            if bs is None:
                print("Something was wrong with that page or URL. Skipping!")
                return

            title = self.safeGet(bs, self.site.titleTag)
            body = self.safeGet(bs, self.site.bodyTag)
            if title != '' and body != '':
                content = Content(url, title, body)
                content.printing()




