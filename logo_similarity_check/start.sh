#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
# 项目根目录（脚本所在目录的父目录）
PROJECT_DIR=$(cd "$SCRIPT_DIR/.." &>/dev/null && pwd)

PORT=15903

# 关闭指定端口上的进程（兼容Linux和macOS）
echo "Stopping process on port $PORT..."

# 使用多种方法查找进程PID
PID=""

# 方法1: 使用 lsof（macOS和Linux都支持）
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:$PORT)
fi

# 如果 lsof 没找到，尝试其他方法
if [ -z "$PID" ]; then
    # 方法2: 使用 ss（Linux）
    if command -v ss &> /dev/null; then
        PID=$(ss -tlnp | grep ":$PORT" | awk '{print $6}' | awk -F'[=,]' '{print $2}' | head -1)
    fi
fi

# 如果还是没找到，尝试 netstat
if [ -z "$PID" ]; then
    # 方法3: 使用 netstat（macOS和Linux）
    if command -v netstat &> /dev/null; then
        # macOS 和 Linux 的 netstat 输出格式不同，需要分别处理
        OS_TYPE=$(uname)
        if [ "$OS_TYPE" = "Darwin" ]; then
            # macOS
            PID=$(netstat -anp tcp | grep "\.$PORT " | awk '{print $9}' | awk -F'/' '{print $1}')
        else
            # Linux
            PID=$(netstat -tlnp 2>/dev/null | grep ":$PORT" | awk '{print $7}' | awk -F'/' '{print $1}')
        fi
    fi
fi

# 清理可能的空字符
PID=$(echo "$PID" | tr -d '[:space:]')

if [ -n "$PID" ] && [ "$PID" -gt 0 ] 2>/dev/null; then
    kill -9 "$PID" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Process $PID killed"
        # 等待进程完全终止
        sleep 1
    else
        echo "Failed to kill process $PID"
    fi
else
    echo "No process found on port $PORT"
fi

# 启动服务
echo "Starting Logo Similarity Check Service on port $PORT..."
cd "$PROJECT_DIR"

# 查找可用的Python解释器
if command -v python &> /dev/null; then
    python -m logo_similarity_check
elif command -v python3 &> /dev/null; then
    python3 -m logo_similarity_check
else
    echo "Error: Python interpreter not found"
    exit 1
fi