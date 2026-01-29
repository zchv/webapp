#!/bin/bash
# Flask Web Application 清理脚本

echo "🧹 开始清理项目..."

# 停止运行中的应用
echo ""
echo "1️⃣  停止运行中的应用..."
bash stop.sh

# 清理 Python 缓存
echo ""
echo "2️⃣  清理 Python 缓存文件..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
echo "✅ Python 缓存已清理"

# 清理日志文件
echo ""
echo "3️⃣  清理日志文件..."
if [ -d "logs" ]; then
    rm -rf logs/*
    echo "✅ 日志文件已清理"
else
    echo "ℹ️  没有日志目录"
fi

# 清理临时文件
echo ""
echo "4️⃣  清理临时文件..."
find . -type f -name ".DS_Store" -delete 2>/dev/null
find . -type f -name "*.tmp" -delete 2>/dev/null
find . -type f -name "*.log" -delete 2>/dev/null
echo "✅ 临时文件已清理"

# 清理上传的临时文件
echo ""
echo "5️⃣  清理上传的临时文件..."
if [ -d "static/uploads" ]; then
    rm -rf static/uploads/*
    echo "✅ 上传文件已清理"
else
    echo "ℹ️  没有上传目录"
fi

echo ""
echo "🎉 清理完成！"
echo ""
echo "💡 提示："
echo "   - 如需重新构建 FAISS 索引，请运行: python build_faiss_index.py"
echo "   - 如需重新安装依赖，请运行: pip install -r requirements.txt"
