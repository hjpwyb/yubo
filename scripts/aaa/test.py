import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import shutil
import time
import random
import logging

# 日志配置
logging.basicConfig(
    filename='crawler_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
logging.getLogger('').addHandler(console)

def log_error(message):
    logging.error(message)

def clear_folder(folder_path):
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"已删除文件夹: {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        print(f"已创建新文件夹: {folder_path}")
    except PermissionError as e:
        print(f"权限错误，无法清理文件夹: {e}")
        log_error(f"权限错误: {e}")
        raise

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"已创建目录: {path}")

def download_poster_image(image_url, folder_path):
    try:
        response = request_with_retries(image_url)
        if response is None:
            raise Exception("封面图片下载失败")
        image_path = os.path.join(folder_path, 'poster.jpg')
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"封面图片已下载到: {image_path}")
    except Exception as e:
        print(f"封面图片下载失败: {e}")
        log_error(f"封面图片下载失败: {e}")

def request_with_retries(url, max_retries=3, delay=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"请求失败 (尝试 {attempt+1}/{max_retries}): {e}")
            log_error(f"请求失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt + 1 < max_retries:
                print(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
            else:
                print(f"请求失败，已达最大重试次数: {url}")
                return None

def get_subpage_links(main_url):
    try:
        response = request_with_retries(main_url)
        if response is None:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        subpage_urls = set()
        for link in links:
            href = link.get('href')
            if href and 'vod/detail/id' in href:
                full_url = urljoin(main_url, href)
                subpage_urls.add(full_url)
        return list(subpage_urls)
    except Exception as e:
        print(f"获取子页面链接失败: {e}")
        log_error(f"获取子页面链接失败: {e}")
        return []

def random_delay(min_delay=2, max_delay=5):
    delay = random.uniform(min_delay, max_delay)
    print(f"随机延迟 {delay:.2f} 秒")
    time.sleep(delay)

def extract_m3u8_links_and_poster(url):
    try:
        response = request_with_retries(url)
        if response is None:
            return "default_title", None, []
        soup = BeautifulSoup(response.content, 'html.parser')
        debug_file = f'debug_page_{int(time.time())}.html'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"网页内容已保存到: {debug_file}")

        title_div = soup.find('div', class_='vodInfo')
        title = title_div.find('h2').get_text(strip=True) if title_div else "default_title"
        poster_img_tag = soup.find('div', class_='vodImg').find('img')
        poster_url = urljoin(url, poster_img_tag['src']) if poster_img_tag else None

        m3u8_links = []
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_text = script.get_text()
            if '.m3u8' in script_text:
                m3u8_match = re.findall(r'(http[s]?://[^\'"\s]+\.m3u8[^\'"\s]*)', script_text)
                for m3u8_url in m3u8_match:
                    m3u8_links.append(('Episode', m3u8_url))

        if not m3u8_links:
            for tag in soup.find_all(['a', 'iframe', 'source']):
                href = tag.get('href') or tag.get('src')
                if href and '.m3u8' in href:
                    full_link = href if href.startswith('http') else urljoin("https://huyazy.com", href)
                    episode_title = tag.get_text(strip=True) or "Episode"
                    m3u8_links.append((episode_title, full_link))

        return title, poster_url, m3u8_links
    except Exception as e:
        print(f"解析失败: {e}")
        log_error(f"解析失败: {e}")
        return "default_title", None, []

def save_m3u8_files_for_each_episode(folder_path, title, m3u8_links):
    for idx, (episode_title, link) in enumerate(m3u8_links, start=1):
        raw_title = episode_title.split('$')[0].strip()
        cleaned_title = re.sub(r'[<>:"/\\|?*]', '', raw_title).replace(" ", "")
        safe_title = (title[:50] + '..') if len(title) > 50 else title
        filename = f"{safe_title}_{cleaned_title or f'Ep{idx}'}.m3u"
        filepath = os.path.join(folder_path, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                f.write(f"#EXTINF:-1,{raw_title}\n")
                f.write(f"{link}\n")
            print(f"M3U8 链接已成功写入 {filepath} 文件中")
        except Exception as e:
            print(f"保存 M3U 文件失败: {e}")
            log_error(f"保存 M3U 文件失败: {e}")

def main():
    base_folder = os.path.abspath(os.getenv('BASE_FOLDER', '/volume1/docker/python_scripts/bbb'))
    clear_folder(base_folder)

    start_page, end_page = 1, 2
    base_urls = [f"https://huyazy.com/index.php/vod/type/id/20/page/{i}.html?ac=detail" 
                 for i in range(start_page, end_page + 1)]
    
    for main_url in base_urls:
        subpage_urls = get_subpage_links(main_url)
        for url in subpage_urls:
            random_delay()
            print(f"处理 {url}...")
            title, poster_url, m3u8_links = extract_m3u8_links_and_poster(url)
            if m3u8_links:
                show_folder = os.path.join(base_folder, title)
                ensure_directory_exists(show_folder)
                if poster_url:
                    download_poster_image(poster_url, show_folder)
                save_m3u8_files_for_each_episode(show_folder, title, m3u8_links)
            else:
                print(f"未找到 M3U8 链接: {url}")
                log_error(f"未找到 M3U8 链接: {url}")

if __name__ == "__main__":
    main()
