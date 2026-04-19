#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
局域网文件回收系统 - 服务端
"""

import os
import sys
from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
from pathlib import Path

app = Flask(__name__)

# 配置
# 可以通过环境变量或修改这里设置基础保存文件夹
BASE_SAVE_FOLDER = os.environ.get('BASE_SAVE_FOLDER', r'D:\uploads')
# 允许上传所有类型的文件
ALLOWED_EXTENSIONS = set()

# 确保基础文件夹存在
Path(BASE_SAVE_FOLDER).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    # 允许所有文件类型
    return True if filename else False

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>局域网文件回收系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #f5f5f5;
            min-height: 100vh;
            padding: 2rem 1rem;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 2rem;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
            color: #333;
        }
        label .required {
            color: #e53e3e;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 1rem;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus, input[type="file"]:focus {
            outline: none;
            border-color: #3182ce;
        }
        .seat-input {
            font-size: 1.2rem;
            text-align: center;
            letter-spacing: 0.1em;
        }
        button {
            width: 100%;
            padding: 1rem;
            background-color: #3182ce;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #2b6cb0;
        }
        .message {
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }
        .message.success {
            background-color: #f0fff4;
            color: #22543d;
            border: 1px solid #9ae6b4;
        }
        .message.error {
            background-color: #fed7d7;
            color: #742a2a;
            border: 1px solid #feb2b2;
        }
        .file-list {
            margin-top: 1rem;
            padding: 1rem;
            background-color: #f7fafc;
            border-radius: 6px;
        }
        .file-item {
            padding: 0.5rem 0;
            border-bottom: 1px solid #e2e8f0;
        }
        .file-item:last-child {
            border-bottom: none;
        }
        .file-name {
            font-weight: 500;
        }
        .file-size {
            color: #718096;
            font-size: 0.875rem;
        }
        footer {
            text-align: center;
            margin-top: 2rem;
            color: #a0aec0;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 文件回收系统</h1>
        <p class="subtitle">请填写座号并上传文件</p>

        {% if message %}
        <div class="message {{message_type}}">
            {{ message }}
        </div>
        {% endif %}

        <form method="POST" enctype="multipart/form-data" action="/upload">
            <div class="form-group">
                <label>
                    <span class="required">*</span> 用户名
                </label>
                <input 
                    type="text" 
                    name="seat" 
                    id="seat" 
                    class="seat-input"
                    placeholder="请输入你的用户名 (例如: zhangsan, 张三)" 
                    required
                    value="{{seat}}"
                >
            </div>

            <div class="form-group">
                <label>选择文件</label>
                <input type="file" name="files" id="file" multiple required>
            </div>

            <button type="submit">🚀 上传文件</button>
        </form>

        {% if uploaded_files %}
        <div class="file-list">
            <strong>本次上传成功 ({{ uploaded_files|length }} 个文件):</strong>
            {% for f in uploaded_files %}
            <div class="file-item">
                <div class="file-name">✓ {{ f.filename }}</div>
                <div class="file-size">{{ f.size_readable }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <footer>
            局域网文件回收系统 · {{ total_files }} 个文件已回收
        </footer>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    # 统计总文件数
    total_files = 0
    for root, dirs, files in os.walk(BASE_SAVE_FOLDER):
        total_files += len(files)
    
    return render_template_string(HTML_TEMPLATE, 
        message=None, 
        total_files=total_files,
        seat='')

@app.route('/upload', methods=['POST'])
def upload():
    seat = request.form.get('seat', '').strip()
    
    if not seat:
        # 座号为空
        total_files = sum(len(files) for _, _, files in os.walk(BASE_SAVE_FOLDER))
        return render_template_string(HTML_TEMPLATE,
            message='错误: 用户名不能为空，请填写用户名后重新上传',
            message_type='error',
            total_files=total_files,
            seat='')
    
    # 安全处理座号作为文件夹名 - 支持中文
    # 只移除不安全字符，保留中文
    import re
    safe_seat = re.sub(r'[<>:"/\\|?*]', '', seat).strip()
    if not safe_seat:
        total_files = sum(len(files) for _, _, files in os.walk(BASE_SAVE_FOLDER))
        return render_template_string(HTML_TEMPLATE,
            message='错误: 用户名包含无效字符，请去掉特殊符号',
            message_type='error',
            total_files=total_files,
            seat=seat)
    
    # 转换为安全文件名同时保留中文
    safe_seat = safe_seat.replace(' ', '_')
    
    # 创建用户文件夹 - 每个上传者用户名单独一个子文件夹
    seat_folder = os.path.join(BASE_SAVE_FOLDER, safe_seat)
    Path(seat_folder).mkdir(parents=True, exist_ok=True)
    
    # 获取所有上传的文件，保存到用户名对应的子文件夹
    files = request.files.getlist('files')
    uploaded_files = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if file and allowed_file(file.filename):
            # 处理文件名 - 保留中文，只移除Windows不允许的字符
            import re
            filename = file.filename
            # 只保留文件名部分，去掉路径 (有些浏览器可能传完整路径)
            filename = os.path.basename(filename)
            # 移除Windows不允许的字符
            filename = re.sub(r'[<>:"/\\|?*]', '', filename).strip()
            if not filename:
                errors.append(f"{file.filename}: 文件名包含无效字符，已跳过")
                continue
            
            # 处理同名文件，避免覆盖
            base, ext = os.path.splitext(filename)
            counter = 1
            final_filename = filename
            while os.path.exists(os.path.join(seat_folder, final_filename)):
                final_filename = f"{base}_{counter}{ext}"
                counter += 1
            
            file_path = os.path.join(seat_folder, final_filename)
            file.save(file_path)
            size = os.path.getsize(file_path)
            uploaded_files.append({
                'filename': final_filename,
                'size': size,
                'size_readable': format_size(size)
            })
        else:
            errors.append(f"{file.filename}: 文件类型不允许")
    
    total_files = sum(len(files) for _, _, files in os.walk(BASE_SAVE_FOLDER))
    
    if len(errors) > 0:
        error_msg = "部分文件上传失败: " + ", ".join(errors)
        if len(uploaded_files) > 0:
            return render_template_string(HTML_TEMPLATE,
                message=f"{len(uploaded_files)} 个文件上传成功，但: {error_msg}",
                message_type='error' if len(uploaded_files) == 0 else 'success',
                uploaded_files=uploaded_files,
                total_files=total_files,
                seat=seat)
        else:
            return render_template_string(HTML_TEMPLATE,
                message=error_msg,
                message_type='error',
                total_files=total_files,
                seat=seat)
    
    if len(uploaded_files) == 0:
        return render_template_string(HTML_TEMPLATE,
            message='没有选择任何有效文件',
            message_type='error',
            total_files=total_files,
            seat=seat)
    
    return render_template_string(HTML_TEMPLATE,
        message=f'✅ 成功! {len(uploaded_files)} 个文件已上传到 [{seat}] 文件夹',
        message_type='success',
        uploaded_files=uploaded_files,
        total_files=total_files,
        seat=seat)

def format_size(size_bytes):
    """格式化文件大小为可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_local_ip():
    """获取本机局域网IP地址"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个外部地址，不需要真正连接
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    # 处理命令行参数修改保存路径
    if len(sys.argv) > 1:
        BASE_SAVE_FOLDER = sys.argv[1]
        Path(BASE_SAVE_FOLDER).mkdir(parents=True, exist_ok=True)
        print(f"自定义保存路径: {BASE_SAVE_FOLDER}")
    
    local_ip = get_local_ip()
    port = 5000
    
    print("\n" + "="*50)
    print(" 📁 局域网文件回收系统 - 服务端已启动")
    print("="*50)
    print(f"\n 客户端访问地址:")
    print(f"  http://{local_ip}:{port}")
    print(f"\n 保存位置:")
    print(f"  {BASE_SAVE_FOLDER}")
    print(f"\n 每个用户独立文件夹:")
    print(f"  {BASE_SAVE_FOLDER}\\【用户名】\\你的文件")
    print("\n" + "="*50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
