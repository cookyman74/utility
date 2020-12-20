import getpass
import os, re
import calendar
from imbox import Imbox
import imaplib
import zipfile
from datetime import datetime

# 메일 대상 서버 config 설정 입니다.
# 메일 선택 함수
def mail_config_select(txt):
    mail_server_list = {
        1: ['imap.gmail.com', 993, True],
        2: ['imap.naver.com', 993, True],
        3: ['imap.daum.net', 993, True],
        4: ['outlook.office365.com', 993, True],
    }
    for i in range(len(mail_server_list)):
         print(u"[%d] %s 서버" % (i+1, mail_server_list[i+1][0]))
    selected_num = input(txt)
    return mail_server_list.get(int(selected_num), None)


# 메일박스 디렉토리 파싱함수
def parse_list_response(line):
    list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
    match = list_response_pattern.match(line.decode('utf-8'))

    flags, delimiter, mailbox_name = match.groups()
    mailbox_name = mailbox_name.strip('"')

    return (flags, delimiter, mailbox_name)


# 메일박스 디렉토리 리스트 출력 및 선택 함수
def mail_dir_select(imbox, txt):
    maildir={}
    i = 0
    status, data = imbox.folders()
    if status != 'OK':
        print("ERROR: fail to show mail box list")
    for line in data:
        flags, delimiter, mailbox_name = parse_list_response(line)
        if bool(re.match('[a-zA-Z0-9].*', mailbox_name)):
            i +=1
            maildir[i] = mailbox_name
            print("[%d] %s" % (i, mailbox_name))
    print("[%d] 전체 메일함" % (i + 1))

    selected_num = input(txt)
    result = maildir.get(int(selected_num), 0)

    if result == 0:
        print(maildir)
        return [v for i, v in maildir.items()]
    else:
        return result


if __name__ == "__main__":

    mail_server = mail_config_select("Select your Mail: ")
    if mail_server:
        userName = input("Mail ID: ")
        passwd = getpass.getpass(prompt="Password: ", stream=None)
    else:
        print("선택값 오류 입니다")
        raise SystemExit

    detach_dir = '.'
    if mail_server[0] not in os.listdir(detach_dir):
        os.mkdir(mail_server[0])

    cal = dict((v, k) for k, v in enumerate(calendar.month_abbr))
    with Imbox(mail_server[0],
               username=userName,
               password=passwd,
               ssl=mail_server[2],
               ssl_context=None,
               starttls=False) as imbox:

        status, folder_list = imbox.folders()
        mail_box_dir = mail_dir_select(imbox, "select mail box: ")

        # if mail_box_dir:
        #     folder_messages = imbox.messages(folder=mail_box_dir)
        # else:
        #     folder_messages = imbox.messages()

        for message_box in mail_box_dir:
            print("메세지박스: ", message_box)
            folder_messages = imbox.messages(folder=message_box)
            for uid, message in folder_messages:
                try:
                    email_datetime = message.date.split(" ")

                    day = email_datetime[1]
                    month = cal.get(email_datetime[2])
                    year = email_datetime[3]
                except:
                    day = "DD"
                    month = "MM"
                    year = "YYYY"

                if message.attachments:
                    print("첨부파일 날짜: ", message.date)
                    for list in message.attachments:
                        if not list:
                            continue

                        filename = str(year)+"."+str(month)+"."+str(day)+"_"+str(list.get('filename'))
                        fileFullPath = os.path.join(detach_dir, mail_server[0], filename)
                        raw_report = list['content'].read()
                        f = open(fileFullPath, 'wb')
                        f.write(raw_report)
                        f.close()
