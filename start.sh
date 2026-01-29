#!/bin/bash
# Flask Web Application 启动脚本

PORT=5001

# 检查端口是否被占用
echo "🔍 检查端口 $PORT 是否被占用..."
PID=$(lsof -ti:$PORT)

if [ ! -z "$PID" ]; then
    echo "⚠️  端口 $PORT 已被进程 $PID 占用"
    echo "🔪 正在终止进程 $PID..."
    kill -9 $PID
    sleep 1
    echo "✅ 进程已终止"
fi

# 设置环境变量解决 OpenMP 冲突
export KMP_DUPLICATE_LIB_OK=TRUE

# 激活虚拟环境
source venv/bin/activate

# 启动 Flask 应用
echo "🚀 正在启动 Flask Web 应用..."
echo "📍 本地访问: http://localhost:$PORT"
echo "📍 局域网访问: http://192.168.0.108:$PORT"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python app_web.py
