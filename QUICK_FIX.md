# 快速配置指南

## 1. 调整LLM Timeout

已在 `config.yaml` 和 `analyzer.py` 中设置timeout为300秒（5分钟）：

```yaml
# config.yaml
llm:
  timeout: 300  # 5分钟
```

```python
# analyzer.py
Settings.llm = OpenAILike(
    timeout=300.0,
    request_timeout=300.0
)
```

## 2. 配置ModelScope MinerU

### 快速启用

```bash
# 设置环境变量
export MODEL_SOURCE=modelscope  # Linux/Mac
set MODEL_SOURCE=modelscope     # Windows

# 安装依赖
pip install paddlepaddle modelscope
```

### 自动配置

代码已自动设置ModelScope源：
```python
# mineru_parser.py
os.environ['MODEL_SOURCE'] = 'modelscope'
```

## 3. 测试改进后的工具

```bash
# 清除旧索引
rm -rf data/cli_vector_store data/cli_index_cache.json

# 重新运行（使用更长timeout）
python cli.py TEST-123 --mock --refresh
```

## 预期改进

- ✅ LLM timeout从默认60秒增加到300秒
- ✅ MinerU使用ModelScope镜像（避免HuggingFace连接问题）
- ✅ 自动fallback到pypdf（如果MinerU失败）

## 如果仍然超时

1. **使用更大的模型**
   ```yaml
   llm:
     model: "qwen3.5-7b"  # 或更大的模型
   ```

2. **减少输入context**
   ```yaml
   retrieval:
     similarity_top_k: 5  # 从10减少到5
   ```

3. **使用streaming模式**（需要代码修改）

详细文档：
- `MINERU_MODELSCOPE.md` - MinerU配置
- `RETRIEVAL_CONFIG.md` - 检索配置
- `TEST_REPORT.md` - 测试报告
