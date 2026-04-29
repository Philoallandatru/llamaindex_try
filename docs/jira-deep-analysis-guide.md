# Jira 深度分析指南

## 文档概述

本文档总结了 Jira 问题深度分析的核心要点、分析框架、Prompt 设计模式和实施策略。

---

## 一、分析框架

### 1.1 问题类型路由（Issue Type Routing）

系统根据 Jira Issue Type 自动路由到不同的分析 profile：

| Issue Type | Issue Family | 分析路由 | 分析重点 |
|------------|--------------|----------|----------|
| FW Bug / HW Bug / Test Bug | `defect` | 根因分析 (RCA) | 失效机制、根因识别、修复方案 |
| DAS/PRD / MRD | `requirement` | 需求追溯分析 | 规格覆盖、实现状态、差距分析 |
| Requirement Change | `requirement_change` | 需求变更影响分析 | 变更范围、规格影响、兼容性 |
| Component Change | `change_control` | 变更影响分析 | 受影响组件、接口影响、验证策略 |
| Epic / Story / Task | `delivery` | 交付总结 | 进度、依赖、风险 |
| Release | `release` | 发布总结 | 发布范围、质量评估 |

**配置文件**: `packages/schema/jira-issue-type-profiles.json`

**路由逻辑**: `services/connectors/jira/issue_type_profiles.py::route_jira_issue_type()`

---

## 二、分析要点

### 2.1 缺陷根因分析 (Defect RCA)

**分析维度**:

1. **根因识别**
   - 代码逻辑错误
   - 配置错误
   - 时序问题
   - 资源竞争
   - 边界条件处理

2. **失效机制**
   - 问题触发条件
   - 错误传播路径
   - 失效模式分类

3. **影响评估**
   - 严重程度（Critical / Major / Minor）
   - 影响范围（功能模块、性能、数据完整性）
   - 用户可见性

4. **证据链**
   - 引用规格条款（NVMe、SATA、PCIe 标准）
   - 设计文档证据
   - 测试结果和日志
   - 代码片段

5. **修复建议**
   - 具体代码修改点
   - 配置调整方案
   - 测试验证方法
   - 回归测试范围

6. **预防措施**
   - 代码审查要点
   - 测试用例增强
   - 设计模式改进

### 2.2 需求追溯分析 (Requirement Traceability)

**分析维度**:

1. **规格覆盖**
   - 对应的规格条款（章节号、页码）
   - 标准版本（NVMe 1.4 / 2.0, SATA 3.x）
   - 强制性 vs 可选性要求

2. **实现状态**
   - 完全实现 / 部分实现 / 未实现
   - 实现完整性评估
   - 与规格要求的符合度

3. **差距分析**
   - 缺失的功能点
   - 不符合规格的实现
   - 性能指标差距

4. **依赖关系**
   - 硬件依赖（NAND、DRAM、Controller）
   - 固件模块依赖（FTL、GC、Wear Leveling）
   - 上下游需求依赖

5. **测试覆盖**
   - 单元测试覆盖率
   - 集成测试场景
   - 合规性测试（Compliance Test）

6. **风险评估**
   - 技术风险
   - 进度风险
   - 合规性风险

### 2.3 变更影响分析 (Change Impact Analysis)

**分析维度**:

1. **变更范围**
   - 涉及的功能模块
   - 接口变更（API、数据结构）
   - 配置参数变更

2. **规格影响**
   - 新增的合规性要求
   - 受影响的规格条款
   - 标准版本升级影响

3. **架构影响**
   - 系统架构变更
   - 模块交互变更
   - 性能影响（IOPS、延迟、带宽）

4. **兼容性**
   - 向后兼容性
   - 与其他功能的兼容性
   - Host 兼容性

5. **测试影响**
   - 新增测试用例
   - 修改的测试用例
   - 回归测试范围

6. **风险评估**
   - 回归风险
   - 性能风险
   - 稳定性风险

7. **实施建议**
   - 分阶段实施方案
   - 验证策略
   - 回滚方案

---

## 三、Prompt 设计模式

### 3.1 Prompt 结构

标准 Prompt 包含以下部分：

```
1. 角色定义 (Assistant Intro)
2. 任务指令 (Task Instruction)
3. 模式指令 (Mode Instructions)
4. 输出格式 (Output Format)
5. 上下文 (Context)
   - Jira 问题上下文
   - Confluence 证据
   - 规格说明证据
   - 图像证据状态
```

### 3.2 三种 Prompt 模式

#### Strict Mode（严格模式）- 默认

