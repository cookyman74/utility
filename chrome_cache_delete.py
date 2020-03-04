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
    search_url = input("삭제하고 싶은 URL에 포함된 단어를 써주세요?")
    for row in cur.execute(f"select id, url FROM urls WHERE url LIKE '%{search_url}%'"):
        print(row)
        id = row[0]
        ids.append((id,))

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