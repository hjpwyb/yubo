import os

output_path = "scripts/aaa/playlisty.m3u"
with open(output_path, 'w') as f:
    f.write(content)

print(f"M3U 文件已生成并保存在 {os.path.abspath(output_path)}")
