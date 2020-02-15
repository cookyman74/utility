import getpass
import os, re
import imaplib
import email.header
import email.parser
from email.header import decode_header
from datetime import datetime


# 메일 대상 서버 config 설정 입니다.
# 메일 선택 함수
def mail_config_select(txt):
    mail_server_list = {
        1: ['imap.gmail.com', 993, True],
        2: ['imap.naver.com', 993, True],
        3: ['imap.daum.net', 993, True],
    }
    for i in range(len(mail_server_list)):
         print(u"[%d] %s 서버" % (i+1, mail_server_list[i+1][0]))
    selected_num = input(txt)
    return mail_server_list.get(int(selected_num))


# 메일박스 디렉토리 파싱함수
def parse_list_response(line):
    list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
    match = list_response_pattern.match(line.decode('utf-8'))
    flags, delimiter, mailbox_name = match.groups()
    mailbox_name = mailbox_name.strip('"')

    return (flags, delimiter, mailbox_name)


# 메일박스 디렉토리 리스트 출력 및 선택 함수
def mail_dir_select(mail_session, txt):
    maildir=[]
    i = 0
    status, data = mail_session.list()
    if status != 'OK':
        print("ERROR: fail to show mail box list")
    for line in data:
        flags, delimiter, mailbox_name = parse_list_response(line)
        if bool(re.match('[a-zA-Z0-9].*', mailbox_name)):
            i +=1
            maildir.append(mailbox_name)
            print("[%d] %s" % (i, mailbox_name))

    selected_num = input(txt)
    # selected_num = 3
    return maildir[int(selected_num)-1]


if __name__ == "__main__":
    detach_dir = '.'
    if 'attachments' not in os.listdir(detach_dir):
        os.mkdir('attachments')

    mail_server = mail_config_select("Select your Mail: ")
    userName = input("Mail ID: ")
    passwd = getpass.getpass(prompt="Password: ", stream=None)

    # 메일서버의 SSL지원 여부에 따라 imap 보안 모드를 선택합니다.
    if mail_server[2]:
        mail_session = imaplib.IMAP4_SSL(mail_server[0], mail_server[1])
    else:
        mail_session = imaplib.IMAP4(mail_server[0], mail_server[1])

    typ, accountDetails = mail_session.login(userName, passwd)
    if typ != 'OK':
        print("Error Authentication failed")
        raise SystemExit

    mail_box_dir = mail_dir_select(mail_session, "select mail box: ")

    # 입력된 메일박스를 선택합니다.
    mail_session.select('INBOX')
    #
    # # 이메일 검색 : 각 메일에는 UID가 있다
    # # 명령: 검색(여기서는 전체), 리턴은 결과와 데이터
    # result, data = mail_session.uid('search', None, "ALL")
    # last_email_uid = data[0].split()[-1]
    # result, data = mail_session.uid('fetch', last_email_uid, '(RFC822)')
    # raw_email = data[0][1]
    # # email_message = email.message_from_string(raw_email.decode('utf-8'))
    # msg = email.parser.BytesParser().parsebytes(raw_email)
    # email_message = email.message_from_bytes(raw_email)
    # print(email_message['To'])
    # print(email.utils.parseaddr(email_message['From']))
    # print(email_message.keys())
    # import base64
    # print(email_message.get('Subject', "안되네"))

    """
    from imbox import Imbox

    with Imbox('imap.naver.com',
               username='',
               password='',
               ssl=True,
               ssl_context=None,
               starttls=False) as imbox:
        all_inbox_messages = imbox.messages()
        for uid, message in all_inbox_messages:
            for attach in message.attachments:
                if not attach:
                    continue
                print(attach.get('filename'), uid)
                print(dir(imbox))
    """

    # 메일을 검색합니다.
    mail_session.literal = u"테스트".encode('utf-8')
    typ, data = mail_session.uid('SEARCH', 'CHARSET', 'UTF-8', 'SUBJECT')
    if typ != 'OK':
        print('Error searching Inbox.')
        raise SystemExit

    # 모두 검색된 메일 데이터를 분해하여 메세지 파트를 출력합니다.
    for msgId in data[0].split():
        typ, messageParts = mail_session.uid('fetch', msgId, '(RFC822)')
        if typ != 'OK':
            print('Error fetching mail.')
            raise SystemExit

        raw_emailbody = messageParts[0][1]
        mail = email.message_from_bytes(raw_emailbody)

        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                # print part.as_string()
                continue
            if part.get('Content-Disposition') is None:
                # print part.as_string()
                continue

            print(part.keys())

            try:    
                print(decode_header(part.get('Subject', None)))
            except Exception as e:
                print("파일명오류",e)
                
            fileName = part.get_filename()
            try:
                print(decode_header(fileName)[0][0])
            except Exception as e:
                print(fileName, e)

            if fileName:
                bytes, encoding = decode_header(fileName)[0]
                if encoding:
                    fileName = bytes.decode(encoding)
                else:
                    #파일명을 decoding하지 못하는 경우
                    fileName = "mail_attached_file_%s" % datetime.today().strftime("%Y%m%d%H%M%S")

            if bool(fileName):
                filePath = os.path.join(detach_dir, 'attachments', fileName)
                if not os.path.isfile(filePath):
                    print(fileName)
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
    mail_session.close()
    mail_session.logout()
    #
