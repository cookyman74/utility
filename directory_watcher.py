import time, smtplib
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
from email.mime.text import MIMEText


def send_mail(title, body):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login('cookyman@gmail.com', 'ihpqblanckrdrjcn')

    msg = MIMEText(body)
    msg['Subject'] = title
    smtp.sendmail('cookyman@gmail.com', 'emro25784251@s-oil.com', msg.as_string())
    smtp.quit()


class Handler(RegexMatchingEventHandler):

    def __init__(self):
        super(Handler, self).__init__(ignore_regexes=[
            '^[.]{1}.*', '.*/[.]{1}.*', '.*~\$.*', '.*\.tmp.*'], ignore_directories=False)

    def on_closed(self, event):
        print(event)

    def file_type(self, event):
        title = '공유 폴더에 파일이'
        if event.is_directory:
            title = '공유 폴더가 '
        result = '%s 변경(삭제/추가) 되었습니다.' % title
        return result

    def on_modified(self, event):
        mail_title = self.file_type(event)
        mail_body = event.src_path
        send_mail(mail_title, mail_body)

    def on_created(self, event):
        mail_title = self.file_type(event)
        mail_body = event.src_path
        send_mail(mail_title, mail_body)


class Watcher:
    DIRECTORY_TO_WATCH = 'z:\\'

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


if __name__ == '__main__':
    w = Watcher()
    w.run()