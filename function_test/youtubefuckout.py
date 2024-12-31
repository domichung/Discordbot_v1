import yt_dlp
import os

def download_song_to_local(url: str, save_path: str) -> str:
    """
    下載音樂到本地端。

    Args:
        url (str): 音樂來源的 YouTube URL。
        save_path (str): 本地保存的路徑。

    Returns:
        str: 已保存檔案的完整路徑。
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),  # 保存格式
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)  # 下載音樂
            file_path = ydl.prepare_filename(info)
            if file_path.endswith(".webm") or file_path.endswith(".m4a"):
                file_path = file_path.rsplit('.', 1)[0] + '.mp3'  # 更新為 mp3 副檔名

            return file_path

    except Exception as e:
        print(f"下載失敗: {e}")
        return None

# 使用範例
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=4hBf5rKm7kU"  # 替換為您的音樂 URL
    save_directory = "./downloads"  # 指定保存的資料夾

    # 確保資料夾存在
    os.makedirs(save_directory, exist_ok=True)

    downloaded_file = download_song_to_local(youtube_url, save_directory)
    if downloaded_file:
        print(f"音樂已下載: {downloaded_file}")
    else:
        print("音樂下載失敗！")
