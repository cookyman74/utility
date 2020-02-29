import re
from imbox import Imbox


class MyMailBox(Imbox):
    def __init__(self, server, port, userid, passwd, ssl=False):
        self.imbox = None
        if server:
            self.server = server
        else:
            self.server = 'imap.google.com'

        if port:
            self.port = port
        else:
            self.port = 993

        self.userid = userid
        self.passwd = passwd
        self.ssl = ssl

    # 메일박스 디렉토리 파싱함수
    def parse_list_response(self, line):
        list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
        match = list_response_pattern.match(line.decode('utf-8'))

        flags, delimiter, mailbox_name = match.groups()
        mailbox_name = mailbox_name.strip('"')

        return (flags, delimiter, mailbox_name)

    # 메일박스 디렉토리 리스트 출력 및 선택 함수
    def mail_dir_select(self):
        maildir=[]
        status, data = self.imbox.folders()
        if status != 'OK':
            print("ERROR: fail to show mail box list")
        for line in data:
            flags, delimiter, mailbox_name = self.parse_list_response(line)
            if bool(re.match('[a-zA-Z0-9].*', mailbox_name)):
                maildir.append(mailbox_name)
        return maildir

    # imapconnect
    def imap_connect(self):
        server = self.server
        userid = self.userid
        passwd = self.passwd
        port = self.port
        ssl = self.ssl

        try:
            self.imbox = Imbox(
                server, port=port, username=userid, password=passwd, ssl=ssl, ssl_context=None, starttls=False)
        except Exception as e:
            print(e)
            raise SystemExit

