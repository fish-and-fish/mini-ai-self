#!/bin/bash

PORT=15903

# 关闭指定端口上的进程（兼容多种Linux发行版）
echo "Stopping process on port $PORT..."

# 尝试使用 ss 命令（较新的Linux系统）
if command -v ss &> /dev/null; then
    PID=$(ss -tlnp | grep ":$PORT" | awk '{print $6}' | grep -oP '[0-9]+' | head -1)
elif command -v netstat &> /dev/null; then
    # 尝试使用 netstat 命令（较旧的Linux系统）
    PID=$(netstat -tlnp | grep ":$PORT" | awk '{print $7}' | grep -oP '[0-9]+' | head -1)
elif command -v lsof &> /dev/null; then
    # 最后尝试使用 lsof 命令
    PID=$(lsof -ti:$PORT)
else
    echo "Warning: None of ss, netstat, lsof found. Cannot check for existing process."
    PID=""
fi

if [ -n "$PID" ] && [ "$PID" -gt 0 ] 2>/dev/null; then
    kill -9 $PID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Process $PID killed"
    else
        echo "Failed to kill process $PID"
    fi
else
    echo "No process found on port $PORT"
fi

# 启动服务
echo "Starting Logo Similarity Check Service on port $PORT..."
cd /Users/linglong/PycharmProjects/miniai

# 查找可用的Python解释器
if command -v python &> /dev/null; then
    python -m logo_similarity_check
elif command -v python3 &> /dev/null; then
    python3 -m logo_similarity_check
else
    echo "Error: Python interpreter not found"
    exit 1
fi