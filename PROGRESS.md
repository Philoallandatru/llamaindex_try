# LlamaIndex Chat Interface - 开发进度

## ✅ Phase 1: Project Setup & Dependencies (完成)

### 创建的文件：
- `pyproject.toml` - Python 依赖配置
- `.gitignore` - Git 忽略规则
- `.env.example` - 环境变量模板
- `README.md` - 项目文档
- 目录结构：backend/, frontend/, data/, tests/

### 前端初始化：
- Vite + React 19 + TypeScript
- 依赖：@tanstack/react-query, axios, lucide-react

---

## ✅ Phase 2: Document Ingestion with MinerU (完成)

### 创建的模块：

#### 1. MinerU Parser (`backend/services/ingestion/mineru_parser.py`)
- PDF 和 Office 文档解析
- 支持 Python API 和 CLI 两种模式
- 提取文本、表格、图片
- 优雅降级到 pypdf

#### 2. Document Parser (`backend/services/ingestion/document_parser.py`)
- 多格式支持：PDF, DOCX, XLSX, PPTX
- 自动格式检测和路由
- MinerU 主解析器 + pypdf 备用

#### 3. Jira Connector (`backend/services/ingestion/jira_connector.py`)
- 使用 atlassian-python-api
- 支持 JQL 查询
- 项目/状态/日期过滤
- 自动转换为 LlamaIndex Document

#### 4. Confluence Connector (`backend/services/ingestion/confluence_connector.py`)
- Space 和 Page 获取
- CQL 查询支持
- 标签和日期过滤
- 增量同步

#### 5. Document Normalizer (`backend/services/ingestion/normalizer.py`)
- 统一转换为 LlamaIndex Document 格式
- 元数据管理（source_type, timestamps, etc.）
- 智能文档分块

#### 6. Configuration (`backend/config/settings.py`)
- Pydantic Settings 配置管理
- 环境变量加载
- 自动创建必要目录

---

## ✅ Phase 3: LlamaIndex Integration & Vector Store (完成)

### 创建的模块：

#### 1. LLM Configuration (`backend/services/indexing/llm_config.py`)
- LM Studio OpenAI-compatible API 集成
- 可配置 model, temperature, max_tokens
- 连接测试功能

#### 2. Embedding Model (`backend/services/indexing/embeddings.py`)
- HuggingFace 本地 embeddings
- 默认：BAAI/bge-small-zh-v1.5（中英文支持）
- 无需 API 调用

#### 3. Vector Store (`backend/services/indexing/vector_store.py`)
- ChromaDB 持久化存储
- Collection 管理
- 文档 CRUD 操作
- 统计信息

#### 4. **BM25 Retriever** (`backend/services/indexing/bm25_retriever.py`) ⭐
- **关键词全文检索**
- BM25 概率排序算法
- 可配置 k1 (term frequency saturation) 和 b (length normalization)
- 停用词过滤
- 适合精确关键词匹配

#### 5. **Hybrid Retriever** (`backend/services/indexing/hybrid_retriever.py`) ⭐
- **混合检索：BM25 + Vector**
- 可配置权重（默认各 50%）
- 分数归一化和融合
- 结合关键词和语义搜索优势

#### 6. Index Manager (`backend/services/indexing/index_manager.py`)
- 统一索引管理
- 支持 3 种检索模式：
  - `vector`: 仅语义相似度
  - `bm25`: 仅关键词匹配
  - `hybrid`: 混合模式（推荐）
- 文档增删改查
- 索引统计

#### 7. Query Engine (`backend/services/indexing/query_engine.py`)
- 引用追踪查询引擎
- 源文档追踪和相关性评分
- 流式响应支持
- 异步查询支持

---

## 📊 检索模式对比

