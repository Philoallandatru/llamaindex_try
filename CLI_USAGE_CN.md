# Jira深度分析CLI工具 - 使用指南

## 功能概述

这是一个基于LlamaIndex的Jira问题深度分析CLI工具，实现以下流程：

```
Jira Key → 抓取Issue详情 → 检索相似Issue → 检索相关文档 → 
证据聚合 → RCA生成 → 输出Markdown/HTML报告
```

## 已测试功能

✓ CLI参数解析  
✓ YAML配置加载  
✓ 增量索引（避免重复索引）  
✓ Markdown/HTML输出生成  

## 安装

```bash
# 安装依赖
pip install llama-index-readers-jira llama-index-readers-confluence pyyaml

# 或使用项目安装
pip install -e .
```

## 配置

复制并编辑配置文件：

```bash
cp config.yaml.example config.yaml
```

配置示例：

```yaml
jira:
  server_url: "https://your-domain.atlassian.net"
  token: "your-jira-api-token"
  email: "your-email@example.com"
  project_keys: ["PROJ", "DEV"]

confluence:  # 可选
  server_url: "https://your-domain.atlassian.net/wiki"
  token: "your-confluence-api-token"
  email: "your-email@example.com"
  space_keys: ["TECH", "DOCS"]

documents:
  folder: "./documents"  # 本地PDF/Office文档目录

llm:
  base_url: "http://localhost:1234/v1"  # LM Studio地址
  model: "qwen2.5-coder-7b-instruct"
  embedding_model: "BAAI/bge-small-zh-v1.5"

storage:
  vector_store: "./data/cli_vector_store"
  index_cache: "./data/cli_index_cache.json"
  output: "./output"
```

## 使用方法

### 基本分析

```bash
python cli.py PROJ-123
```

### 强制刷新数据源

首次运行会全量拉取，后续只索引新内容。使用 `--refresh` 强制重新索引：

```bash
python cli.py PROJ-123 --refresh
```

### 自定义配置文件

```bash
python cli.py PROJ-123 -c my-config.yaml
```

### 自定义输出目录

```bash
python cli.py PROJ-123 -o ./reports
```

## 分析流程

1. **抓取Jira** - 获取Issue本体、评论、附件
2. **结构化提取** - 解析Issue内容和元数据
3. **检索相似Issue** - 向量检索找到相关问题
4. **检索文档** - 从Wiki/Confluence/本地文档中检索相关内容
5. **证据聚合** - 整合所有信息
6. **RCA生成** - 使用LLM生成根因分析
7. **输出报告** - 生成Markdown和HTML格式报告

## 增量索引机制

- **首次运行**：全量拉取Jira/Confluence/本地文档
- **后续运行**：只索引新增或变更的内容
- **索引状态**：保存在 `data/cli_index_cache.json`
- **强制刷新**：使用 `--refresh` 参数

## 输出格式

分析结果保存在 `output/` 目录（可配置）：

- `{JIRA_KEY}_{timestamp}.md` - Markdown报告
- `{JIRA_KEY}_{timestamp}.html` - HTML报告

报告包含：
- Issue详情和元数据
- 相似Issue列表（带相似度评分）
- 相关文档列表（带相关性评分）
- 根因分析（RCA）
- 行动建议
- 验证步骤

## 前置要求

1. **Python 3.11+**
2. **LM Studio** 运行在 `localhost:1234`（或配置其他LLM端点）
3. **Jira/Confluence API Token**
   - 在 https://id.atlassian.com/manage-profile/security/api-tokens 创建
4. **本地文档**（可选）
   - 支持PDF、DOCX、PPTX、XLSX
   - 使用MinerU解析

## 测试

运行组件测试：

```bash
python test_cli.py
```

## 文件结构

```
cli.py                          # CLI入口
config.yaml                     # 配置文件
backend/services/cli/
  ├── config.py                 # 配置加载
  ├── analyzer.py               # 主分析器
  ├── data_loader.py            # 数据加载（Jira/Confluence/本地）
  ├── index_tracker.py          # 增量索引追踪
  └── output_formatter.py       # 输出格式化
```

## 注意事项

1. 确保LM Studio已启动并加载模型
2. Jira/Confluence token需要有读取权限
3. 首次运行会下载embedding模型（约200MB）
4. 大量文档首次索引可能需要较长时间

## 故障排查

**LM Studio连接失败**
```bash
curl http://localhost:1234/v1/models
```

**Jira认证失败**
- 检查token是否有效
- 确认email和server_url正确

**文档解析失败**
- 确保MinerU已正确安装
- 检查文档格式是否支持