**适用场景**: 合规性报告、正式文档、高风险决策

**核心原则**:
- 如果证据不能直接支持结论，明确说明证据不足
- 不推断未在检索证据中明确体现的事实
- 不超出 Jira 字段和评论的范围推断发布风险
- 当 Jira 提到验证、复测或未解决状态时，不说"无需后续跟进"

**Prompt 指令**:
```
模式：严格证据审查
如果证据不能直接支持结论，请明确说明证据不足。
不要推断未在检索证据中明确体现的事实。
```

#### Balanced Mode（平衡模式）

**适用场景**: 日常工程分析、技术讨论、问题诊断

**核心原则**:
- 区分直接证据和合理推断
- 指出不确定性
- 说明需要哪些额外证据来加强结论

**Prompt 指令**:
```
模式：平衡证据审查
区分直接证据和合理推断。
指出不确定性以及需要哪些额外证据来加强结论。
```

#### Exploratory Mode（探索模式）

**适用场景**: 早期问题探索、头脑风暴、假设验证

**核心原则**:
- 明确标注假设，不作为既定事实呈现
- 仅使用假设来建议后续检查
- 不声称最终结论

**Prompt 指令**:
```
模式：探索性证据审查
明确标注假设，不要将其作为既定事实呈现。
仅使用假设来建议后续检查，而非声称最终结论。
```

### 3.3 分析 Profile 示例

#### 缺陷根因分析 Profile

```python
{
    "label": "根因分析",
    "assistant_intro": "你是一位SSD固件缺陷根因分析专家。",
    "task_instruction": """
基于检索到的Confluence文档和规格说明证据，对此Jira缺陷问题进行深度根因分析。
分析要求：
1. 根因识别：分析可能的根本原因，包括代码逻辑、配置错误、时序问题、资源竞争等
2. 失效机制：解释问题是如何发生的，触发条件和传播路径
3. 影响评估：评估问题的严重程度、影响范围（功能模块、性能、数据完整性）
4. 证据链：引用具体的规格条款、设计文档、测试结果来支撑分析结论
5. 修复建议：提供具体的修复方案，包括代码修改点、配置调整、测试验证方法
6. 预防措施：建议如何避免类似问题再次发生
"""
}
```

#### 需求追溯分析 Profile

```python
{
    "label": "需求追溯分析",
    "assistant_intro": "你是一位SSD需求追溯和差距分析专家。",
    "task_instruction": """
基于检索到的Confluence文档和规格说明证据，对此Jira需求问题进行需求追溯分析。
分析要求：
1. 规格覆盖：识别需求对应的规格条款（NVMe、SATA、PCIe等标准）
2. 实现状态：评估需求的实现完整性，是否完全满足规格要求
3. 差距分析：指出当前实现与规格要求之间的差距
4. 依赖关系：分析需求的上下游依赖，包括硬件依赖、固件模块依赖
5. 测试覆盖：评估测试用例是否充分覆盖需求的各个方面
6. 风险评估：识别需求实现中的潜在风险和不确定性
"""
}
```

### 3.4 输出格式规范

标准输出包含 5 个部分：

```markdown
1. 概述：简明的问题概览（2-3 句话）

2. 跨源证据：引用 Confluence 和规格证据，标注文档 ID
   - Confluence: [文档ID] v[版本]: [证据片段]
   - 规格: [文档ID] v[版本]: [证据片段]

3. 分析：根据问题类型进行根因/追溯/影响分析
   - 根因分析: 失效机制、触发条件、根本原因
   - 追溯分析: 规格覆盖、实现状态、差距
   - 影响分析: 变更范围、受影响组件、风险

4. 差距：缺失的证据或未解答的问题
   - 列出需要补充的证据
   - 指出不确定的技术点

5. 建议：建议的后续步骤
   - 具体的行动项
   - 优先级排序
```

---

## 四、检索策略

### 4.1 跨源检索（Cross-Source Retrieval）

系统对以下来源进行联合检索：

1. **Jira Issue 本身**
   - Issue Fields（Summary, Description, Status, Priority）
   - Comments（评论历史）
   - Attachments（附件元数据）

2. **Confluence 文档**
   - 设计文档
   - 技术规范
   - 测试报告
   - 会议记录

3. **规格文档**
   - NVMe Specification
   - SATA Specification
   - PCIe Specification
   - 其他行业标准

### 4.2 检索增强（Search Enhancement）

针对不同分析章节，系统会增强检索查询：

