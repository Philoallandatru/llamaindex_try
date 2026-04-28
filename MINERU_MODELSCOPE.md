# MinerU ModelScope配置指南

## 安装依赖

```bash
# 安装MinerU和ModelScope
pip install magic-pdf[full]
pip install modelscope

# 如果需要GPU加速
pip install paddlepaddle-gpu
# 或CPU版本
pip install paddlepaddle
```

## 配置ModelScope镜像源

MinerU支持从ModelScope下载模型，避免HuggingFace连接问题。

### 方法1: 环境变量

```bash
# Windows
set MODEL_SOURCE=modelscope

# Linux/Mac
export MODEL_SOURCE=modelscope
```

### 方法2: 代码配置

已在 `mineru_parser.py` 中自动设置：
```python
os.environ['MODEL_SOURCE'] = 'modelscope'
```

## ModelScope模型列表

MinerU会自动从ModelScope下载以下模型：

1. **布局检测模型**
   - ModelScope ID: `damo/cv_resnet18_layout-detection`
   - 用途: 检测文档布局结构

2. **公式识别模型**
   - ModelScope ID: `damo/cv_resnet_formula-recognition`
   - 用途: 识别数学公式

3. **表格识别模型**
   - ModelScope ID: `damo/cv_resnet_table-recognition`
   - 用途: 提取表格内容

## 首次运行

首次运行时，MinerU会自动从ModelScope下载模型：

```bash
# 测试MinerU
python cli.py TEST-123 --mock --refresh
```

模型会下载到：
- Windows: `C:\Users\<用户>\.cache\modelscope\`
- Linux: `~/.cache/modelscope/`

## 配置文件

`mineru_config.yaml` 包含MinerU的详细配置：

```yaml
model_config:
  model_source: "modelscope"  # 使用ModelScope镜像
  layout_model: "damo/cv_resnet18_layout-detection"
  formula_model: "damo/cv_resnet_formula-recognition"
  table_model: "damo/cv_resnet_table-recognition"

parse_config:
  output_format: "markdown"
  extract_images: true
  extract_tables: true
  recognize_formula: true
  dpi: 200

performance:
  use_gpu: false  # 改为true启用GPU
  batch_size: 1
  timeout: 300
```

## 性能优化

### 使用GPU加速

```bash
# 安装GPU版本PaddlePaddle
pip install paddlepaddle-gpu

# 修改配置
# mineru_config.yaml: use_gpu: true
```

### 调整超时时间

在 `config.yaml` 中已设置：
```yaml
llm:
  timeout: 300  # 5分钟
```

## 故障排查

### 模型下载失败

```bash
# 手动设置ModelScope镜像
export MODEL_SOURCE=modelscope

# 清除缓存重新下载
rm -rf ~/.cache/modelscope/
```

### PaddlePaddle错误

```bash
# 重新安装PaddlePaddle
pip uninstall paddlepaddle paddlepaddle-gpu
pip install paddlepaddle  # 或 paddlepaddle-gpu
```

### 内存不足

```yaml
# 减小batch_size
performance:
  batch_size: 1
```

## 测试MinerU

```bash
# 测试单个PDF
python -c "
from backend.services.ingestion.mineru_parser import MinerUParser
from pathlib import Path

parser = MinerUParser()
result = parser.parse_pdf(Path('documents/test.pdf'))
print(f'Parsed {len(result[\"text\"])} characters')
print(f'Found {len(result[\"tables\"])} tables')
"
```

## 与pypdf对比

| 特性 | MinerU | pypdf |
|------|--------|-------|
| 文本提取 | ✓ | ✓ |
| 表格提取 | ✓ | ✗ |
| 图片提取 | ✓ | ✗ |
| 公式识别 | ✓ | ✗ |
| 布局保持 | ✓ | ✗ |
| 速度 | 慢 | 快 |
| 依赖 | 多 | 少 |

## 建议

1. **开发环境**: 使用pypdf (快速，依赖少)
2. **生产环境**: 使用MinerU (质量高，功能全)
3. **混合模式**: 当前实现自动fallback到pypdf
