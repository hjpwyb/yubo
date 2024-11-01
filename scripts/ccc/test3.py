import os
import requests
from bs4 import BeautifulSoup
import random

# 获取子页面链接
def get_subpage_links(main_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
    
    def get_random_url(url):
        random_query = f"?t={random.randint(1, 100000)}"
        return url + random_query
    
    url_with_random_query = get_random_url(main_url)
    response = requests.get(url_with_random_query, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)

    subpage_urls = []
    for link in links:
        href = link.get('href')
        if href and href.startswith('/index.php/vod/detail/id/'):
            full_url = f"https://huyazy.com{href}"
            subpage_urls.append(full_url)
    
    return subpage_urls

# 从子页面提取 M3U8 链接及其他信息
def extract_m3u8_links(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
    
    def get_random_url(url):
        random_query = f"?t={random.randint(1, 100000)}"
        return url + random_query
    
    url_with_random_query = get_random_url(url)
    response = requests.get(url_with_random_query, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    info_div = soup.find('div', class_='vodInfo')
    if info_div:
        title_tag = info_div.find('h2')
        title = title_tag.get_text(strip=True) if title_tag else "default_title"
    else:
        title = "default_title"

    # 查找所有 <a> 标签内的播放链接
    m3u8_links = []
    for a_tag in soup.select('#play_2 a'):
        href = a_tag.get('href')
        if href and href.endswith('.m3u8'):
            full_link = href if href.startswith('http') else f"https://huyazy.com{href}"
            episode_title = a_tag.get_text(strip=True)
            m3u8_links.append((episode_title, full_link))

    return title, m3u8_links

# 保存所有 M3U8 链接到一个合并的 M3U 文件
def save_merged_m3u_file(folder_path, title_m3u8_data):
    output_file_path = os.path.join(folder_path, 'merged.m3u')
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for title, m3u8_links in title_m3u8_data:
            if m3u8_links:
                # 每个剧集的标题作为一个 #EXTINF 行
                file.write(f"#EXTINF:-1,{title}\n")
                # 添加第一个链接来显示标题
                file.write(f"{m3u8_links[0][1]}\n")
                for episode_title, link in m3u8_links:
                    # 写入每一集的实际链接
                    file.write(f"#EXTINF:-1,{episode_title}\n")
                    file.write(f"{link}\n")
                # 添加结束标记确保下一行有假链接
                file.write("#EXTINF:-1, --- End of Episode ---\n")
                file.write("http://example.com/fake-link-for-end-of-episode\n")
    print(f"M3U 文件已成功合并为 {output_file_path}")

# 主函数
def main():
    folder_path = 'scripts/ccc'  # 指定文件夹路径
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # 清空旧的合并文件
    merged_file_path = os.path.join(folder_path, 'merged.m3u')
    if os.path.exists(merged_file_path):
        os.remove(merged_file_path)
        print(f"已删除旧文件: {merged_file_path}")

    # 更新后的页面链接
    base_urls = [
        "https://huyazy.com/index.php/vod/type/id/20/page/1.html?ac=detail",
        "https://huyazy.com/index.php/vod/type/id/20/page/2.html?ac=detail"
    ]
    
    # 存储所有剧集标题和链接信息
    title_m3u8_data = []
    
    # 抓取并收集所有子页面的 M3U8 链接
    for main_url in base_urls:
        subpage_urls = get_subpage_links(main_url)
        for url in subpage_urls:
            print(f"Processing {url}...")
            title, m3u8_links = extract_m3u8_links(url)
            if m3u8_links:
                title_m3u8_data.append((title, m3u8_links))
            else:
                print(f"No M3U8 links found for {url}")

    # 保存所有 M3U8 链接到一个文件中
    save_merged_m3u_file(folder_path, title_m3u8_data)

if __name__ == "__main__":
    main()
