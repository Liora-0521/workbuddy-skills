---
name: concept-learner
description: This skill should be used when the user provides a concept name and wants systematic, structured learning materials generated for that concept. It produces a Markdown file containing eight sections: definition, core principles, key components, application scenarios, concrete examples, relationships with related concepts, recommended learning path, and references. Use this skill when the user says "学习 X 概念", "教我 X", "用 Skill 学习 X", or anything similar asking for a structured walkthrough of a concept.
agent_created: true
---

# 概念学习资料生成 Skill (Concept Learner)

## 用途

针对任意一个概念（技术 / 学术 / 业务 / 抽象名词），自动生成一份结构化、可复读的学习资料。输出的核心目标：

- 让一个 0 基础读者在 10 分钟内建立对这个概念的"立体认知"；
- 让一个有基础的读者能快速核对"自己是否真的理解了这个概念"；
- 资料以 Markdown 形式持久化在 `learnings/<概念名>.md`，方便后续检索、对比、提交到版本库。

## 何时使用

触发本 Skill 的典型用户意图（任一即可）：

- "用 Skill 学习 Agent / 大模型上下文 / Skill"
- "帮我系统地了解一下 X 这个概念"
- "生成一份 X 概念的学习资料"
- "教我 X，并写成文档"

输入格式约定：`/concept-learner <概念名>` 或者直接说"用 concept-learner 学习 X"。

## 输入

| 字段     | 类型   | 必填 | 说明                                                         |
| -------- | ------ | ---- | ------------------------------------------------------------ |
| 概念名   | string | 是   | 用户给定的概念，例如 `Agent`、`大模型的上下文`、`Skill`、`RAG` |
| 侧重点   | string | 否   | 用户可选指定侧重方向，例如"工程实现"、"理论基础"、"行业应用" |
| 输出路径 | string | 否   | 默认 `learnings/<概念名>.md`（相对当前项目根目录）           |

## 输出

生成一个 Markdown 文件，默认路径为 `<项目根>/learnings/<概念名>.md`。文档结构严格遵循 `references/template.md` 中定义的八个章节，顺序不可调整：

1. **概念定义**（Definition）— 一句话定义 + 通俗解释
2. **核心原理**（Core Principles）— 底层工作机制、最关键的 2-4 条原理
3. **关键组成**（Key Components）— 构成这个概念的模块/要素清单
4. **应用场景**（Application Scenarios）— 在哪些领域、被谁、用来做什么
5. **具体例子**（Examples）— 至少 2 个具体可验证的例子
6. **与其他概念的关系**（Relationships）— 与相近/依赖/对比概念的关系
7. **学习路径**（Learning Path）— 从入门到深入的 3-5 阶段建议
8. **参考资料**（References）— 至少 3 条权威来源链接

## 执行流程

按照以下顺序执行，每一步都不要跳过：

### Step 1: 解析输入

确认概念名（必要时询问用户）；如果用户指定了侧重点/输出路径，记录下来。

### Step 2: 信息检索

为保证资料准确性，必须主动检索信息，而不是仅凭模型先验：

1. 使用 `WebSearch` 检索概念的核心定义、最新共识；
2. 必要时使用 `WebFetch` 拉取权威页面（官方文档、维基百科、知名博客）作为参考；
3. 至少收集 3 条可信来源。

### Step 3: 按模板生成内容

读取 `references/template.md` 模板，按八个章节填充内容。要求：

- **概念定义**：先给一行精炼定义，再用"通俗解释"段落用比喻/类比说明；
- **核心原理**：每条原理独立成段，避免空话，要说明"为什么这样"；
- **关键组成**：用列表呈现，每条配 1-2 句解释；
- **应用场景**：至少 3 个真实场景，避免泛泛而谈；
- **具体例子**：例子必须可验证、可复现，必要时附代码片段或示意图描述；
- **与其他概念的关系**：明确区分"相似概念"、"前置概念"、"后续概念"；
- **学习路径**：分阶段列出，每阶段说明"读什么 / 做什么 / 怎么验证掌握"；
- **参考资料**：用 Markdown 链接，给出标题、来源、URL。

### Step 4: 持久化

将生成的内容写入 `<项目根>/learnings/<概念名>.md`，确保：

- 目录存在（不存在则创建）；
- 文件名使用小写、连字符分隔，去掉空格和特殊字符；
- 文件首行为 H1 标题（`# <概念名>`）；
- 字符编码为 UTF-8。

### Step 5: 自我检查

输出前对照以下检查清单：

- [ ] 八个章节是否齐全？
- [ ] 每个章节是否有实质性内容（非空话、非模板套话）？
- [ ] 例子是否具体可验证？
- [ ] 参考资料是否真实可达？
- [ ] 文件是否已写入磁盘？

如有问题，迭代修正后再交付。

## 引用资源

- `references/template.md` — 学习资料的标准模板，生成时严格遵循。

## 注意事项

- 不要照搬模型先验；对于 AI / LLM / Agent 等快速演进的领域，必须依赖最新检索结果；
- 不要生成虚假参考资料或编造 URL；
- 概念中文名 / 英文名并列时，优先用用户给定的形式作为 H1 标题；
- 默认输出位置在 `<项目根>/learnings/`，若项目根未确定，请先向用户确认。
