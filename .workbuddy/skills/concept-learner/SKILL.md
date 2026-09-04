---
name: concept-learner
description: This skill should be used when the user wants to systematically learn an arbitrary concept and produce a structured, self-contained HTML study guide. It accepts a concept name (any topic — Agent, RAG, Transformer, Skill, attention, vector database, etc.) as input and generates a 7-section HTML file at learning-materials/<slug>.html, covering learning objectives, core questions, structured explanation, application case, concept disambiguation, self-test questions, and verifiable references. Use this skill when the user says "用 concept-learner 学习 X", "/concept-learner X", "帮我系统学习 X 并输出 HTML 资料", or anything similar asking for a complete, browsable study guide for a concept they don't yet understand.
agent_created: true
---

# 概念学习资料生成 Skill (Concept Learner)

## 一、适用场景

本 Skill 用于解决一个具体问题：**让用户对一个陌生的概念，从"听说过"快速达到"能讲、能用、能区分"的水平**。

触发场景（满足任一即可）：

- 用户说"用 concept-learner 学习 X"或 `/concept-learner X`；
- 用户希望系统化掌握某个技术 / 学术 / 业务概念；
- 用户希望为团队沉淀"概念入门手册"，未来可直接分享 HTML 文件。

不适用场景：

- 用户只是想做一句话定义查询（直接调用普通问答即可，不必走 Skill）；
- 用户希望阅读一份**已经存在**的资料（这是查，不是学）。

## 二、输入信息

| 字段         | 类型   | 必填 | 说明                                                                                          |
| ------------ | ------ | ---- | --------------------------------------------------------------------------------------------- |
| `concept`    | string | ✅   | 概念名，如 `Agent`、`RAG`、`Transformer`、`Skill`、`注意力机制` 等任意中英文概念                 |
| `audience`   | enum   | ❌   | 目标读者：`beginner`（默认）/ `intermediate` / `advanced`                                     |
| `focus`      | string | ❌   | 用户指定的侧重点，如"工程实现"、"理论基础"、"行业应用"                                          |
| `output_dir` | path   | ❌   | 默认 `learning-materials/`，文件名 `<slug>.html`（slug：小写、连字符、去空格/特殊字符）          |

如果 `concept` 含义模糊，Skill 应当主动追问用户确认（而不是自行假设）。

## 三、生成步骤

按以下顺序执行，**每一步都不能跳过**：

### Step 1：明确范围
确认概念边界，避免做"百科式"资料。例如学习"Agent"时，要主动声明本文**只讨论** LLM-based Agent，**不涉及**强化学习中的 RL Agent。

### Step 2：检索权威资料
**资料来源要求**（必须满足）：
1. 至少 3 条**可点击**的 URL；
2. 至少 1 条**官方来源**（如模型方文档、维基百科、论文 PDF）；
3. 不接受任何"AI 自行生成的不存在链接"——若检索不到，**宁可少写也不要编**；
4. 使用 `WebSearch` 检索核心定义与最新共识；必要时使用 `WebFetch` 抓取原始页面。

### Step 3：构建学习目标与核心问题
- **学习目标**：3-5 条，用"学完后能做 X"而不是"学完后知道 X"；
- **核心问题**：3-5 个"读者读完后应该能自己回答"的问题。

### Step 4：撰写结构化解释（个人理解）
- 不是教科书复述，而是带着**个人理解**写：用类比、举反例、点出"我当初误解的地方"；
- 必须避免整段照搬 AI 对话结果；
- 解释"为什么这样设计"而不只是"它是什么"。

### Step 5：设计具体应用场景
- 给出一个**真实可验证**的场景（公司名 / 产品名 / 论文标题 / 代码片段）；
- 说明场景的输入、做了什么、产出什么、为什么有效。

### Step 6：辨析容易混淆的边界
- 至少 3 条"容易混淆 / 用错"的边界；
- 每条包含：本概念的边界 vs 误用方式 + 如何判断。

### Step 7：设计自测问题
- 至少 4 道题，覆盖"是什么 / 为什么 / 怎么用 / 怎么区分"四个层级；
- 答案可藏在 `<details>` 标签里，方便读者先做后查。

### Step 8：写入 HTML 文件
- 输出路径：`learning-materials/<slug>.html`；
- 单一 HTML 文件，含内嵌 CSS，**不依赖外部资源**（CDN 例外：Mermaid 用于关系图）；
- 在页脚注明"由 concept-learner Skill 生成于 YYYY-MM-DD"与人类核查说明。

### Step 9：自检（**强制，不可跳过**）

## 四、输出结构

生成的 HTML 文件包含 7 个章节，顺序不可调整：

| # | 章节 | 用途 |
| --- | --- | --- |
| 1 | 学习目标（Objectives） | 读者学完后能做什么 |
| 2 | 核心问题（Core Questions） | 引导主动阅读 |
| 3 | 个人理解（My Interpretation） | 带个人视角的结构化解释 |
| 4 | 应用案例（Application Case） | 一个真实可验证的例子 |
| 5 | 概念辨析（Disambiguation） | 容易混淆的边界 |
| 6 | 自测问题（Self-test） | 检验掌握程度 |
| 7 | 参考来源（References） | 可点击的权威链接 |

> 模板见 `references/template.html`。**生成时必须严格遵循**，仅可改写文案、不可改章节顺序与数量。

## 五、资料来源要求（硬性规则）

1. **必须真实**：每条参考链接都要可以打开，标题与内容一致；
2. **必须可核查**：链接指向公开可访问的页面；
3. **拒绝编造**：不允许出现 `example.com`、`http://...` 这类占位；
4. **优先官方**：官方文档 / 论文 / 维基百科优先级 > 个人博客；
5. **标注日期**：若来源页面会随时间变动（如官方博客），注明访问日期。

## 六、自检要求（强制清单）

生成完成后，**必须**对照以下清单逐项打勾：

- [ ] 7 个章节是否齐全且顺序正确？
- [ ] "学习目标"是否用"能做"而不是"能知道"？
- [ ] "个人理解"是否带主观视角（不是百科复述）？
- [ ] "应用案例"是否真实可验证（包含公司 / 产品 / 代码）？
- [ ] "概念辨析"至少 3 条？
- [ ] "自测问题"至少 4 道且答案可隐藏？
- [ ] "参考来源"链接是否真的能打开？（抽样点击 1-2 个验证）
- [ ] HTML 文件是否单文件可独立打开？无 404 资源？
- [ ] 移动端阅读体验是否正常（字体、行距不溢出）？
- [ ] 文件名是否 `learning-materials/<slug>.html` 且 slug 规范？

如有问题，迭代修正后再交付。**自检未通过不得交付**。

## 七、引用资源

- `references/template.html` — 7 章节 HTML 模板，生成时严格遵循。
