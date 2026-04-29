# 渐进式重构计划

## 目标
使用 create-llama 的现代架构重构项目，同时保留现有的核心功能（CLI 工具、Jira 集成等）

## 当前项目结构分析

### 保留的核心功能
1. **CLI 工具** (`backend/services/cli/`)
   - Jira 问题深度分析
   - BM25 混合检索
   - Mock 数据支持
   - 输出格式化（Markdown + HTML）

2. **后端服务** (`backend/services/`)
   - 知识库管理
   - 数据源管理
   - 文档处理和索引
   - 报告生成

3. **数据模型** (`backend/models/`)
   - 完整的数据模型定义

### 需要重构的部分
1. **前端界面** - 使用 Next.js + shadcn/ui 替代当前的 Vite + React
2. **API 层** - 采用 create-llama 的 API 路由结构
3. **聊天引擎** - 使用 create-llama 的流式响应和会话管理

## 重构阶段

### Phase 1: 研究和准备（当前阶段）
- [x] 创建 create-llama 示例项目
- [ ] 分析 create-llama 的项目结构
- [ ] 识别可复用的组件和模式
- [ ] 制定详细的迁移计划

### Phase 2: 新项目搭建
- [ ] 在新目录创建 create-llama 项目
- [ ] 配置 TypeScript 和依赖
- [ ] 设置开发环境

### Phase 3: 迁移核心逻辑
- [ ] 将 CLI 工具作为独立模块集成
  - 保持 `backend/services/cli/` 完整性
  - 创建 API 端点调用 CLI 功能
- [ ] 迁移数据模型
  - 转换为 TypeScript 类型定义
  - 保持与 Python 后端的兼容性
- [ ] 迁移后端服务
  - 知识库管理 API
  - 数据源管理 API
  - 文档处理 API

### Phase 4: 前端重构
- [ ] 使用 shadcn/ui 重建界面
  - 聊天页面
  - 知识库管理页面
  - 数据源管理页面
  - 报告页面
- [ ] 集成 create-llama 的聊天组件
- [ ] 实现流式响应

### Phase 5: 功能增强
- [ ] 添加 Jira 问题分析的 Web 界面
- [ ] 可视化混合检索结果
- [ ] 改进报告展示

### Phase 6: 测试和优化
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档更新

## 技术栈对比

### 当前
- Frontend: Vite + React + TypeScript
- Backend: FastAPI + Python
- UI: 自定义 CSS
- State: React hooks

### 目标
- Frontend: Next.js + React + TypeScript
- Backend: FastAPI + Python (保留) + Next.js API Routes (新增)
- UI: shadcn/ui + Tailwind CSS
- State: React hooks + create-llama 的状态管理

## 迁移策略

### 混合架构（推荐）
```
llamaindex_try/
├── backend/              # 保留 Python 后端
│   ├── services/
│   │   └── cli/         # CLI 工具（完全保留）
│   ├── api/             # FastAPI 路由
│   └── models/          # 数据模型
├── frontend-new/        # 新的 Next.js 前端
│   ├── app/             # Next.js App Router
│   ├── components/      # shadcn/ui 组件
│   └── lib/             # 工具函数
└── frontend/            # 旧前端（逐步废弃）
```

### 数据流
```
用户 → Next.js UI → Next.js API Routes → FastAPI Backend → CLI Tools
                                      ↓
                                  LlamaIndex
```

## 关键决策

### 1. 保留 Python 后端
- ✅ CLI 工具已经很成熟
- ✅ LlamaIndex Python 生态更完整
- ✅ 避免重写复杂的检索逻辑

### 2. 使用 Next.js 前端
- ✅ 更好的 SEO 和性能
- ✅ shadcn/ui 提供现代化 UI
- ✅ 与 create-llama 生态集成

### 3. 渐进式迁移
- ✅ 降低风险
- ✅ 可以随时回退
- ✅ 保持项目可用性

## 下一步行动
1. 等待 create-llama 项目创建完成
2. 分析生成的项目结构
3. 创建 POC：在新前端调用现有 CLI 工具
4. 决定是否继续全面重构
