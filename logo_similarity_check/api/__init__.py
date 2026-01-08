import uvicorn
import os
import sys

# 解决PyCharm运行上下文的路径问题
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    # 方案：放弃workers多进程（Debug模式不支持），改用单进程
    # 调试时用单进程，生产环境启动时再加workers
    uvicorn.run(
        "main:app",  # 关键：用相对导入字符串（__init__.py和main.py同目录）
        host="0.0.0.0",
        port=8901,
        workers=1,  # 调试模式强制单进程（workers>1会和Debug冲突）
        reload=True  # 可选：调试时开启热重载，修改代码自动重启
    )