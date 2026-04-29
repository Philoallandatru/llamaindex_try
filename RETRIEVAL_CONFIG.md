# 检索模式配置指南

## 配置文件位置

编辑 `config.yaml` 中的 `retrieval` 部分：

```yaml
retrieval:
  mode: "hybrid"  # 检索模式: vector, bm25, hybrid
  similarity_top_k: 10  # 返回结果数量
  bm25_weight: 0.7  # BM25权重 (仅hybrid模式)
  vector_weight: 0.3  # 向量权重 (仅hybrid模式)
```

## 三种检索模式

### 1. Vector模式 - 纯语义检索

```yaml
retrieval:
  mode: "vector"
  similarity_top_k: 10
```

**特点:**
- 基于embedding向量相似度
- 理解语义和概念
- 适合概念性查询

**适用场景:**
- "如何优化性能"
- "用户登录流程"
- "数据库连接问题"

**优点:** 理解同义词和相关概念  
**缺点:** 对精确匹配（如ID、代码）效果差

---

### 2. BM25模式 - 纯关键词检索

```yaml
retrieval:
  mode: "bm25"
  similarity_top_k: 10
```

**特点:**
- 基于词频和逆文档频率
- 精确关键词匹配
- 适合技术术语和ID

**适用场景:**
- "PROJ-123"
- "NullPointerException"
- "getUserById"
- "Redis缓存"

**优点:** 精确匹配技术术语  
**缺点:** 不理解语义，无法处理同义词

---

### 3. Hybrid模式 - 混合检索（推荐）

```yaml
retrieval:
  mode: "hybrid"
  similarity_top_k: 10
  bm25_weight: 0.7  # BM25占70%
  vector_weight: 0.3  # Vector占30%
```

**特点:**
- 结合BM25和向量检索
- 使用Reciprocal Rank Fusion融合结果
- 平衡精确匹配和语义理解

**权重配置建议:**

#### 高BM25权重 (0.7-0.8)
```yaml
bm25_weight: 0.7
vector_weight: 0.3
```
**适合:** 
- 技术文档检索
- Bug报告查找
- 包含大量技术术语和ID的场景

#### 平衡权重 (0.5-0.5)
```yaml
bm25_weight: 0.5
vector_weight: 0.5
```
**适合:**
- 通用场景
- 混合查询（既有术语又有概念）

#### 高Vector权重 (0.3-0.4)
```yaml
bm25_weight: 0.3
vector_weight: 0.7
```
**适合:**
- 概念性文档
- 需求分析
- 设计文档检索

---

## 配置示例

### 场景1: Jira Bug分析（推荐高BM25）

```yaml
retrieval:
  mode: "hybrid"
  similarity_top_k: 15
  bm25_weight: 0.75  # 更关注精确匹配
  vector_weight: 0.25
```

**原因:** Bug报告包含大量错误信息、堆栈跟踪、Issue ID等需要精确匹配的内容

### 场景2: 需求文档检索

```yaml
retrieval:
  mode: "hybrid"
  similarity_top_k: 10
  bm25_weight: 0.4
  vector_weight: 0.6  # 更关注语义
```

**原因:** 需求文档更注重概念和业务逻辑，语义理解更重要

### 场景3: 技术规范查找

```yaml
retrieval:
  mode: "hybrid"
  similarity_top_k: 20
  bm25_weight: 0.8  # 高度关注精确匹配
  vector_weight: 0.2
```

**原因:** API名称、配置项、技术术语需要精确匹配

---

## 进度展示

CLI工具现在包含详细的进度展示：

### 分析流程进度条

```bash
$ python cli.py PROJ-123

============================================================
Analyzing PROJ-123
Retrieval mode: hybrid
  BM25 weight: 0.7
  Vector weight: 0.3
============================================================

Analysis pipeline: 100%|████████████| 7/7 [00:15<00:00,  2.14s/it]

============================================================
✓ Analysis complete
  Similar issues found: 5
  Relevant docs found: 8
  Markdown: output/PROJ-123_20260428_120000.md
  HTML: output/PROJ-123_20260428_120000.html
============================================================
```

### 刷新数据源进度条

```bash
$ python cli.py PROJ-123 --refresh

============================================================
FORCE REFRESH MODE
============================================================

Refreshing data sources: 100%|████████| 4/4 [01:30<00:00, 22.5s/it]
  Building index: 100%|████████████| 150/150 [00:45<00:00,  3.33it/s]

✓ Refresh complete: 150 documents indexed
```

---

## 性能调优

### 提高检索速度

```yaml
retrieval:
  similarity_top_k: 5  # 减少返回数量
```

### 提高检索质量

```yaml
retrieval:
  similarity_top_k: 20  # 增加返回数量
  bm25_weight: 0.7  # 根据场景调整
```

### 针对中文内容

```yaml
llm:
  embedding_model: "BAAI/bge-small-zh-v1.5"  # 中文优化模型

retrieval:
  mode: "hybrid"
  bm25_weight: 0.6  # 中文分词可能影响BM25效果
  vector_weight: 0.4
```

---

## 测试不同配置

快速测试不同检索模式的效果：

```bash
# 测试Vector模式
# 编辑config.yaml: mode: "vector"
python cli.py PROJ-123 -o output/vector_test

# 测试BM25模式
# 编辑config.yaml: mode: "bm25"
python cli.py PROJ-123 -o output/bm25_test

# 测试Hybrid模式
# 编辑config.yaml: mode: "hybrid"
python cli.py PROJ-123 -o output/hybrid_test

# 比较三个输出文件的检索结果质量
```

---

## 常见问题

**Q: 权重必须加起来等于1.0吗？**  
A: 是的，`bm25_weight + vector_weight = 1.0`

**Q: 如何知道哪种模式最好？**  
A: 建议先用hybrid模式（0.7/0.3），根据实际检索结果调整

**Q: BM25权重设置为1.0可以吗？**  
A: 可以，但建议直接使用 `mode: "bm25"`

**Q: 检索结果太少怎么办？**  
A: 增加 `similarity_top_k` 值，如从10改为20

**Q: 检索结果不相关怎么办？**  
A: 
- 检查索引是否包含相关文档
- 尝试调整BM25/Vector权重
- 考虑重建索引 `--refresh`
