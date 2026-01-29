#!/bin/bash
# Flask Web Application 停止脚本

PORT=5001

echo "🔍 查找运行在端口 $PORT 的进程..."
PID=$(lsof -ti:$PORT)

if [ -z "$PID" ]; then
    echo "✅ 没有进程运行在端口 $PORT"
    exit 0
fi

echo "⚠️  发现进程 $PID 运行在端口 $PORT"
echo "🔪 正在终止进程..."
kill -9 $PID

# 等待进程终止
sleep 1

# 验证进程是否已终止
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "❌ 进程终止失败"
    exit 1
else
    echo "✅ 应用已成功停止"
    exit 0
fi