| 章节名称 | 检索范围提示 | Top-K |
|---------|-------------|-------|
| `rca` | 失效机制、错误代码、根因证据 | 3 |
| `spec_impact` | 规格条款、需求、组件影响证据 | 3 |
| `decision_brief` | 决策、风险、权衡证据 | 3 |
| `general_summary` | 跨源综合概览证据 | 3 |

**实现**: `services/analysis/search_enhancer.py::build_enhanced_search_query()`

### 4.3 检索引擎

- **默认引擎**: BM25（基于词频的经典检索）
- **索引结构**: Page Index（页面级索引）
- **权限控制**: ACL Policy 过滤

---

## 五、证据管理

### 5.1 证据类型

1. **文本证据**
   - 检索到的文档片段（Evidence Span）
   - 引用格式: `[文档ID] v[版本]: [证据片段]`

2. **图像证据**
   - 架构图、流程图、时序图
   - 状态: 已检测 / 未检测 / 无图像

3. **结构化证据**
   - Issue Fields（结构化字段）
   - 规格章节（Clause、Page、Heading）

### 5.2 证据引用格式

```python
{
    "document": "SSD-12345",
    "version": "2024-04-15T10:30:00Z",
    "evidence_span": "FTL mapping table overflow when...",
    "page": 42,
    "clause": "5.3.2",
    "authority_level": "canonical"
}
```

### 5.3 证据质量评估

- **直接证据**: 明确支持结论的证据
- **间接证据**: 需要推理才能支持结论的证据
- **缺失证据**: 需要但未检索到的证据

---

## 六、实施流程

### 6.1 深度分析流程

```
1. 问题路由
   ↓
2. 提取搜索关键词
   ↓
3. 跨源检索（Confluence + 规格）
   ↓
4. 选择分析 Profile
   ↓
5. 构建证据文本
   ↓
6. 生成分析 Prompt
   ↓
7. 生成答案（LLM 或提取式）
   ↓
8. 组装分析报告
```

**核心函数**: `services/analysis/deep_analysis.py::build_deep_analysis_payload()`

### 6.2 批量分析流程

```
1. 时间过滤（updated_from_iso, updated_to_iso）
   ↓
2. 筛选 Jira Issues
   ↓
3. 对每个 Issue 执行深度分析
   ↓
4. 汇总分析结果
   ↓
5. 生成批量报告
```

**核心函数**: `services/analysis/jira_issue_analysis.py::build_jira_batch_spec_report()`

### 6.3 时间过滤选项

| 过滤方式 | 参数 | 示例 |
|---------|------|------|
| 时间窗口 | `updated_from_iso`, `updated_to_iso` | `2024-04-01T00:00:00Z` ~ `2024-04-30T23:59:59Z` |
| 特定日期 | `updated_on_date` | `2024-04-15` |
| 精确时间点 | `updated_at_iso` | `2024-04-15T14:30:00Z` |

---

## 七、答案生成策略

### 7.1 提取式答案（Extractive Answer）- 默认

**特点**:
- 无需 LLM
- 确定性输出
- 快速响应

**输出格式**:
```
深度分析（根因分析）- SSD-12345

找到跨源证据：3条Confluence证据 和2条规格证据。请直接查看引用的证据。

证据：
- CONF-001 v2024-04-10: FTL mapping table design...
- CONF-002 v2024-04-12: Error handling flow...
- NVME-1.4 v2021-06-01: Section 5.3.2 states...
```

### 7.2 LLM 增强答案（LLM-Enhanced Answer）

**特点**:
- 需要显式启用 LLM Backend
- 生成式输出
- 更丰富的分析

**启用方式**:
```python
llm_backend = LLMBackend(
    name="openai-compatible",
    base_url="http://localhost:1234/v1",
    model="qwen2.5-14b-instruct",
    timeout_seconds=60
)

payload = build_deep_analysis_payload(
    jira_document=jira_doc,
    confluence_documents=conf_docs,
    spec_documents=spec_docs,
    allowed_policies={"public"},
    prompt_mode="strict",
    llm_backend=llm_backend
)
```

---

## 八、质量保证

### 8.1 Prompt 质量检查清单

- [ ] 角色定义清晰
- [ ] 任务指令具体
- [ ] 模式指令符合场景
- [ ] 输出格式明确
- [ ] 上下文完整
- [ ] 证据引用规范

### 8.2 分析质量检查清单

- [ ] 问题类型路由正确
- [ ] 检索到相关证据
- [ ] 证据引用准确
- [ ] 分析逻辑清晰
- [ ] 差距识别完整
- [ ] 建议具体可行

