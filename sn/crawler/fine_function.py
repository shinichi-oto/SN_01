import re
import os
import string
import pymysql

from random import randint
from collections import Counter


if os.name == 'nt':
    conn = pymysql.connect(host='127.0.0.1', port=3306,
                           user='root', password='<PASSWORD>',
                           db='mysql', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute('USE webscraping')
elif os.name == 'posix':
    conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock',
                           user='root', password='PASSWORD',
                           db='mysql', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute('USE webscraping')


def isCommon(ngram):
    commonWords = ['THE', 'BE', 'AND', 'OF', 'A', 'IN', 'TO', 'HAVE', 'IT', 'I', 'THAT', 'FOR', 'YOU',
                   'HE', 'WITH', 'ON', 'DO', 'SAY', 'THIS', 'THEY', 'IS', 'AN', 'AT', 'BUT', 'WE', 'HIS',
                   'FROM', 'THAT', 'NOT', 'BY', 'SHE', 'OR', 'AS', 'WHAT', 'GO', 'THEIR', 'CAN', 'WHO',
                   'GET', 'IF', 'WOULD', 'HER', 'ALL', 'MY', 'MAKE', 'ABOUT', 'KNOW', 'WILL', 'AS', 'UP',
                   'ONE', 'TIME', 'HAS', 'BEEN', 'THERE', 'YEAR', 'SO', 'THINK', 'WHEN', 'WHICH', 'THEM',
                   'SOME', 'ME', 'PEOPLE', 'TAKE', 'OUT', 'INTO', 'JUST', 'SEE', 'HIM', 'YOUR', 'COME',
                   'COULD', 'NOW', 'THAN', 'LIKE', 'OTHER', 'HOW', 'THEN', 'ITS', 'OUR', 'TWO', 'MORE',
                   'THESE', 'WANT', 'WAY', 'LOOK', 'FIRST', 'ALSO', 'NEW', 'BECAUSE', 'DAY', 'MORE', 'USE',
                   'NO', 'MAN', 'FIND', 'HERE', 'THING', 'GIVE', 'MANY', 'WELL', 'FREE', 'REUTERS', 'APRIL',  # 'WELL'
                   'DEFENSEAUTOS', 'INDEXBROWSEWORLDBUSINESSLEGALMARKETSBREAKINGVIEWSTECHNOLOGYINVESTIGATIONSLIFESTYLEABOUT',
                   '2022LOAD', 'USEPRIVACYDIGITAL', 'REUTERSABOUT', 'NEEDS.CHECKPOINTTHE', 'VIDEOREUTERS',
                   'CHIEF', 'AGENCYBRAND', 'ATTRIBUTION', 'GUIDELINESREUTERS', 'NEWS', 'KINGDOMSTOCKSENERGYAMERICASMIDDLE',
                   '2022SPORTSGALLERYSPORTSKENYANS', 'AGOSPORTSTENNIS', '2022GALLERYMIDDLE', 'PHARMACEUTICALSCHINAUNITED',
                   'KINGDOMSTOCKSENERGYAMERICASMIDDLE', 'EASTFINANCEAFRICAAEROSPACE', 'TRANSPORTATIONMEDIA',
                   'TELECOMENVIRONMENTCURRENCIESINDIACOMMODITIESRETAIL', 'LEADERSHIPREUTERS', 'CHECKREUTERS',
                   'INFORMEDDOWNLOAD', 'LARGEST', 'MULTIMEDIA', 'NEWS', 'PROVIDER', 'ATTORNEY-EDITOR', 'PROVIDES',
                   'STRONGEST', 'ARGUMENT', 'RELYING', 'AUTHORITATIVE', 'CONTENT', 'TECHNOLOGY.ONESOURCETHE',
                   'FEEDBACKALL', 'HIGHLY-CUSTOMISED', 'WORKFLOW', 'EXPERIENCE', 'FINANCE', 'PROFESSIONALS.REFINITIV',
                   'PRODUCTSREFINITIV', 'BUSINESS', 'FINANCIAL', 'NATIONAL', 'TRANSPORTATIONENERGYENVIRONMENTFINANCEHEALTHCARE',
                   'PHARMACEUTICALSMEDIA', 'TELECOMRETAIL', 'MOST', 'COMPREHENSIVE', 'SOLUTION', 'HISTORICAL',
                   'MARKET', 'DATA', 'PHARMACEUTICALSMEDIA', 'TELECOMRETAIL', 'CONSUMERSUSTAINABLE',
                   'TELECOMRETAIL', 'CONSUMERSUSTAINABLE', 'BUSINESSCHARGEDFUTURE', 'SUMMARY', 'CONFIDENTIALITY',
                   'PROFESSIONALS', 'VIA', 'DESKTOP', 'MEDIA', 'ORGANIZATIONS', 'WORKSPACE', 'ACCESS', 'UNMATCHED',
                   'TRUST', 'PRINCIPLES', 'MARCH', 'HEIGHTENED', 'RISK', 'INDIVIDUAL', 'UNCOVER', 'HIDDEN', 'RISKS',
                   'REGISTER', 'GREGORIOOUR', 'REUTERS.COMREGISTERREPORTING', 'ARE', 'GENERATED', 'AUTOMATICALLY',
                   'GENERATED', 'AUTOMATICALLY', 'BASED', 'LAW', 'FIRM', 'NAMES', 'SHOWN', 'ABOVE', 'FREE',
                   'UNLIMITED', 'ACCESS', 'REUTERS.COMREGISTERPALM', 'MONTHS.REGISTER', 'REUTERS.COMREGISTERIN',
                   'REUTERS.COMREGISTERADDITIONAL', 'REUTERS', 'REUTERS.COMREGISTERREPORTING', 'THOMSON', 'CO', 'INC']
    for word in ngram:
        if word in commonWords:
            return True
    return False


def cleanDataSentence(sentence):
    sentence = sentence.split(' ')
    sentence = [word.strip(string.punctuation + string.whitespace)
                for word in sentence]
    sentence = [word for word in sentence if len(word) > 1
                or (word.lower() == 'a' or word.lower() == 'i')]
    return sentence


def cleanDataInput(content):
    content = content.upper()
    content = re.sub('\n', ' ', content)
    content = bytes(content, "UTF-8")
    content = content.decode("ascii", "ignore")
    sentences = content.split('. ')
    return [cleanDataSentence(sentence) for sentence in sentences]


def getNgramsSentence(content, n):
    output = []
    for i in range(len(content) - n + 1):
        if not isCommon(content[i:i + n]):
            output.append(content[i:i + n])
    return output


def getNgrams(content, n):
    content = cleanDataInput(content)
    ngrams = Counter()
    ngrams_list = []
    for sentence in content:
        newNgrams = [' '.join(ngram) for ngram in
                     getNgramsSentence(sentence, n)]
        ngrams_list.extend(newNgrams)
        ngrams.update(newNgrams)
    return (ngrams)


def getSentenceCount(ngram, count):
    sentences = count.upper().split(". ")
    for sentence in sentences:
        if ngram in sentence:
            return sentence + '\n'
    return


def listSum(wordList):
    sum = 0
    for word, value in wordList.items():
        sum += value
    return sum


def randomWord(wordList):
    randIndex = randint(1, listSum(wordList))
    for word, value in wordList.items():
        randIndex -= value
        if randIndex <= 0:
            return word


def buildDict(text):
    text = text.replace('\n', ' ')
    text = text.replace('"', '')
    punctuation = [',', '.', ';', ':']
    for symbol in punctuation:
        text = text.replace(symbol, ' {} '.format(symbol))

    words = text.split(' ')
    words = [word for word in words if word != '']

    wordDict = {}
    for i in range(1, len(words)):
        if words[i - 1] not in wordDict:
            wordDict[words[i-1]] = {}
        if words[i] not in wordDict[words[i-1]]:
            wordDict[words[i-1]][words[i]] = 0
        wordDict[words[i-1]][words[i]] += 1
    return wordDict


def summary_clean_sentence(text: str):
    clean = re.sub(r'[\\:;)(]', '', text)
    clean = re.sub(r'/', ' ', clean)
    return clean


def year_month_day_search():
    while True:
        year = input('Input Year >>> ')
        if year.isdecimal():
            if len(year) == 4:
                print(f'Input Year: {year}')
                year = int(year)
                break
            else:
                print('Input Error : 0000')
        else:
            print(f'{year} is not Decimal')
    while True:
        month = input('Input Month >>> ')
        if month.isdecimal():
            if len(month) == 2:
                print(f'Input Month: {month}')
                month = int(month)
                break
            else:
                print('Input Error : 00')
        else:
            print(f'{month} is not Decimal')
    while True:
        day = input('Input Day >>> ')
        if day.isdecimal():
            if len(day) == 2:
                print(f'Input Day: {day}')
                day = int(day)
                break
            else:
                print('Input Error : 00')
        else:
            print(f'{day} is not Decimal')

    return year, month, day


def year_month_day_y():
    while True:
        year = input('Input Year >>> ')
        if year.isdecimal():
            if len(year) == 4:
                print(f'Input Year: {year}')
                break
            else:
                print('Input Error : 0000')
        else:
            print(f'{year} is not Decimal')

    return year


def year_month_day_ym():
    while True:
        year = input('Input Year >>> ')
        if year.isdecimal():
            if len(year) == 4:
                print(f'Input Year: {year}')
                break
            else:
                print('Input Error : 0000')
        else:
            print(f'{year} is not Decimal')
    while True:
        month = input('Input Month >>> ')
        if month.isdecimal():
            if len(month) == 2:
                print(f'Input Month: {month}')
                break
            else:
                print('Input Error : 00')
        else:
            print(f'{month} is not Decimal')

    return year, month


def year_month_day_ymd():
    while True:
        year = input('Input Year >>> ')
        if year.isdecimal():
            if len(year) == 4:
                print(f'Input Year: {year}')
                break
            else:
                print('Input Error : 0000')
        else:
            print(f'{year} is not Decimal')
    while True:
        month = input('Input Month >>> ')
        if month.isdecimal():
            if len(month) == 2:
                print(f'Input Month: {month}')
                break
            else:
                print('Input Error : 00')
        else:
            print(f'{month} is not Decimal')
    while True:
        day = input('Input Day >>> ')
        if day.isdecimal():
            if len(day) == 2:
                print(f'Input Day: {day}')
                break
            else:
                print('Input Error : 00')
        else:
            print(f'{day} is not Decimal')

    return year, month, day


def year_month_day_ymdst():
    while True:
        year = input('Input Year >>> ')
        if year.isdecimal():
            if len(year) == 4:
                print(f'Input Year: {year}')
                break
            else:
                print('Input Error : 0000')
        else:
            print(f'{year} is not Decimal')
    while True:
        month = input('Input Month >>> ')
        if month.isdecimal():
            if len(month) == 2:
                print(f'Input Month: {month}')
                break
            else:
                print('Input Error : 00')
        else:
            print(f'{month} is not Decimal')
    while True:
        day = input('Input Day >>> ')
        if day.isdecimal():
            if len(day) == 2:
                print(f'Input Day: {day}')
                break
            else:
                print('Input Error : 00')
        else:
            print(f'{day} is not Decimal')
    while True:
        st = input('Input NOT LIKE string >>> ')
        if st.isalpha():
            print(f'Input Query String {st}')
            break
        else:
            print(f'{st} is NOT String')

    return year, month, day, st


def cond_Query():
    while True:
        cond_text = input('(ymd)-(ym)-(y)-(st) : >>> ')
        if cond_text.isalpha():
            if cond_text == 'ymd':
                print(f'Input Conditions : {cond_text}')
                cond_text = str(cond_text)
                break
            elif cond_text == 'ym':
                print(f'Input Conditions : {cond_text}')
                cond_text = str(cond_text)
                break
            elif cond_text == 'y':
                print(f'Input Conditions : {cond_text}')
                cond_text = str(cond_text)
                break
            elif cond_text == 'st':
                print(f'Input Conditions : {cond_text}')
                cond_text = str(cond_text)
                break
            else:
                print('Input Error : (ymd)-(ym)-(y)-(st)')
        else:
            print(f'{cond_text} is not alpha(string)')
    return cond_text


def server_Query(ac):
    global content
    if ac == 'ymd':
        print('ymd test')
        f_year_ymd, f_month_ymd, f_day_ymd = year_month_day_ymd()
        cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_ymd}-{f_month_ymd}-{f_day_ymd}%'"
                    f" AND content NOT LIKE 'skip%'")  # 年月日
        content = cur.fetchall()
    elif ac == 'ym':
        print('ym test')
        f_year_ym, f_month_ym = year_month_day_ym()
        cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_ym}-{f_month_ym}%'"
                    f" AND content NOT LIKE 'skip%'")  # 年月
        content = cur.fetchall()
    elif ac == 'y':
        print('y test')
        f_year_y = year_month_day_y()
        cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_y}%'"
                    f" AND content NOT LIKE 'skip%'")  # 年
        content = cur.fetchall()
    elif ac == 'st':
        print('st test')
        f_year_ymdst, f_month_ymdst, f_day_ymdst, f_st_ymdst = year_month_day_ymdst()
        cur.execute(f"SELECT content FROM website WHERE url LIKE '%{f_year_ymdst}-{f_month_ymdst}-{f_day_ymdst}%'"
                    f" AND content NOT LIKE '{f_st_ymdst}%'")
        content = cur.fetchall()
    return content


def get_text_ratio(content):
    cont = []
    for text in content:
        text = text[0]
        all_text = len(text)
        all_ratio = int(all_text * 0.15)
        sp_text = text[:-all_ratio]
        cont.append(sp_text)
    return cont
