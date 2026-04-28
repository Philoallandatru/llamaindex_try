"""
文档索引构建流程说明

## 支持的文档格式

### 1. PDF文档 (.pdf)
- 主解析器: MinerU (支持表格、图片提取)
- 备用解析器: pypdf (纯文本提取)
- 特性: 按页分割，保留页码信息

### 2. Office文档
- Word: .docx, .doc
- Excel: .xlsx, .xls  
- PowerPoint: .pptx, .ppt
- 解析器: MinerU (必需)
- 特性: 提取文本、表格、元数据

### 3. 文本文档
- 格式: .txt, .md, .json
- 解析器: 内置文本读取
- 特性: 直接读取UTF-8编码文本

## 索引构建流程

### 自动增量索引

1. **首次运行** (无缓存)
   ```bash
   python cli.py PROJ-123
   ```
   - 扫描 documents/ 目录下所有支持的文件
   - 逐个解析文档 (MinerU/pypdf/text)
   - 生成LlamaIndex Document对象
   - 构建向量索引 (ChromaDB)
   - 记录已索引文件到 index_cache.json

2. **后续运行** (有缓存)
   ```bash
   python cli.py PROJ-456
   ```
   - 检查 index_cache.json
   - 只处理新增或未索引的文件
   - 增量更新向量索引

3. **强制全量重建**
   ```bash
   python cli.py PROJ-789 --refresh
   ```
   - 清空索引缓存
   - 重新解析所有文档
   - 重建完整索引

### 文档处理细节

**PDF处理:**
```
file.pdf 
  → MinerU解析 
  → 提取: 文本 + 表格 + 图片
  → 生成多个Document:
     - 主文档 (全文)
     - 表格文档 (每个表格独立)
  → 添加metadata: source, page, parser, has_tables
```

**Office处理:**
```
file.docx
  → MinerU解析
  → 提取: 文本 + 表格 + 格式
  → 生成Document with metadata
```

**文本处理:**
```
file.txt
  → 直接读取UTF-8
  → 单个Document
  → metadata: source, file_name
```

### 索引存储结构

```
data/
├── cli_vector_store/          # ChromaDB向量存储
│   ├── chroma.sqlite3         # 向量数据库
│   └── ...
└── cli_index_cache.json       # 索引追踪缓存
    {
      "jira_issues": {
        "PROJ-123": {
          "indexed_at": "2026-04-28T10:00:00",
          "project": "PROJ"
        }
      },
      "confluence_pages": {
        "12345": {
          "indexed_at": "2026-04-28T10:01:00",
          "space": "TECH"
        }
      },
      "documents": {
        "specs/design.pdf": {
          "indexed_at": "2026-04-28T10:02:00",
          "path": "/full/path/to/design.pdf"
        }
      }
    }
```

## 使用示例

### 准备文档目录

```bash
mkdir -p documents
cp /path/to/specs/*.pdf documents/
cp /path/to/docs/*.docx documents/
```

### 首次索引

```bash
# 会自动索引 documents/ 下所有文件
python cli.py PROJ-123
```

输出:
```
Loading Jira issues...
Loading Confluence pages...
Loading local documents...
Indexing 15 new documents...
1. Fetching PROJ-123...
2. Retrieving similar issues...
3. Retrieving relevant documentation...
4. Generating RCA...

Analysis complete
  Markdown: output/PROJ-123_20260428_110000.md
  HTML: output/PROJ-123_20260428_110000.html
```

### 添加新文档后

```bash
# 只会索引新增的文件
cp new-spec.pdf documents/
python cli.py PROJ-456
```

输出:
```
Indexing 1 new documents...  # 只索引 new-spec.pdf
...
```

### 修改文档后重建索引

```bash
# 文档内容变更后需要强制刷新
python cli.py PROJ-789 --refresh
```

## 性能优化

1. **增量索引**: 避免重复处理已索引文档
2. **并行处理**: 可扩展为多线程解析
3. **缓存机制**: index_cache.json 记录索引状态
4. **分块存储**: 大文档按页/段落分割，提高检索精度

## 故障处理

**MinerU解析失败:**
- PDF自动回退到pypdf
- Office文档会报错（需要MinerU）

**文档编码问题:**
- 文本文件必须是UTF-8编码
- 非UTF-8会导致解析失败

**索引损坏:**
```bash
# 删除索引重建
rm -rf data/cli_vector_store data/cli_index_cache.json
python cli.py PROJ-123 --refresh
```
"""