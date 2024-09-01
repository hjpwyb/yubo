# 假设你有一些生成或获取 m3u8 链接的代码
m3u8_links = [
    "http://example.com/stream/1.m3u8",
    "http://example.com/stream/2.m3u8",
    "http://example.com/stream/3.m3u8"
]

# 生成内容
content = ""
for link in m3u8_links:
    content += f"#EXTINF:-1, Some description\n"
    content += f"{link}\n"

# 将内容写入文件
output_path = "scripts/aaa/playlisty.m3u"
with open(output_path, 'w') as f:
    f.write(content)

print(f"M3U 文件已生成并保存在 {output_path}")
