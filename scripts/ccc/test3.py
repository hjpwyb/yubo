import os

def merge_m3u_files(folder_path):
    # 合并后的输出文件路径
    output_file_path = os.path.join(folder_path, 'merged.m3u')

    # 创建或覆盖输出文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("#EXTM3U\n")  # 写入 M3U 文件的头部信息

        # 遍历指定文件夹中的每个文件
        for file in os.listdir(folder_path):
            if file.endswith('.m3u'):
                with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as input_file:
                    lines = input_file.readlines()
                    
                    # 逐行处理输入文件内容
                    for line in lines:
                        line = line.strip()  # 去除前后空白字符
                        # 写入剧集标题
                        if line.startswith("#EXTINF:"):
                            output_file.write(line + '\n')  # 写入剧集标题
                        # 写入有效链接
                        elif line and not line.startswith("#"):
                            output_file.write(line + '\n')  # 写入链接
                    
                    # 添加“End of Episode”的行
                    output_file.write("#EXTINF:-1, --- End of Episode ---\n")

    print(f"M3U 文件已合并到 {output_file_path}")

if __name__ == "__main__":
    # 替换为您的文件夹路径
    folder_path = 'ccc'  # 确保这是您 M3U 文件的文件夹
    merge_m3u_files(folder_path)
