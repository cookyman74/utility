import os
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc


def get_size_format(b_size, factor=1024, suffix="B"):
    """
    스케일함수, 1024으로 나눈값으로 소수점2째자리까지 표현
    :param b_size:
    :param factor:
    :param suffix:
    :return:
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b_size < factor:
            return f"{b_size:.2f}{unit}{suffix}"
        b_size /= factor
    return f"{b_size:.2f}Y{suffix}"


def get_directory_size(directory):
    """
    디렉토리 크기 측정.
    :param directory:
    :return: 디렉토리 크기, 바이트값
    """
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # 하위 목록중에 파일이면, stat()을 이용하여 파일사이즈
                total += entry.stat().st_size
            elif entry.is_dir():
                # 하위 목록중에 디렉토리이면, 재귀
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total


if __name__ == "__main__":
    import sys
    folder_path = sys.argv[1]

    directory_sizes = []
    names = []
    # 특정 경로의 하위디렉토리를 순환반복
    for directory in os.listdir(folder_path):

        directory = os.path.join(folder_path, directory)
        # 디렉토리 크기
        directory_size = get_directory_size(directory)
        if directory_size == 0:
            continue
        directory_sizes.append(directory_size)
        names.append(os.path.basename(directory) + ": " + get_size_format(directory_size))

    total = get_size_format(sum(directory_sizes))
    title = f"{folder_path}({total})내 서브-디렉토리별 용량분포(bytes)"
    # plot_pie(directory_sizes, names)

    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
    plt.pie(directory_sizes, labels=names, autopct=lambda pct: f"{pct:.2f}%")
    plt.title(title)
    plt.show()