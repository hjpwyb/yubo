import os
from pathlib import Path
import re

# 配置基本路径（相对路径，基于脚本所在目录）
script_dir = Path(__file__).parent  # scripts/aaa
base_dir = script_dir.parent / "bbb"  # scripts/bbb
# GitHub raw 文件的基础 URL
web_base_url = "https://raw.githubusercontent.com/hjpwyb/yubo/main/scripts/bbb"
output_path = script_dir / "index.html"  # scripts/aaa/index.html

def extract_episode_number(text):
    """从文件名中提取集数数字用于排序"""
    match = re.search(r'第(\d+)[集期]', text)
    if match:
        return int(match.group(1))
    return float('inf')

def generate_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>节目列表</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                padding: 0;
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
            }
            h2 { 
                margin-top: 40px;
                margin-bottom: 20px;
            }
            .category { 
                margin-bottom: 40px; 
                width: 100%;
            }
            .program-grid { 
                display: grid; 
                grid-template-columns: repeat(4, 1fr); 
                gap: 15px; 
                padding: 0 10px;
            }
            .program-item { 
                text-align: center; 
                position: relative;
                width: 100%;
                margin-bottom: 40px;
            }
            .program-name { 
                font-weight: bold; 
                margin-bottom: 8px;
                font-size: 16px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 200px;
            }
            .poster-container { 
                position: relative;
                width: 100%;
            }
            .poster { 
                width: 200px; 
                height: 280px; 
                object-fit: cover; 
                display: block; 
                margin: 0 auto;
                border-radius: 5px; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
            }
            .episodes { 
                display: none; 
                position: absolute; 
                left: 0; 
                top: 100%; 
                width: 100%; 
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid #ccc; 
                padding: 8px; 
                z-index: 10; 
                text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                white-space: normal;
                max-height: 200px;
                overflow-y: auto;
            }
            .poster-container:hover .episodes { 
                display: block; 
            }
            .episodes a { 
                display: inline-block; 
                margin: 3px 6px; 
                text-decoration: none; 
                color: #0066cc;
            }
            .episodes a:hover {
                color: #003366;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>节目列表</h1>
    """

    # 按节目分组（假设 scripts/bbb 下直接是节目文件夹）
    programs = {}
    for root, dirs, files in os.walk(base_dir):
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == ".":
            continue  # 跳过根目录本身
        
        program_name = rel_path.split(os.sep)[0]  # 取第一级目录作为节目名
        if program_name not in programs:
            programs[program_name] = {'m3u': [], 'poster': None}

        for file in files:
            if file.endswith(('.m3u', '.jpg')):
                full_path = os.path.join(root, file)
                web_url = f"{web_base_url}/{os.path.relpath(full_path, base_dir).replace(os.sep, '/')}"

                if file.endswith('.m3u'):
                    programs[program_name]['m3u'].append((file, web_url))
                elif file == 'poster.jpg':  # 只识别 poster.jpg 作为海报
                    programs[program_name]['poster'] = web_url

    # 生成节目内容
    if programs:
        html_content += '        <div class="category">\n'
        html_content += '            <div class="program-grid">\n'

        for program_name, content in sorted(programs.items()):
            html_content += '                <div class="program-item">\n'
            html_content += f'                    <div class="program-name">{program_name}</div>\n'
            html_content += '                    <div class="poster-container">\n'
            
            if content['poster']:
                html_content += f'                        <img src="{content["poster"]}" alt="{program_name}" class="poster">\n'
            else:
                html_content += '                        <span>无海报</span>\n'
            
            html_content += '                        <div class="episodes">\n'
            if not content['m3u']:
                html_content += '                            无集数文件\n'
            else:
                sorted_episodes = sorted(content['m3u'], key=lambda x: (extract_episode_number(x[0]), x[0]))
                for episode_name, m3u_url in sorted_episodes:
                    display_name = episode_name.replace(f"{program_name}_", "").replace(".m3u", "")
                    potplayer_url = f"potplayer://{m3u_url}"
                    html_content += f'                            <a href="{potplayer_url}">{display_name}</a>\n'
            html_content += '                        </div>\n'
            html_content += '                    </div>\n'
            html_content += '                </div>\n'

        html_content += '            </div>\n'
        html_content += '        </div>\n'
    else:
        html_content += '        <p>未找到任何节目</p>\n'

    html_content += """
    </body>
    </html>
    """

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML文件已生成到: {output_path}")

if __name__ == "__main__":
    generate_html()
