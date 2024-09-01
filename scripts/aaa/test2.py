import os
import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# 配置文件路径
TEMP_FILE = 'combined.txt'
CLEANED_FILE = 'cleaned_combined.txt'
OUTPUT_M3U_FILE = 'playlisty.m3u'
OUTPUT_DIR = 'output/scripts/aaa'  # 指定输出目录

def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
    except Exception as e:
        raise ValueError(f"无法从URL中提取域名: {e}")

def fetch_and_extract_subpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        text = response.text

        start_index = text.find("动漫剧情")
        if start_index == -1:
            return None

        end_index = min(start_index + 1000, len(text))
        snippet = text[start_index:end_index]

        return snippet

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def get_subpage_links(main_page_url):
    try:
        response = requests.get(main_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        domain = extract_domain(main_page_url)
        pattern = re.compile(r'/vodplay/.*')
        all_links = [urljoin(domain, link['href']) for link in links]

        # 只提取匹配的子页面链接
        subpage_links = {urljoin(domain, link['href']) for link in links if pattern.match(link['href'])}
        
        subpage_links = list(subpage_links)
        num_links = len(subpage_links)
        center_start_index = max(0, (num_links - 40) // 2)
        return subpage_links[center_start_index:center_start_index + 40]

    except Exception as e:
        print(f"Failed to fetch main page {main_page_url}: {e}")
        return []

def clean_text(text):
    text = re.sub(r'动漫剧情.*?<h3 class=', '<h3 class=', text, flags=re.DOTALL)
    text = re.sub(r'</h3>.*?url":', '</h3>', text, flags=re.DOTALL)
    text = re.sub(r'url_next":".*?时间：', '时间：', text, flags=re.DOTALL)
    text = re.sub(r'<div class="mac_digg" style="float:left"><span class="click-ding-gw"><a class="digg_link" data-id="\d+" data-mid=', '', text, flags=re.DOTALL)
    return text

def write_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def extract_data():
    title_pattern = re.compile(r'<h3 class="title">(.*?)<\/h3>', re.DOTALL)
    m3u8_pattern = re.compile(r'https://[^\s"]+\.m3u8')

    with open(CLEANED_FILE, 'r', encoding='utf-8') as file:
        content = file.read()

    content = content.replace('\\', '')

    titles = title_pattern.findall(content)
    m3u8_links = m3u8_pattern.findall(content)

    return titles, m3u8_links

def generate_playlist_m3u(titles, m3u8_links):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_m3u_path = os.path.join(OUTPUT_DIR, OUTPUT_M3U_FILE)
    
    if os.path.exists(output_m3u_path):
        os.remove(output_m3u_path)
    
    with open(output_m3u_path, 'w', encoding='utf-8') as m3u_file:
        m3u_file.write('#EXTM3U\n')
        for title, link in zip(titles, m3u8_links):
            m3u_file.write(f"#EXTINF:-1,{title}\n{link}\n")
    
    print(f"\n已生成 {output_m3u_path} 文件，包含 {len(m3u8_links)} 个链接。")

def main():
    if not os.path.exists('temp_pages'):
        os.makedirs('temp_pages')

    # 每次运行前清空文件
    open(TEMP_FILE, 'w').close()
    open(CLEANED_FILE, 'w').close()

    # 扩展域名试错范围
    possible_domains = [f"http://82{j}ck.cc" for j in range(60, 70)] + [f"http://83{j}ck.cc" for j in range(60, 70)]
    valid_domain = None
    
    for domain in possible_domains:
        main_page_url = f'{domain}/vodtype/9-1.html'
        print(f"尝试访问 {main_page_url}...")
        
        try:
            response = requests.get(main_page_url)
            if response.status_code == 200 and '/vodtype/' in response.text:
                valid_domain = domain
                print(f"找到有效域名: {domain}")
                break
        except requests.RequestException:
            continue
    
    if not valid_domain:
        print("没有找到有效的域名。")
        return

    # 处理所有页面
    for i in range(1, 6):
        main_page_url = f'{valid_domain}/vodtype/9-{i}.html'
        print(f"处理页面: {main_page_url}")
        
        subpage_links = get_subpage_links(main_page_url)
        if not subpage_links:
            print(f"未提取到子页面链接或链接数量为0，跳过页面: {main_page_url}")
            continue
    
        print(f"提取到的子页面链接数量: {len(subpage_links)}")
    
        for url in subpage_links:
            snippet = fetch_and_extract_subpage(url)
            if snippet:
                with open(TEMP_FILE, 'a', encoding='utf-8') as file:
                    file.write(snippet)
                    file.write("\n" + "="*80 + "\n")

    print(f"数据已从子页面保存到 {TEMP_FILE}。")

    content = read_file(TEMP_FILE)
    
    if not content.strip():
        print("未能读取到子页面内容。")
        return
    
    print("正在清理内容...")
    cleaned_content = clean_text(content)
    write_file(CLEANED_FILE, cleaned_content)
    
    print(f"处理后的内容已保存到 {CLEANED_FILE}")

    print("正在提取标题和 m3u8 链接...")
    titles, m3u8_links = extract_data()
    
    if not titles or not m3u8_links:
        print("没有提取到有效的标题或 m3u8 链接。")
        return
    
    if len(titles) != len(m3u8_links):
        print("警告: 标题和 m3u8 链接数量不匹配！")
    
    generate_playlist_m3u(titles, m3u8_links)

if __name__ == "__main__":
    main()
