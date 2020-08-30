import youtube_dl
import subprocess
import os
import glob
import re
import time

url = 'https://www.youtube.com/playlist?list=PLkDaE6sCZn6Ec-XTbcX1uRg2_u4xOEky0'
ydl_opts = {
    'quiet': True,
}

ytb_playlist_url = []
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl_list = ydl.extract_info(url, download=False)
    if 'entries' in ydl_list:
        # Can be a playlist or a list of videos
        video = ydl_list['entries']

        # loops entries to grab each video_url
        for i, item in enumerate(video):
            ytb_playlist_url.append(ydl_list['entries'][i]['webpage_url'])

download_folder = "C:\\Users\\cooky\\Google 드라이브\\EZUP Work\\"

ydl_opts = {
    'writesubtitles': 'best',
    'skip_download': True,
    'subtitleslangs': ['en', 'ko'],
    'outtmpl': download_folder+'%(uploader)s\\COURSE1\\%(autonumber)s_%(title)s',
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(ytb_playlist_url)

os.chdir(download_folder+"%s" % ydl_list['uploader'])
all_files = glob.glob("*.vtt", recursive=True)

for source_filename in all_files:
    match = re.search(r"^.*\.en\.vtt", source_filename)
    if match:
        file_name = "[ENGLISH]"+source_filename
    else:
        file_name = "[한글자막]"+source_filename

    os.rename(source_filename, file_name)
    dest_filename = os.path.splitext(file_name)[0]

    try:
        subprocess.Popen(
            ['ffmpeg', '-i', file_name, dest_filename + '.srt'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("오류")

time.sleep(10)
[os.remove(f) for f in glob.glob("*.vtt")]
