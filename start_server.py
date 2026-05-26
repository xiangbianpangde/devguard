"""本地预览 dashboard.html 的静态服务器。

用法: python start_server.py  （等价于 python -m http.server 8080，但固定根目录）
打开: http://localhost:8080/dashboard.html
"""
import os
import http.server
import webbrowser
import threading

PORT = 8080
URL = f"http://localhost:{PORT}/dashboard.html"

# 以脚本所在目录为根，保证复制到任何项目后都能用
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 仅绑定本机回环地址，不暴露到局域网
server = http.server.HTTPServer(("127.0.0.1", PORT), http.server.SimpleHTTPRequestHandler)

# 服务器就绪后自动用默认浏览器打开仪表盘
threading.Timer(0.5, lambda: webbrowser.open(URL)).start()

print(f"Server running at {URL} (Ctrl+C 停止)")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n已停止。")
