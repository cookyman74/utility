from qbittorrent import Client
import sys

# connect to the qbittorent Web UI
qb = Client("http://127.0.0.1:8080/")

# 설치된 qbittorent에 접속할 수 있도록 사전에 설정된 계정정보로 설정.
qb.login("admin", "adminadmin")

# 토렌트파일 열기
file_path = sys.argv[1]
torrent_file = open(file_path, "rb")

# start downloading
qb.download_from_file(torrent_file)
# 만약 토렌트 파일이 아닌 마그네틱링크를 이용하고자 한다면 다음과 같이 코드를 바꾸시면 됩니다.
# magnet_link = "magnet:?xt=urn:btih:e334ab9ddd91c10938a7....."
# qb.download_from_link(magnet_link)

# 다운로드 경로를 바꾸려면 다음과 같이 savepath 옵션을 추가로 설정해주세요.
# qb.download_from_file(torrent_file, savepath="/the/path/you/want/to/save")

# 모든 다운로드 일시정지
qb.pause_all()

# 재실행
qb.resume_all()

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

# 토렌트 다운로드 리스트 입니다.
torrents = qb.torrents()

for torrent in torrents:
    print("Torrent name:", torrent["name"])
    print("hash:", torrent["hash"])
    print("Seeds:", torrent["num_seeds"])
    print("File size:", get_size_format(torrent["total_size"]))
    print("Download speed:", get_size_format(torrent["dlspeed"]) + "/s")