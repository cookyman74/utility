import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
import youtube_dl
import subprocess
import os
import glob

#extract playlist id from url
url = 'https://www.youtube.com/playlist?list=PLkDaE6sCZn6Hn0vK8co82zjQtt3T2Nkqc'
query = parse_qs(urlparse(url).query, keep_blank_values=True)
playlist_id = query["list"][0]

print(f'get all playlist items links from {playlist_id}')
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = "AIzaSyDlSX4-3u-Vj9S0X77X2iZLFLW7dtOQgU4")

request = youtube.playlistItems().list(
    part = "snippet",
    playlistId = playlist_id,
    maxResults = 50
)
response = request.execute()

playlist_items = []
while request is not None:
    response = request.execute()
    playlist_items += response["items"]
    request = youtube.playlistItems().list_next(request, response)

print(f"total: {len(playlist_items)}")
yt_list = [
    f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}'
    for t in playlist_items
]

ydl_opts = {
    'writesubtitles': 'best',
    'skip_download': True,
    'outtmpl': '%(uploader)s - %(title)s.%(ext)s',
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    a = ydl.download(yt_list)

all_files = glob.glob("*.vtt", recursive=True)

for source_filename in all_files:
    dest_filename = os.path.splitext(source_filename)[0]
    subprocess.Popen(
        ['ffmpeg', '-i', source_filename, dest_filename + '.srt'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)