| 模式 | 优势 | 适用场景 | 示例 |
|------|------|----------|------|
| **Vector** | 语义理解 | 概念查询、改写、多语言 | "什么是机器学习？" 匹配 "AI 和数据科学" |
| **BM25** | 精确匹配 | 技术术语、ID、名称 | "SSD-777" 精确匹配 Issue Key |
| **Hybrid** | 综合最优 | 大多数查询 | 结合两者优势 |

---

## 🎯 核心特性

### ✅ 已实现：
1. **多数据源支持**
   - PDF/Office 文档（MinerU）
   - Jira Issues
   - Confluence Pages

2. **三种检索模式**
   - Vector（语义）
   - BM25（关键词）⭐
   - Hybrid（混合）⭐

3. **本地化部署**
   - LM Studio（本地 LLM）
   - HuggingFace Embeddings（本地）
   - ChromaDB（本地存储）

4. **智能文档处理**
   - 自动格式检测
   - 表格和图片提取
   - 元数据管理
   - 智能分块

---

## 📁 项目结构

```
llamaindex_try/
├── backend/
│   ├── api/                    # FastAPI routes (待实现)
│   ├── services/
│   │   ├── ingestion/          # ✅ 文档解析和连接器
│   │   │   ├── mineru_parser.py
│   │   │   ├── document_parser.py
│   │   │   ├── jira_connector.py
│   │   │   ├── confluence_connector.py
│   │   │   ├── normalizer.py
│   │   │   └── README.md
│   │   ├── indexing/           # ✅ 索引和检索
│   │   │   ├── llm_config.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   ├── bm25_retriever.py      ⭐
│   │   │   ├── hybrid_retriever.py    ⭐
│   │   │   ├── index_manager.py
│   │   │   ├── query_engine.py
│   │   │   └── README.md
│   │   └── chat/               # 待实现
│   ├── models/                 # Pydantic schemas (待实现)
│   └── config/
│       └── settings.py         # ✅ 配置管理
├── frontend/                   # ✅ React + Vite + TypeScript
│   ├── src/
│   └── package.json
├── data/                       # ✅ 本地数据存储
│   ├── uploads/
│   ├── vector_store/
│   └── chat_history/
├── tests/                      # ✅ 单元测试
│   ├── test_ingestion.py
│   └── test_indexing.py
├── pyproject.toml              # ✅ Python 依赖
├── .env.example                # ✅ 环境变量模板
├── .gitignore                  # ✅
├── README.md                   # ✅ 项目文档
└── PROGRESS.md                 # 本文件
```

---

## 🚀 下一步：Phase 4 - Chat Engine & Session Management

### 待实现：
1. **Chat Session Manager**
   - 会话创建/加载/保存
   - 消息历史管理
   - 会话列表和删除

2. **Chat Engine**
   - LlamaIndex ContextChatEngine
   - 对话上下文维护
   - 流式响应

3. **Source Citation Handler**
   - 源文档提取
   - 引用格式化
   - 去重和排序

4. **Message Handler**
   - 输入验证
   - 路由到查询引擎
   - 错误处理

---

## 📝 使用示例

### 初始化索引管理器（混合检索）
```python
from backend.services.indexing.index_manager import create_index_manager

manager = create_index_manager(
    collection_name="documents",
    use_hybrid=True,
    bm25_weight=0.5,    # BM25 权重
    vector_weight=0.5,  # Vector 权重
)
```

### 添加文档
```python
from llama_index.core import Document

documents = [
    Document(text="Python 是一种编程语言", metadata={"source": "doc1"}),
    Document(text="机器学习使用 Python", metadata={"source": "doc2"}),
]

await manager.add_documents(documents)
```

### 查询（混合检索）
```python
query_engine = manager.get_query_engine(
    similarity_top_k=5,
    retrieval_mode="hybrid"  # 或 "vector", "bm25"
)

response = query_engine.query("Python 用于什么？")
print(response)
```

---

## 🎉 已完成功能

