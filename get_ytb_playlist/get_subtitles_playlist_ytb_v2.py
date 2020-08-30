from urllib.parse import parse_qs, urlparse
import googleapiclient.discovery
import youtube_dl
import subprocess
import os
import glob
import re
import time

url = 'https://www.youtube.com/playlist?list=PLOU2XLYxmsII9mzQ-Xxug4l2o04JBrkLV'

#extract playlist id from url
query = parse_qs(urlparse(url).query, keep_blank_values=True)
playlist_id = query["list"][0]

print(f'get all playlist items links from {playlist_id}')
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey="AIzaSyCk0ie0Dd75ry5t1srGz6OnaXZM5e1wMdg")

request = youtube.playlistItems().list(
    part="snippet",
    playlistId=playlist_id,
    #maxResults=50
)
response = request.execute()

playlist_items = []

while request is not None:
    response = request.execute()
    playlist_items += response["items"]
    request = youtube.playlistItems().list_next(request, response)

print(f"total: {len(playlist_items)}")
channel_name = playlist_items[0]["snippet"]["channelTitle"]

ytb_playlist_url = [
    f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}'
    for t in playlist_items
]

course_name = ""
download_folder = "C:\\Users\\cooky\\Google 드라이브\\EZUP Work\\"+channel_name+"\\"+course_name

ydl_opts = {
    # 'writeautomaticsub': True,
    'writesubtitles': True,
    'skip_download': True,
    'subtitleslangs': ['en', 'ko'],
    'outtmpl': download_folder+'\\%(autonumber)s_%(title)s',
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(ytb_playlist_url)

os.chdir(download_folder)
f = open("playlist_url.txt", 'w')
f.write(url)
f.close()
all_files = glob.glob("*.vtt", recursive=True)

for source_filename in all_files:
    print(source_filename + "변경합니다.")
    match = re.search(r"^.*\.en\.vtt", source_filename)
    if match:
        file_name = "[ENGLISH]"+source_filename
    else:
        print("한글 변경")
        file_name = "[한글자막]"+source_filename

    dest_filename = os.path.splitext(file_name)[0]

    try:
        subprocess.Popen(
            ['ffmpeg', '-i', source_filename, dest_filename + '.srt'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("오류")

time.sleep(10)
[os.remove(f) for f in glob.glob("*.vtt")]