### 8.3 常见问题

**Q1: 检索不到相关证据怎么办？**

A: 
1. 检查 ACL Policy 是否正确
2. 扩大检索范围（增加 top_k）
3. 调整搜索关键词
4. 使用 `exploratory` 模式进行假设性分析

**Q2: 如何选择 Prompt 模式？**

A:
- 合规性报告 → `strict`
- 日常工程分析 → `balanced`
- 早期问题探索 → `exploratory`

**Q3: 如何处理多语言证据？**

A: 系统支持中英文混合，Prompt 使用中文，证据保持原语言。

---

## 九、扩展点

### 9.1 自定义分析 Profile

在 `services/analysis/deep_analysis.py` 中添加新的 profile：

```python
ANALYSIS_PROFILES["custom_profile"] = {
    "label": "自定义分析",
    "assistant_intro": "你是一位...",
    "task_instruction": "分析要求：\n1. ...\n2. ..."
}
```

### 9.2 自定义 Issue Type 路由

在 `packages/schema/jira-issue-type-profiles.json` 中添加：

```json
{
  "profiles": {
    "Custom Issue Type": {
      "issue_family": "custom_family",
      "issue_route": "custom_route"
    }
  }
}
```

### 9.3 自定义检索策略

在 `services/analysis/search_enhancer.py` 中扩展：

```python
SECTION_SCOPE_HINTS["custom_section"] = "自定义检索范围提示"
```

---

## 十、参考资料

### 10.1 核心代码文件

| 文件路径 | 功能 |
|---------|------|
| `services/analysis/deep_analysis.py` | 深度分析核心逻辑 |
| `services/analysis/jira_issue_analysis.py` | Jira 问题分析 |
| `services/analysis/jira_profiles.py` | Prompt 构建 |
| `services/connectors/jira/issue_type_profiles.py` | 问题类型路由 |
| `packages/schema/jira-issue-type-profiles.json` | 路由配置 |

### 10.2 相关文档

- `docs/modules/jira-analysis-reporting.md` - 模块契约
- `docs/jira-connector-implementation.md` - Jira 连接器实现
- `docs/ENHANCED_RETRIEVAL.md` - 增强检索策略

### 10.3 测试文件

- `tests/analysis/test_jira_issue_analysis.py` - 单元测试
- `tests/phase3_integration_test.py` - 集成测试
- `test_deep_analysis_e2e.py` - 端到端测试

---

## 附录：完整 Prompt 示例

### 示例 1: 缺陷根因分析（Strict Mode）

```
你是一位SSD固件缺陷根因分析专家。
基于检索到的Confluence文档和规格说明证据，对此Jira缺陷问题进行深度根因分析。
分析要求：
1. 根因识别：分析可能的根本原因，包括代码逻辑、配置错误、时序问题、资源竞争等
2. 失效机制：解释问题是如何发生的，触发条件和传播路径
3. 影响评估：评估问题的严重程度、影响范围（功能模块、性能、数据完整性）
4. 证据链：引用具体的规格条款、设计文档、测试结果来支撑分析结论
5. 修复建议：提供具体的修复方案，包括代码修改点、配置调整、测试验证方法
6. 预防措施：建议如何避免类似问题再次发生

模式：严格证据审查
如果证据不能直接支持结论，请明确说明证据不足。
不要推断未在检索证据中明确体现的事实。

输出格式：
1. 概述：简明的问题概览
2. 跨源证据：引用Confluence和规格证据，标注文档ID
3. 分析：根据问题类型进行根因/追溯/影响分析
4. 差距：缺失的证据或未解答的问题
5. 建议：建议的后续步骤

## Jira问题上下文
# SSD-12345 - FTL Mapping Table Overflow

- Issue: SSD-12345
- Version: 2024-04-15T10:30:00Z
- Source: jira

## Issue Fields
- Assignee: Zhang Wei
- Priority: Critical
- Status: In Progress
- Issue Type: FW Bug

## Jira Markdown
When running sequential write workload with 4KB block size, 
FTL mapping table overflows after 2 hours...

## Confluence证据
- CONF-001 v2024-04-10: FTL mapping table design allocates 256MB...
- CONF-002 v2024-04-12: Error handling flow shows no overflow check...

## 规格说明证据
- NVME-1.4 v2021-06-01: Section 5.3.2 requires proper error handling...

## 图像证据状态
已检测到 2 张图像：架构图、流程图
```

---

**文档版本**: v1.0  
**最后更新**: 2026-04-29  
**维护者**: Codex Team