- ✅ 项目结构和依赖
- ✅ MinerU PDF/Office 解析
- ✅ Jira/Confluence 连接器
- ✅ 文档标准化
- ✅ LM Studio LLM 集成
- ✅ HuggingFace Embeddings
- ✅ ChromaDB 向量存储
- ✅ **BM25 全文检索** ⭐
- ✅ **混合检索（BM25 + Vector）** ⭐
- ✅ 索引管理器
- ✅ 引用查询引擎

---

## 📊 进度统计

- **Phase 1**: 100% ✅
- **Phase 2**: 100% ✅
- **Phase 3**: 100% ✅
- **Phase 4**: 0% (下一步)
- **Phase 5**: 0%
- **Phase 6**: 0%
- **Phase 7**: 0%

**总体进度**: 3/7 = 43%

---

## 🔧 技术栈

### 后端：
- Python 3.11+
- FastAPI
- LlamaIndex
- ChromaDB
- MinerU
- atlassian-python-api

### 前端：
- React 19
- TypeScript
- Vite
- TanStack Query
- Axios

### AI/ML：
- LM Studio (本地 LLM)
- HuggingFace Embeddings
- BM25 算法
- Vector Similarity

---

生成时间：2026-04-25

---

## ✅ Phase 4: Chat Engine & Session Management (完成)

### 创建的模块：

#### 1. Chat Models (`backend/models/chat.py`)
- **ChatMessage** - 单条消息模型（role, content, timestamp, sources）
- **ChatSession** - 会话模型（session_id, messages, metadata）
- **SendMessageRequest** - 发送消息请求
- **ChatResponse** - 聊天响应
- **Citation** - 源引用模型

#### 2. Session Manager (`backend/services/chat/session_manager.py`)
- 创建/加载/保存/删除会话
- 消息历史管理
- 会话列表和过滤
- JSON 持久化存储（`data/chat_history/`）
- 对话历史检索

#### 3. Citation Handler (`backend/services/chat/citation_handler.py`)
- 从源节点提取引用
- 格式化引用（Markdown, HTML, dict）
- 去重引用
- 创建文本片段
- 相关性评分排序

#### 4. Message Handler (`backend/services/chat/message_handler.py`)
- 输入验证（长度、内容）
- 消息清理
- 可疑内容检测
- 源过滤器提取
- 错误响应格式化

#### 5. Chat Engine (`backend/services/chat/chat_engine.py`)
- LlamaIndex CondensePlusContextChatEngine 集成
- 对话上下文维护（可配置窗口，默认 10 条）
- 流式响应支持
- 自动源引用提取
- 会话持久化

---

## 🎯 Phase 4 核心特性

### ✅ 对话上下文
- 维护最近 N 条消息（默认 10）
- 使用 ChatMemoryBuffer 高效管理
- 基于 token 限制自动修剪

### ✅ 源引用
- 每个响应包含源文档
- 相关性评分
- 自动去重
- 格式化片段和元数据

### ✅ 会话持久化
- JSON 存储在 `data/chat_history/`
- 消息添加时自动保存
- 支持会话元数据
- 高效会话列表

### ✅ 流式支持
- 实时响应生成
- 逐块传输
- 流式完成后添加引用

---

## 📊 更新后的进度统计

- **Phase 1**: 100% ✅
- **Phase 2**: 100% ✅
- **Phase 3**: 100% ✅
- **Phase 4**: 100% ✅
- **Phase 5**: 0% (下一步)
- **Phase 6**: 0%
- **Phase 7**: 0%

**总体进度**: 4/7 = 57%

---

## 📁 更新后的项目结构

```
llamaindex_try/
├── backend/
│   ├── services/
│   │   ├── ingestion/          # ✅ Phase 2
│   │   ├── indexing/           # ✅ Phase 3
│   │   └── chat/               # ✅ Phase 4 (新增)
│   │       ├── session_manager.py
│   │       ├── chat_engine.py
│   │       ├── citation_handler.py
│   │       ├── message_handler.py
│   │       └── README.md
│   ├── models/                 # ✅ Phase 4 (新增)
│   │   ├── chat.py
│   │   └── __init__.py
│   └── config/                 # ✅ Phase 2
├── tests/                      # ✅ 测试覆盖
│   ├── test_ingestion.py
│   ├── test_indexing.py
│   └── test_chat.py            # ✅ Phase 4 (新增)
└── ...
```

