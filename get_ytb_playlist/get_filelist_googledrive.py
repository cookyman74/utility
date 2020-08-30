import pickle
import os
import re
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import requests
from tqdm import tqdm
import sys

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file']


def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # initiate Google Drive service API
    return build('drive', 'v3', credentials=creds)


def get_download_url(id):
    # base URL for download
    URL = "https://docs.google.com/uc?export=download"
    # init a HTTP session
    session = requests.Session()
    # make a request
    response = session.get(URL, params={'id': id}, stream=True)
    return response


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    # get the file size from Content-length response header
    file_size = int(response.headers.get("Content-Length", 0))
    # extract Content disposition from response headers
    content_disposition = response.headers.get("content-disposition")
    # parse filename
    filename = re.findall("filename=\"(.+)\"", content_disposition)[0]
    print("[+] File size:", file_size)
    print("[+] File name:", filename)
    progress = tqdm(response.iter_content(CHUNK_SIZE), f"Downloading {filename}", total=file_size, unit="Byte", unit_scale=True, unit_divisor=1024)
    with open(destination, "wb") as f:
        for chunk in progress:
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                # update the progress bar
                progress.update(len(chunk))
    progress.close()


def search(service, argv):
    # search for the file
    result = {}
    page_token = None

    name = argv[2]
    folder_name = argv[1]
    folder_query = f"name contains '{folder_name}' " \
        f"and mimeType = 'application/vnd.google-apps.folder' " \
        f"and trashed = false"

    while True:
        response = service.files().list(q=folder_query,
                                        spaces="drive",
                                        fields="nextPageToken, files(id, name, mimeType)",
                                        pageToken=page_token).execute()
        # iterate over filtered files
        for folder in response.get("files", []):
            print(f"Found folder: {folder['name']}: {folder['id']}")
            file_query = f"name contains '{name}' and '{folder['id']}' in parents " \
                f"and mimeType != 'application/vnd.google-apps.folder' " \
                f"and trashed = false"
            response = service.files().list(q=file_query,
                                            spaces="drive",
                                            fields="nextPageToken, files(id, name, mimeType)",
                                            pageToken=page_token).execute()

            for file in response.get("files", []):
                download_url = get_download_url(file['id']).url
                url_list = f"<a href={download_url}>{file['name']}</a>"
                # print(f"{url_list}")
                result[file['id']] = [file['name'], url_list]
            page_token = response.get('nextPageToken', None)
        if not page_token:
            # no more files
            break
    return result


def main(argv):
    if len(argv) < 3:
        print("인자값 부족")
        sys.exit(2)
    
    # 구글 드라이브 인증
    service = get_gdrive_service()
    # search for the file by name
    search_result = search(service, argv)
    
    # get the GDrive ID of the file
    for file_id, value in search_result.items():
        file_name = value[0]
        url = value[1]
        # make it shareable
        service.permissions().create(body={"role": "reader", "type": "anyone"}, fileId=file_id).execute()
        # download file
        if len(argv) == 4 and argv[3] == 'down':
            # base URL for download
            URL = "https://docs.google.com/uc?export=download"
            # init a HTTP session
            session = requests.Session()
            # make a request
            response = session.get(URL, params={'id': file_id}, stream=True)
            token = get_confirm_token(response)
            if token:
                params = {'id': file_id, 'confirm': token}
                response = session.get(URL, params=params, stream=True)
            # download to disk
            save_response_content(response, file_name)
        elif len(argv) == 3:
            print(url)
        else:
            sys.exit(2)


if __name__ == '__main__':
    main(sys.argv)
