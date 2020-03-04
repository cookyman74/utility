import sqlite3
import sys
import os

path = ""
if "linux" in sys.platform.lower():
    path = "~/.config/google-chrome/Default/History"
if "darwin" in sys.platform.lower():
    path = "~/Library/Application Support/Google/Chrome/Default/History"
if "win32" in sys.platform.lower():
    path = "~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
path = os.path.expanduser(path)

conn = sqlite3.connect(path)
cur = conn.cursor()

result = True

id = 0
ids = []
RESULT = True

while RESULT:
    RESULT = False
    print("1. URL에서 검색하기")
    print("2. 사이트 Title에서 검색하기")
    print("3. URL, Title에 포함된 모든 항목 검색하기")
    option = int(input("검색옵션을 선택해주세요(1 ~ 3)"))
    search_url = input("삭제하고 싶은 단어를 작성해주세요?")
    print("=" * 50)

    if option == 1:
        sql = f"select id, title, url FROM urls WHERE url LIKE '%{search_url}%'"
    elif option == 2:
        sql = f"select id, title, url FROM urls WHERE title LIKE '%{search_url}%'"
    else:
        sql = f"select id, title, url FROM urls WHERE url LIKE '%{search_url}%' or title LIKE '%{search_url}%'"

    for row in cur.execute(sql):
        print(row)
        id = row[0]
        ids.append((id,))

    print("=" * 50)
    confirm = input("삭제목록이 맞습니까?(Y or N)")
    if confirm == "Y" or confirm == "y":
        cur.executemany('DELETE FROM urls WHERE id=?', ids)
        conn.commit()
        print("검색된 항목을 모두 삭제하였습니다.")
    elif confirm == "N" or confirm == "n":
        print("취소하였습니다.(다시 돌아갑니다.)")
        RESULT = True
    else:
        print("잘못눌렀거나 취소하였습니다.")
        raise SystemExit

conn.close()