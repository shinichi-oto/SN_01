import os
import ctypes
import _winapi
import sys
import time
import pymysql
import argparse
import pandas as pd

#import multiprocessing
#multiprocessing.set_start_method('spawn')
#ctypes.windll.kernel32.SetStdHandle(_winapi.STD_INPUT_HANDLE, 0)

from multiprocessing import Process

from crawler import Crawler, Reuters, SearchSite
import fine_function as ff
from fine_function import cond_Query, server_Query, get_text_ratio, \
    summary_clean_sentence, getNgrams, getSentenceCount, year_month_day_search, \
    randomWord, buildDict
import hugging_translate as ht
import summary as sm
import wordout as wo


siteData = [
    ['<COUNTRY>', '<SITE>', '<URL>', '^(/<CONT>/)', False,
     '<TAG: Title>', '<TAG: content>'],
]


searchSiteData = [
    ['<SEARCH:URL>', '<TAG>',
     '<TAG:SEARCH>', False, '<URL>',
     '<TAG:T>', '<TAG:CONTENT>'
     ],
]

if __name__ == '__main__':

    # ---------------------------------------------------------------------------
    # load Tag File System
    # --------------- ExcelFile -------------------------------------------------

    xlsx = pd.ExcelFile('Book2.xlsx')
    US_excel = pd.read_excel(xlsx, 'Sheet12')

    siteData = []
    for i in range(len(US_excel.iloc[:, 1:])):
        site = list(US_excel.iloc[i, 1:])
        siteData.append(site)
    # ----------------------------------------------------------------------------
    # ----------------------------------------------------------------------------

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", help="Multiprocess Crawling. Input Start", nargs='?')
    parser.add_argument("-s", help="Search Crawling. Input Start")
    parser.add_argument("-n", help="Ngram System: ")
    parser.add_argument("-nsum", help="Ngram Summary System")
    parser.add_argument("-nj", help="Ngram_jp_translation_System")
    parser.add_argument("-ns", help="Summary System: ")
    args = parser.parse_args()

    if not (args.m or args.s or args.n, args.ns):
        print("Need to -m or -s is Find string")
        sys.exit(1)

    # ------------------------------------------------------------------
    # ------------ Start multiprocess Crawling -------------------------
    if args.m == 'start':

        try:
            sites = []
            for row in siteData:
                sites.append(Reuters(row[0], row[1], row[2],
                                     row[3], row[4], row[5],
                                     row[6]))

            processes = []
            for targetSite in sites:
                crawler = Crawler(site=targetSite)
                processes.append(crawler)

            active_process = []
            for i in range(len(processes)):
                active_process.append(Process(target=processes[i].crawl, args=()))
                time.sleep(2)

            for p in active_process:
                p.start()

        except ConnectionRefusedError as c:
            print(c)
            print('WinError 10061 : Not Access')
        except pymysql.err.OperationalError as e:
            print(e)
            print('Server Password Error')

    # -------------------------------------------------------------------
    # ----------- Start Search ------------------------------------------
    elif args.s == 'start':

        searchSiteAdded = []
        for row in searchSiteData:
            searchSiteAdded.append(SearchSite(row[0], row[1], row[2],
                                              row[3], row[4], row[5], row[6]))

        for targetSite in searchSiteAdded:
            crawler = Crawler(site=targetSite)
            print("Search Topics")
            crawler.search_1(topic=input())

    # -------------------------------------------------------------------
    # ---------- Start Ngram System -------------------------------------
    elif args.n == 'start':

        try:
            cond_text = cond_Query()
            content = server_Query(cond_text)
            cont = get_text_ratio(content)
            content = summary_clean_sentence(str(cont))
            ngrams = getNgrams(content, 3)

            print(ngrams.most_common(20))
            for i in ngrams.most_common(10):
                print('String : {} \n'.format(i), getSentenceCount(i[0], content))
            wo.wc_run(ngrams.most_common(70))
        except pymysql.err.OperationalError as e:
            print(e)
            print('Server Password Error')

    # -------------------------------------------------------------------
    # ---------- Start Ngram Summary System : low System ----------------
    elif args.nsum == 'start':
        try:
            cond_text = cond_Query()
            content = server_Query(cond_text)
            cont = get_text_ratio(content)
            content = summary_clean_sentence(str(cont))
            ngrams = getNgrams(content, 3)

            print(ngrams.most_common(20))

            for i in ngrams.most_common(10):
                sentence = getSentenceCount(i[0], content)
                summary = sm.fugging_summary(sentence)
                print('String : {} \n'.format(i), getSentenceCount(i[0], content))
                print('String : {} \n'.format(i), summary)
        except pymysql.err.OperationalError as e:
            print(e)
            print('Server Password Error')

    # ----------------------------------------------------------------
    # ---------- Translate Ngram System : low time system ------------
    elif args.nj == 'start':

        try:
            cond_text = cond_Query()
            content = server_Query(cond_text)
            cont = get_text_ratio(content)
            content = summary_clean_sentence(str(cont))
            ngrams = getNgrams(content, 3)

            for i in ngrams.most_common(10):
                sentence = getSentenceCount(i[0], content)
                generate, tokenizer = ht.fugging_translation(sentence)
                translation = ht.translate_decode(tokenizer, generate)
                print('String : {} \n'.format(i), translation)
        except pymysql.err.OperationalError as e:
            print(e)
            print('Server Password Error')

    # -------------------------------------------------------------------
    # ---------- Start Summary System -----------------------------------
    elif args.ns == 'start':
        print("======== Test System ========")

        cond_text = cond_Query()
        cont = server_Query(cond_text)
        cont = get_text_ratio(cont)
        #content = content[:-160]  # content[:-160]
        content = summary_clean_sentence(str(cont))

        ngrams = getNgrams(content, 1)
        key = ngrams.most_common(1)[0][0].lower()

        wordDict = buildDict(content)

        length = 500
        chain = [key]

        for i in range(0, length):
            newWord = randomWord(wordDict[chain[-1]])
            chain.append(newWord)

        text = ' '.join(chain)
        summary = sm.fugging_summary(text)
        print("English : ", summary)
        generate, tokenizer = ht.fugging_translation(summary)
        translation = ht.translate_decode(tokenizer, generate)
        print("Japanese : ", translation)




