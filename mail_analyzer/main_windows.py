import sys
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import font_manager, rc

from collections import Counter
from konlpy.tag import Twitter
from wordcloud import WordCloud

from mymailbox import MyMailBox


def draw_time_graph():
    font_fname = 'C:\\Users\\cooky\\AppData\\Local\\Microsoft\\Windows\\Fonts\\D2CodingBold.ttf'  # A font of your choice
    font_name = font_manager.FontProperties(fname=font_fname).get_name()
    rc('font', family=font_name)

    wc = WordCloud(font_path=font_fname, background_color='white', width=800, height=600)

    sql = """
    select word, sum(count) from words_statistics
    group by word
    order by sum(count) desc limit 1000
    """
    cursor.execute(sql)
    rows = cursor.fetchall()

    rows = dict(rows)

    cloud = wc.generate_from_frequencies(rows)
    cloud.to_file("wordscloud222.png")


class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()

    def draw_time_graph(self):
        sql_time = """
                            select substr(time, 1,2), count(*) from mail_info
                            where time not like '+%' and time not like '-%'
                            group by substr(time, 1,2) 
                        """
        cursor.execute(sql_time)
        data = cursor.fetchall()

        x = [list[0] for list in data]
        y = [list[1] for list in data]

        ax = self.fig.add_subplot(111)
        ax.plot(x, y)
        self.canvas.draw()

    def draw_week_graph(self):
        sql_week = """
                    select weekends, count(*) from mail_info
                    where weekends like "%,"
                    group by weekends 
                """
        cursor.execute(sql_week)
        data = cursor.fetchall()

        x = [list[0] for list in data]
        y = [list[1] for list in data]

        ax = self.fig2.add_subplot(111)
        ax.plot(x, y)
        self.canvas2.draw()

    def setupUI(self):
        self.setGeometry(600, 200, 1200, 800)
        self.setWindowTitle("MailAnalyzer Viewer v0.1")
        self.setWindowIcon(QIcon('icon.png'))

        # 탭 스크린 설정
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300, 200)

        # 탭 추가
        self.tabs.addTab(self.tab1, "Time Graph")
        self.tabs.addTab(self.tab2, "Week Graph")
        self.tabs.addTab(self.tab3, "Word Cloud")

        idLabel = QLabel("ID: ")
        pwLabel = QLabel("PW: ")
        serverLabel = QLabel("IMAP서버: ")
        portLabel = QLabel("포트주소: ")
        sslLabel = QLabel("SSL: ")

        self.idEdit = QLineEdit()
        self.pwEdit = QLineEdit()
        self.serverEdit = QLineEdit()
        self.portEdit = QLineEdit()
        self.sslCheck = QCheckBox()

        self.pushButton = QPushButton("로그인")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        serverLayout = QGridLayout()
        serverLayout.addWidget(serverLabel, 0, 0)
        serverLayout.addWidget(self.serverEdit, 0, 1)
        serverLayout.addWidget(portLabel, 1, 0)
        serverLayout.addWidget(self.portEdit, 1, 1)
        serverLayout.addWidget(sslLabel, 2, 0)
        serverLayout.addWidget(self.sslCheck, 2, 1)

        serverBox = QGroupBox("메일서버정보")
        serverBox.setLayout(serverLayout)
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(serverBox)

        loginLayout = QGridLayout()
        loginLayout.addWidget(idLabel, 0, 0)
        loginLayout.addWidget(self.idEdit, 0, 1)
        loginLayout.addWidget(pwLabel, 1, 0)
        loginLayout.addWidget(self.pwEdit, 1, 1)
        loginLayout.addWidget(self.pushButton, 2, 0)

        loginBox = QGroupBox("로그인 계정정보")
        loginBox.setLayout(loginLayout)
        leftLayout.addWidget(loginBox)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

        self.fig2 = plt.Figure()
        self.canvas2 = FigureCanvas(self.fig2)

        # self.fig3 = plt.Figure()
        # self.canvas3 = FigureCanvas(self.fig3)
        self.fig3 = QLabel()
        # self.canvas3 = FigureCanvas(self.fig3)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)

        self.tab1.layout = QVBoxLayout()
        self.tab1.layout.addWidget(self.canvas)
        self.tab1.layout.addWidget(self.progress)
        self.tab1.setLayout(self.tab1.layout)

        self.tab2.layout = QVBoxLayout()
        self.tab2.layout.addWidget(self.canvas2)
        self.tab2.setLayout(self.tab2.layout)

        self.tab3.layout = QVBoxLayout()
        self.tab3.layout.addWidget(self.fig3)
        self.tab3.setLayout(self.tab3.layout)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addWidget(self.tabs)
        layout.setStretchFactor(leftLayout, 0)
        layout.setStretchFactor(self.tabs, 1)

        self.setLayout(layout)

    def pushButtonClicked(self):

        server = self.serverEdit.text()
        userid = self.idEdit.text()
        passwd = self.pwEdit.text()
        ssl = self.sslCheck.isChecked()
        port = self.portEdit.text()

        try:
            mailbox = MyMailBox(server, port=port, userid=userid, passwd=passwd, ssl=ssl)
            mailbox.imap_connect()
            imbox = mailbox.imbox
        except Exception as e:
            print("오류",e)

        mailbox_dir = mailbox.mail_dir_select()
        item, ok = QInputDialog.getItem(self, "선택", "메일박스를 선택하세요.", mailbox_dir, 0, False)

        if ok and item:
            message_list = imbox.messages(folder=item)
            print(message_list)

        h = Twitter()
        fullcount = len(message_list)

        progress_count = 0

        for uid, msg in message_list:
            progress_count += 1
            progress = (progress_count / fullcount) * 100
            try:
                self.progress.setValue(progress)
            except Exception as e:
                print(e)
                continue

            try:
                body = msg.body.get('plain')[0]
                sent_from_name = msg.sent_from[0].get('name')
                sent_from_email = msg.sent_from[0].get('email')
                sent_to_count = len(msg.sent_to)
                subject = msg.subject
                receive_date = msg.date.split(" ")
                weekends = receive_date[0]
                eday = receive_date[2]
                emonth = receive_date[1]
                eyear = receive_date[3]
                etime = receive_date[4]
            except Exception as e:
                print("추출오류(%s)" % uid, e)
                continue

            try:
                sql = """ INSERT INTO mail_info (mailserver, uid, body, sent_from_name, sent_from_email, sent_to_count, subject,
                                                    weekends, day, month, year, time)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """

                cursor.execute(sql, (server, uid, body, sent_from_name, sent_from_email, sent_to_count, subject,
                                     weekends, eday, emonth, eyear, etime))

                nouns = h.nouns(body)
                count = Counter(nouns)

                for n, c in count.most_common(100):
                    sql_insert = "INSERT INTO words_statistics(mailserver, word, count) VALUES (?, ?, ?)"
                    sql_update = "UPDATE words_statistics set count = count + ? where word = ? and mailserver = ?"
                    try:
                        cursor.execute(sql_insert, (server, n, c))
                    except Exception as e:
                        print("단어DB저장오류", e)
                        try:
                            cursor.execute(sql_update, (n, c, server))
                        except Exception as e:
                            print(e)
                            continue

                db.commit()
            except Exception as e:
                print("입력오류", e)
                continue

        self.draw_time_graph()
        self.draw_week_graph()
        try:
            draw_time_graph()
            pxmap = QPixmap("wordscloud222.png")
            self.fig3.setPixmap(pxmap)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    db = sqlite3.connect("test.db")
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mail_info(
            mailserver VARCHAR(50),
            uid INT UNIQUE,
            subject VARCHAR(300),
            body VARCHAR(1000),
            sent_from_name VARCHAR(10),
            sent_from_email VARCHAR(30),
            sent_to_count INT,
            weekends VARCHAR(10),
            day VARCHAR(2),
            month VARCHAR(2),
            year VARCHAR(4),
            time VARCHAR(10)
            )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS words_statistics(
            mailserver VARCHAR(50),
            word VHARCHAR(20) UNIQUE,
            count INT
            )
        """
    )

    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()

    db.close()