---

更新时间：2026-04-25

---

## ✅ Phase 5: FastAPI Backend Routes (完成)

### 创建的模块：

#### 1. API Models (`backend/models/api.py`)
- **BuildIndexRequest/Response** - 索引构建
- **UploadFileRequest/Response** - 文件上传
- **JiraConnectionRequest** - Jira 连接
- **ConfluenceConnectionRequest** - Confluence 连接
- **ConnectionTestResponse** - 连接测试
- **SyncSourceResponse** - 同步响应
- **HealthCheckResponse** - 健康检查
- **ErrorResponse** - 错误响应

#### 2. Chat Routes (`backend/api/chat_routes.py`)
- `POST /api/chat/sessions` - 创建会话
- `GET /api/chat/sessions` - 列出会话
- `GET /api/chat/sessions/{id}` - 获取会话详情
- `DELETE /api/chat/sessions/{id}` - 删除会话
- `POST /api/chat/message` - 发送消息（非流式）
- `GET /api/chat/sessions/{id}/history` - 获取对话历史

#### 3. WebSocket Routes (`backend/api/websocket_routes.py`)
- `WS /ws/chat/{session_id}` - 流式聊天
- 实时消息传输
- 分块响应（chunk/complete/error）
- 自动重连支持

#### 4. Index Routes (`backend/api/index_routes.py`)
- `GET /api/index/stats` - 索引统计
- `POST /api/index/build` - 构建索引
- `DELETE /api/index/clear` - 清空索引
- `GET /api/index/status` - 索引状态

#### 5. Source Routes (`backend/api/source_routes.py`)
- `POST /api/sources/upload` - 上传文件（PDF/Office）
- `POST /api/sources/jira/test` - 测试 Jira 连接
- `POST /api/sources/jira/sync` - 同步 Jira Issues
- `POST /api/sources/confluence/test` - 测试 Confluence 连接
- `POST /api/sources/confluence/sync` - 同步 Confluence Pages
- `GET /api/sources/list` - 列出数据源

#### 6. Main Application (`backend/main.py`)
- FastAPI 应用初始化
- CORS 配置（支持前端跨域）
- 全局异常处理
- 生命周期管理（startup/shutdown）
- 健康检查端点
- 路由挂载

---

## 🎯 Phase 5 核心特性

### ✅ REST API
- 完整的 CRUD 操作
- Pydantic 模型验证
- 自动 API 文档（Swagger UI + ReDoc）
- 错误处理和状态码

### ✅ WebSocket 支持
- 实时流式响应
- 消息类型：chunk, complete, error
- 自动断线重连
- 会话隔离

### ✅ 数据源集成
- 文件上传（multipart/form-data）
- Jira API 集成
- Confluence API 集成
- 连接测试和同步

### ✅ 中间件和配置
- CORS 跨域支持
- 全局异常处理
- 日志记录
- 环境变量配置

---

## 📊 更新后的进度统计

- **Phase 1**: 100% ✅
- **Phase 2**: 100% ✅
- **Phase 3**: 100% ✅
- **Phase 4**: 100% ✅
- **Phase 5**: 100% ✅
- **Phase 6**: 0% (下一步)
- **Phase 7**: 0%

**总体进度**: 5/7 = 71%

---

## 📁 更新后的项目结构

