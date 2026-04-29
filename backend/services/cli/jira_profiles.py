"""Jira 问题分析 Profile 定义"""

from typing import Dict, Literal

# 问题类型到分析路由的映射
ISSUE_TYPE_ROUTING = {
    # 缺陷类
    "FW Bug": {"family": "defect", "route": "rca"},
    "HW Bug": {"family": "defect", "route": "rca"},
    "Test Bug": {"family": "defect", "route": "rca"},
    "Bug": {"family": "defect", "route": "rca"},

    # 需求类
    "DAS": {"family": "requirement", "route": "requirement_trace"},
    "PRD": {"family": "requirement", "route": "requirement_trace"},
    "MRD": {"family": "requirement", "route": "requirement_trace"},
    "Requirement": {"family": "requirement", "route": "requirement_trace"},

    # 变更类
    "Requirement Change": {"family": "requirement_change", "route": "change_impact"},
    "Component Change": {"family": "change_control", "route": "change_impact"},
    "Change Request": {"family": "change_control", "route": "change_impact"},

    # 交付类
    "Epic": {"family": "delivery", "route": "delivery_summary"},
    "Story": {"family": "delivery", "route": "delivery_summary"},
    "Task": {"family": "delivery", "route": "delivery_summary"},

    # 发布类
    "Release": {"family": "release", "route": "release_summary"},
}

# 分析 Profile 定义
ANALYSIS_PROFILES: Dict[str, Dict] = {
    "rca": {
        "label": "根因分析",
        "assistant_intro": "你是一位SSD固件缺陷根因分析专家。",
        "task_instruction": """基于检索到的Confluence文档和规格说明证据，对此Jira缺陷问题进行深度根因分析。

分析要求：
1. 根因识别：分析可能的根本原因，包括代码逻辑、配置错误、时序问题、资源竞争等
2. 失效机制：解释问题是如何发生的，触发条件和传播路径
3. 影响评估：评估问题的严重程度、影响范围（功能模块、性能、数据完整性）
4. 证据链：引用具体的规格条款、设计文档、测试结果来支撑分析结论
5. 修复建议：提供具体的修复方案，包括代码修改点、配置调整、测试验证方法
6. 预防措施：建议如何避免类似问题再次发生"""
    },

    "requirement_trace": {
        "label": "需求追溯分析",
        "assistant_intro": "你是一位SSD需求追溯和差距分析专家。",
        "task_instruction": """基于检索到的Confluence文档和规格说明证据，对此Jira需求问题进行需求追溯分析。

分析要求：
1. 规格覆盖：识别需求对应的规格条款（NVMe、SATA、PCIe等标准）
2. 实现状态：评估需求的实现完整性，是否完全满足规格要求
3. 差距分析：指出当前实现与规格要求之间的差距
4. 依赖关系：分析需求的上下游依赖，包括硬件依赖、固件模块依赖
5. 测试覆盖：评估测试用例是否充分覆盖需求的各个方面
6. 风险评估：识别需求实现中的潜在风险和不确定性"""
    },

    "change_impact": {
        "label": "变更影响分析",
        "assistant_intro": "你是一位SSD变更影响分析专家。",
        "task_instruction": """基于检索到的Confluence文档和规格说明证据，对此Jira变更问题进行变更影响分析。

分析要求：
1. 变更范围：涉及的功能模块、接口变更、配置参数变更
2. 规格影响：新增的合规性要求、受影响的规格条款、标准版本升级影响
3. 架构影响：系统架构变更、模块交互变更、性能影响（IOPS、延迟、带宽）
4. 兼容性：向后兼容性、与其他功能的兼容性、Host兼容性
5. 测试影响：新增测试用例、修改的测试用例、回归测试范围
6. 风险评估：回归风险、性能风险、稳定性风险
7. 实施建议：分阶段实施方案、验证策略、回滚方案"""
    },

    "delivery_summary": {
        "label": "交付总结",
        "assistant_intro": "你是一位项目交付分析专家。",
        "task_instruction": """基于检索到的Confluence文档和Jira相关问题，对此交付项进行总结分析。

分析要求：
1. 交付范围：完成的功能点、交付的组件
2. 进度状态：计划进度、实际进度、延期情况
3. 依赖关系：上游依赖、下游依赖、阻塞问题
4. 质量评估：测试覆盖率、缺陷密度、遗留问题
5. 风险识别：技术风险、进度风险、资源风险
6. 后续计划：待完成工作、优化建议"""
    },

    "release_summary": {
        "label": "发布总结",
        "assistant_intro": "你是一位产品发布分析专家。",
        "task_instruction": """基于检索到的Confluence文档和Jira相关问题，对此发布进行总结分析。

分析要求：
1. 发布范围：包含的功能、修复的缺陷、性能改进
2. 质量评估：测试覆盖率、缺陷收敛情况、遗留问题
3. 合规性：规格符合性、认证状态
4. 兼容性：向后兼容性、Host兼容性
5. 风险评估：已知风险、缓解措施
6. 发布建议：发布准备度、注意事项"""
    }
}

