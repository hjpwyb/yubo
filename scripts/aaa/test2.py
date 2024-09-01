import requests
from bs4 import BeautifulSoup

# 假设你的脚本已经定义了生成 M3U 文件内容的逻辑，并且 content 是最终的 M3U 文件内容
# 这里是示例逻辑

# 例如，content 是你提取的 m3u8 链接生成的内容
content = "#EXTM3U\n"
urls = [
    "http://example.com/video1.m3u8",
    "http://example.com/video2.m3u8",
    # 添加更多链接...
]

for url in urls:
    content += f"#EXTINF:-1,Example Video\n{url}\n"

# 将 content 写入文件
output_path = "scripts/aaa/playlisty.m3u"
with open(output_path, 'w') as f:
    f.write(content)

print(f"M3U 文件已生成并保存在 {output_path}")