```
llamaindex_try/
├── backend/
│   ├── api/                    # ✅ Phase 5 (新增)
│   │   ├── chat_routes.py
│   │   ├── websocket_routes.py
│   │   ├── index_routes.py
│   │   ├── source_routes.py
│   │   ├── __init__.py
│   │   └── README.md
│   ├── models/                 # ✅ Phase 4 & 5
│   │   ├── chat.py
│   │   ├── api.py              # ✅ Phase 5 (新增)
│   │   └── __init__.py
│   ├── services/
│   │   ├── ingestion/          # ✅ Phase 2
│   │   ├── indexing/           # ✅ Phase 3
│   │   └── chat/               # ✅ Phase 4
│   ├── config/                 # ✅ Phase 2
│   └── main.py                 # ✅ Phase 5 (新增)
├── frontend/                   # ✅ Phase 1
├── data/                       # ✅ Phase 1
└── tests/                      # ✅ Phase 2-4
```

---

## 🚀 API 端点总览

### 总计：20+ 个端点

**Chat (6)**: sessions CRUD, message, history
**WebSocket (1)**: streaming chat
**Index (4)**: stats, build, clear, status
**Source (6)**: upload, jira test/sync, confluence test/sync, list
**Health (2)**: root, health check

---

## 📝 代码统计

- **API 代码**: ~1200 行
- **路由文件**: 5 个
- **模型文件**: 2 个
- **主应用**: 1 个

---

更新时间：2026-04-25

---

## ✅ Phase 6: Frontend - ChatGPT-Style UI (完成)

### 创建的文件：

#### 1. Global Styles (`frontend/src/styles/globals.css`)
- ChatGPT 风格设计
- 深色/浅色主题支持
- 响应式布局
- 动画效果（打字指示器）

#### 2. API Client (`frontend/src/utils/api.ts`)
- Axios 封装
- TypeScript 类型定义
- API 函数：sessions, messages, index, sources
- 类型安全的 API 调用

#### 3. Chat Page (`frontend/src/pages/ChatPage.tsx`)
- 完整的聊天界面
- 侧边栏会话列表
- 消息显示（用户/助手）
- 源引用卡片
- 输入框和发送按钮
- 打字指示器
- TanStack Query 集成

#### 4. App Component (`frontend/src/App.tsx`)
- QueryClient 配置
- 路由设置
- 全局样式导入

#### 5. Main Entry (`frontend/src/main.tsx`)
- React 应用入口
- StrictMode 包装

---

## 🎯 Phase 6 核心特性

### ✅ UI 设计
- ChatGPT 风格界面
- 左侧会话列表
- 右侧聊天区域
- 清晰的消息分隔
- 源引用展示

### ✅ 交互功能
- 创建新会话
- 切换会话
- 发送消息
- 实时响应
- 自动滚动

### ✅ 状态管理
- TanStack Query 数据获取
- React Hooks 状态管理
- 自动缓存和重新验证

### ✅ 响应式设计
- 适配不同屏幕尺寸
- 深色/浅色主题
- 流畅动画

---

## 📊 最终进度统计

- **Phase 1**: 100% ✅
- **Phase 2**: 100% ✅
- **Phase 3**: 100% ✅
- **Phase 4**: 100% ✅
- **Phase 5**: 100% ✅
- **Phase 6**: 100% ✅
- **Phase 7**: 0% (可选)

**总体进度**: 6/7 = 86%

---

## 🎉 核心功能已完成！

### ✅ 后端 (Phase 1-5)
- 文档解析（MinerU + pypdf）
- 多数据源（PDF, Office, Jira, Confluence）
- 三种检索模式（Vector, BM25, Hybrid）
- 对话引擎（上下文管理）
- REST API + WebSocket
- 会话持久化

### ✅ 前端 (Phase 6)
- ChatGPT 风格 UI
- 实时聊天
- 会话管理
- 源引用显示

---

## 🚀 快速启动

### 后端
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[portal-runner]"
python main.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 访问
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 📝 Phase 7 (可选): Integration & Testing

Phase 7 是可选的集成测试和优化阶段，核心功能已经完成！

---

更新时间：2026-04-25
