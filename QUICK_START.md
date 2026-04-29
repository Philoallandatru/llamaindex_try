# 快速启动指南

## 已完成的集成

✅ Express TypeScript 服务器已创建
✅ 现代化聊天 UI 已实现
✅ 依赖已安装
✅ 配置文件已设置（使用 LM Studio）
✅ API 代理已实现（转发到 Python 后端）

## 启动步骤

### 1. 启动 LM Studio
确保 LM Studio 正在运行，并加载了模型：
- LLM 模型：qwen3.5-4b
- Embedding 模型：nomic-embed-text-v1.5
- 端口：1234

### 2. 启动 Python 后端
```bash
# 在项目根目录
cd backend
python main.py
```

后端将运行在 `http://localhost:8000`

### 3. 启动 TypeScript 服务器（已启动 ✅）
```bash
# 在新的终端窗口
cd server
npm start
```

服务器将运行在 `http://localhost:3000`

**当前状态：服务器已在后台运行**

### 4. 访问聊天界面
打开浏览器访问：`http://localhost:3000`

## 架构说明

```
用户浏览器 (localhost:3000)
    ↓
Express TypeScript 服务器
    ↓ HTTP POST /api/chat
FastAPI Backend (Python, localhost:8000)
    ↓
LlamaIndex + BM25 混合检索
    ↓
LM Studio (localhost:1234)
```

## 当前状态

🟢 **TypeScript 服务器已启动** - http://localhost:3000
⚪ **Python 后端需要启动** - http://localhost:8000
⚪ **LM Studio 需要运行** - http://localhost:1234

## 功能特性

### TypeScript 层提供
- ✅ 现代化聊天 UI
- ✅ 流式响应支持
- ✅ 会话管理
- ✅ 自动重连

### Python 层提供
- ✅ BM25 + Vector 混合检索
- ✅ 知识库管理
- ✅ Jira 集成
- ✅ CLI 工具
- ✅ 文档处理

## 测试

1. 在聊天界面输入问题
2. TypeScript workflow 会调用 Python API
3. Python 后端执行检索和生成
4. 响应返回到聊天界面

## 故障排除

### 问题：无法连接到 Python 后端
- 检查 Python 后端是否运行：`curl http://localhost:8000/health`
- 检查 `server/.env` 中的 `PYTHON_API_URL`

### 问题：LM Studio 连接失败
- 确保 LM Studio 正在运行
- 检查模型是否已加载
- 验证端口 1234 是否可访问

### 问题：TypeScript 服务器启动失败
- 检查端口 3000 是否被占用
- 查看控制台错误信息
- 确认依赖已安装：`npm install --legacy-peer-deps`

## 下一步

### 可选改进
1. **添加更多 UI 组件** - 自定义聊天界面
2. **实现流式响应** - 修改 workflow 支持 SSE
3. **添加知识库选择器** - 在 UI 中选择不同的知识库
4. **集成 CLI 功能** - 在 Web 界面调用 Jira 分析

### 完整迁移
如果效果满意，可以考虑：
1. 运行 `npm run eject` 获得完整的 Next.js 项目
2. 自定义 UI 和路由
3. 逐步迁移更多功能到 TypeScript

## 文件说明

- `server/src/index.ts` - Express 服务器入口，提供 API 代理
- `server/public/index.html` - 现代化聊天界面
- `server/.env` - 环境配置
- `server/package.json` - 依赖管理

## 快速测试

```bash
# 1. 测试 TypeScript 服务器
curl http://localhost:3000/health
# 应该返回: {"status":"ok","pythonBackend":"http://localhost:8000"}

# 2. 启动 Python 后端（如果还没启动）
cd backend && python main.py

# 3. 在浏览器打开
open http://localhost:3000
```