# Prompt 模式定义
PROMPT_MODES = {
    "strict": {
        "label": "严格证据审查",
        "instruction": """模式：严格证据审查
如果证据不能直接支持结论，请明确说明证据不足。
不要推断未在检索证据中明确体现的事实。
不要超出 Jira 字段和评论的范围推断发布风险。
当 Jira 提到验证、复测或未解决状态时，不说"无需后续跟进"。"""
    },

    "balanced": {
        "label": "平衡证据审查",
        "instruction": """模式：平衡证据审查
区分直接证据和合理推断。
指出不确定性以及需要哪些额外证据来加强结论。"""
    },

    "exploratory": {
        "label": "探索性证据审查",
        "instruction": """模式：探索性证据审查
明确标注假设，不要将其作为既定事实呈现。
仅使用假设来建议后续检查，而非声称最终结论。"""
    }
}

# 输出格式模板
OUTPUT_FORMAT = """
输出格式：
1. 概述：简明的问题概览（2-3句话）

2. 跨源证据：引用Confluence和规格证据，标注文档ID
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
"""


def route_issue_type(issue_type: str) -> str:
    """根据 Issue Type 路由到分析 Profile"""
    routing = ISSUE_TYPE_ROUTING.get(issue_type, {"route": "rca"})
    return routing["route"]


def build_analysis_prompt(
    issue_type: str,
    issue_content: str,
    similar_issues: list,
    relevant_docs: list,
    mode: Literal["strict", "balanced", "exploratory"] = "strict"
) -> str:
    """构建分析 Prompt"""

    # 路由到对应的 Profile
    profile_key = route_issue_type(issue_type)
    profile = ANALYSIS_PROFILES[profile_key]

    # 获取模式指令
    mode_config = PROMPT_MODES[mode]

    # 构建 Prompt
    prompt = f"""{profile['assistant_intro']}

{profile['task_instruction']}

{mode_config['instruction']}

{OUTPUT_FORMAT}

## Jira问题上下文

{issue_content}

## 相似问题证据

"""

    # 添加相似问题
    if similar_issues:
        for i, issue in enumerate(similar_issues, 1):
            prompt += f"\n### 相似问题 {i}\n"
            prompt += f"- Issue Key: {issue.get('key', 'N/A')}\n"
            prompt += f"- Summary: {issue.get('summary', 'N/A')}\n"
            prompt += f"- Status: {issue.get('status', 'N/A')}\n"
            prompt += f"- 相似度: {issue.get('score', 0):.2f}\n"
    else:
        prompt += "\n未找到相似问题。\n"

    # 添加相关文档
    prompt += "\n## Confluence和规格文档证据\n"
    if relevant_docs:
        for i, doc in enumerate(relevant_docs, 1):
            prompt += f"\n### 文档 {i}\n"
            prompt += f"- 来源: {doc.get('source', 'N/A')}\n"
            prompt += f"- 标题: {doc.get('title', 'N/A')}\n"
            prompt += f"- 相关度: {doc.get('score', 0):.2f}\n"
            prompt += f"- 内容摘要:\n{doc.get('text', 'N/A')[:500]}...\n"
    else:
        prompt += "\n未找到相关文档。\n"

    prompt += "\n请基于以上证据进行深度分析。\n"

    return prompt
