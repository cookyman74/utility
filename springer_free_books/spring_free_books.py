import sqlite3
import os
import argparse
import pandas as pd
from helper import *

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--folder', help='folder to store downloads')

parser.add_argument(
    '-i','--init', action='store_true', help='init database'
)

parser.add_argument(
    '-v','--verbose', action='store_true', help='show more details'
)

args = parser.parse_args()
folder = create_path(args.folder if args.folder else '.\downloads')

if args.init == True:
    os.remove('freebook.db')

conn = sqlite3.connect('freebook.db')
cs = conn.cursor()

table_url = 'https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4'
table = 'table_' + table_url.split('/')[-1] + '.xlsx'
table_path = os.path.join('./', table)

if not os.path.exists(table_path):
    books = pd.read_excel(table_url)
    # Save table in the download folder
    books.to_excel(table_path)
else:
    books = pd.read_excel(table_path, index_col=0, header=0)

header = books.columns.tolist()
contents = books.values.tolist()

query = f''' CREATE TABLE IF NOT EXISTS "FREE_BOOKS" (
        "{header[0]}" TEXT,
        "{header[1]}" TEXT,
        "{header[2]}" TEXT,
        "{header[3]}" TEXT,
        "{header[4]}" TEXT,
        "{header[5]}" TEXT,
        "{header[6]}" TEXT,
        "{header[7]}" TEXT,
        "{header[8]}" TEXT,
        "{header[9]}" TEXT,
        "{header[10]}" TEXT,
        "{header[11]}" TEXT,
        "{header[12]}" TEXT,
        "{header[13]}" TEXT,
        "{header[14]}" TEXT,
        "{header[15]}" TEXT,
        "{header[16]}" TEXT,
        "{header[17]}" TEXT,
        "{header[18]}" TEXT,
        "{header[19]}" TEXT,
        "{header[20]}" TEXT,
        "{header[21]}" TEXT
        )'''

cs.execute(query)
conn.commit()

def column_select(HEADER, a, b):
    text=""
    for i in range(a, b):
        text += '"'+HEADER[i]+'",'
    text = text[:-1]
    return text

def insert_value(CONTENTS, a, b, k):
    text = ""
    for i in range(a,b):
        text += '"'+str(CONTENTS[k][i])+'",'
    text = text[:-1]
    return text

data_sql = ''' select count(*) from FREE_BOOKS '''
cs.execute(data_sql)
data_count = cs.fetchone()

if args.init == True or data_count[0] <= 400:
    COLUMN = column_select(header, 0, len(header))

    for i in range(len(contents)):
        VALUES = insert_value(contents, 0, len(header), i)
        query = f'INSERT into FREE_BOOKS ({COLUMN}) values ({VALUES})'
        cs.execute(query)
    conn.commit()
    print("데이터 입력 완료")

R = True
while R:
    R = False
    print("도서의 제목 또는 분류에 포함된 검색할 단어를 입력하세요.")
    words = str(input("검색어: "))
    query_select = f'''
    select "Book Title", "Author", "Edition", "OpenURL", "Print ISBN", "English Package Name" from FREE_BOOKS 
    where "Book Title" like "%{words}%" or "Subject Classification" like "%{words}%" ;
    '''
    results = cs.execute(query_select)

    print("\n")
    print("#다운 받을 항목을 선택해주세요")
    num = 1
    books = []
    for i in results:
        print(f"{num}. "+i[0])
        books.append(i)
        num += 1
    print(f"{num}. 검색결과 모두 다운로드")

    try:
        book_num = int(input("번호선택: "))
        print("\n")
        print("# 다운로드 받을 파일 형식을 선택해주세요")
        print("1. pdf")
        print("2. epub")
        print("3. 모두")
        filetype_num = int(input("번호선택: "))
    except Exception as e:
        print("\n")
        print("*잘못 누르셨습니다.(%s)" % e)
        R = True
        continue

    if book_num > num or book_num < 0 or filetype_num < 0 or filetype_num > 3:
        print("\n")
        print("잘못 입력하였습니다. 종료")
        R = True
        continue

    patches = []
    if filetype_num == 1:
        patches.append({'url': '/content/pdf/', 'ext': '.pdf'})
    elif filetype_num == 2:
        patches.append({'url':'/download/epub/', 'ext':'.epub'})
    else:
        patches.append({'url': '/content/pdf/', 'ext': '.pdf'})
        patches.append({'url':'/download/epub/', 'ext':'.epub'})

book = []
if book_num < num:
    book.append(books[book_num])
    download_books(book, folder, patches)
else:
    download_books(books, folder, patches)