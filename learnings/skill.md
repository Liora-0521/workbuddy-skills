# Skill

> **一种以 SKILL.md 为核心的结构化指令包，把"如何做某类事"的知识和工作流打包给 Agent，让通用 Agent 变成领域专家。**

**通俗解释**：Agent 是一个"什么都能干的实习生"，Skill 则是递给他的《岗位操作手册》——你给他《代码审查手册》，他就成了"代码审查专家"；你给他《SQL 调优手册》，他就成了"SQL 调优专家"。同一份手册可以在不同的 Agent（Claude Code / Codex CLI / Gemini CLI）间共享。

---

## 1. 概念定义

- **正式定义**：Skill 是一种**结构化的指令包**，通过 `SKILL.md` 文件及其关联资源（脚本、参考资料、资产）为 Agent 提供针对特定任务类型的标准化工作流程、知识与最佳实践。Skill 通过**渐进式加载**（metadata → body → 资源）管理上下文消耗。
- **通俗定义**：Skill = 给 Agent 看的"岗位手册"，把"做某类事的标准流程"打包成一个可安装、可分享的模块。
- **关键术语**：SKILL.md、Progressive Disclosure、Agent Skill、Project Skill、User Skill、Slash Command、MCP。

> Anthropic 的官方比喻：Skill 是给 Agent 的"菜谱"——里面写明完成某任务需要的工具、步骤、火候（最佳实践）。

## 2. 核心原理

### 原理 1：Skill 与 Agent 是"两层"关系
Agent 是"运行时"（如 Claude Code、Codex CLI），Skill 是"装在 Agent 里的指令文件"。Skill 不替代 Agent，而是让已有的 Agent 在特定任务上表现更好。  
*为什么这样*：Agent 的通用推理能力是"大脑"，Skill 是"专科训练手册"——大脑 + 手册 = 专科医生。脱离 Agent 的 Skill 没有任何作用。

### 原理 2：渐进式披露（Progressive Disclosure）节省上下文
Skill 的内容分三层加载：  
- **第一层**（~100 词）：始终在上下文里的 metadata（name + description），让 Agent 知道"这个 Skill 是干嘛的"。  
- **第二层**（<5K 词）：任务匹配时才加载的 SKILL.md 正文，包含工作流指令。  
- **第三层**（无限制）：SKILL.md 显式引用时才加载的脚本 / 参考资料 / 资产。  
*为什么这样*：Agent 的上下文窗口有限，不能把所有可能的 Skill 都塞进去；分层加载是"按需供给"。

### 原理 3：Skill 由模型自动触发，而非显式命令
与 `/command` 的显式触发不同，Skill 的触发由**语义匹配**驱动——用户说"这段代码太乱了"，Agent 会自动调用代码格式化 Skill。  
*为什么这样*：显式命令需要用户记忆所有命令名，认知负担重；语义触发让 Skill "无感"地被调用。

### 原理 4：Skill 是可分享、可版本化的模块
Skill 以纯文本 Markdown 文件形式存在，可放入 Git 仓库、可装到不同 Agent、可被团队复用。它不是黑盒 API，是透明的"文档型软件"。  
*为什么这样*：传统软件能力要靠 SDK/API 分发，Skill 把"能力"降低到"文档级"门槛，任何会写 Markdown 的人都能创建和分发。

## 3. 关键组成

- **SKILL.md（必需）**：Skill 的核心文件，YAML frontmatter（name、description）+ Markdown 正文（工作流指令）。
- **scripts/（可选）**：可执行脚本（Python / Bash），用于确定性操作（如 PDF 旋转、格式转换）。脚本可不读入上下文直接执行。
- **references/（可选）**：参考文档，按需加载（如数据库 schema、API 文档、政策文件），避免 SKILL.md 过于臃肿。
- **assets/（可选）**：用于输出的资产文件（如 logo、PPT 模板、前端脚手架），不读入上下文但参与最终产物。
- **frontmatter 字段**：name（必需）、description（必需，决定何时触发）、agent_created（agent 创建时必须为 true）、可选 read_when、metadata。
- **触发描述（description）**：用第三人称写，明确"什么场景下用这个 Skill"，决定 Agent 是否会自动调用。

## 4. 应用场景

- **场景 1：代码审查 Skill** —— 在 Claude Code / Codex 中安装 `/code-review` Skill，Agent 在每次写完代码后自动按团队标准审查（命名、安全、可测性）。
- **场景 2：领域知识库 Skill** —— 把公司内部的产品手册、合规规则、API 文档打包成 Skill，让 Agent 在回答业务问题时自动加载正确上下文。
- **场景 3：报告生成 Skill** —— 把日报 / 周报 / 投研报告的固定格式与数据源打包，Agent 自动按模板填数据生成文档。
- **场景 4：调试 / 排错 Skill** —— 把团队多年积累的故障排查 SOP 做成 Skill，Agent 收到"线上挂了"时自动按步骤排查。
- **场景 5：多 Agent 系统的"分工配置"** —— 在多 Agent 系统中，每个子 Agent（如代码 Agent、写作 Agent、测试 Agent）各自安装对应的 Skill，形成"Agent + Skill = 角色"的模式。
- **场景 6：本仓库的概念学习 Skill** —— `concept-learner` 这个 Skill 本身就是一个例子：输入概念名，输出结构化学习资料。

## 5. 具体例子

### 例子 1：一个最简 Skill 的目录结构

```
my-skill/
├── SKILL.md            # 必需
├── scripts/
│   └── helper.py       # 可选，工具脚本
├── references/
│   └── template.md     # 可选，模板/参考资料
└── assets/
    └── logo.png        # 可选，输出资产
```

`SKILL.md` 示例：

```markdown
---
name: my-skill
description: This skill should be used when the user wants to do X, Y, or Z. It produces...
agent_created: true
---

# My Skill

## 用途
做 X。

## 何时使用
用户说 "X" 时。

## 执行流程
1. 调用 scripts/helper.py
2. 按 references/template.md 生成输出
3. 返回结果

## 注意事项
- 不要做 A
- 始终做 B
```

### 例子 2：Skill vs Command vs Agent 的对比

```
同一个脚本 format_code.py，可以打包成三种形态：

做成 Command (/fmt)：
  - 用户必须手动输入 /fmt 才运行
  - 单个 .md 文件
  - 触发：显式
  - 比喻：墙上贴的便条 "记得运行 /fmt"

做成 Skill (代码格式化 Skill)：
  - 用户说 "这段代码太乱了"，Claude 自动运行
  - 目录 + SKILL.md
  - 触发：语义匹配
  - 比喻：贴在桌面上的自动感应贴纸

做成 Agent (代码格式化子 Agent)：
  - 独立上下文里运行，主对话不被污染
  - 适合"需要隔离大任务"场景
  - 比喻：请了一位专门做代码格式化的同事
```

### 例子 3：本仓库的 concept-learner Skill

```
目录：.workbuddy/skills/concept-learner/
├── SKILL.md              # 描述触发条件、工作流、引用 resources
└── references/
    └── template.md       # 学习资料的八章节模板

调用流程：
  用户：/concept-learner Agent
  Skill 工作流：
    1. 用 WebSearch 检索 "Agent" 的权威定义
    2. 按 template.md 的八章节填充内容
    3. 写入 learnings/agent.md
    4. 自我检查：八章节齐全、例子可验证、参考资料真实
```

## 6. 与其他概念的关系

- **相似概念 vs Command / Slash Command**：Command 是用户显式触发（`/cmd`）；Skill 是语义触发（"自动匹配"）。Command 是简单提示词封装，Skill 是复杂能力封装。
- **相似概念 vs Agent**：Agent 是**运行时**（能推理、能执行），Skill 是**指令文件**（告诉 Agent 怎么做）。Skill 不替代 Agent——Skill 装进 Agent 才有效。
- **相似概念 vs Subagent**：Subagent 是隔离上下文的"子 Agent"，Skill 是"主 Agent 的操作手册"。Subagent 是"另一个大脑"，Skill 是"同一大脑的不同模式"。
- **相似概念 vs MCP Server**：MCP 提供"工具和数据接入能力"（让 Agent 能做 X），Skill 提供"流程和知识"（让 Agent 知道何时 / 怎么做 X）。两者是正交的能力层。
- **相似概念 vs Prompt**：Prompt 是单次对话的输入指令；Skill 是跨对话、可复用、可版本化的结构化指令集。
- **相似概念 vs Rule**：Rule 通常绑定项目（agent.md / project_rules），用于项目级强约束；Skill 是更通用的领域能力，可在多个项目复用。
- **前置概念**：要理解 Skill，先要理解 Agent、LLM、Prompt Engineering、Function Calling。
- **后续概念**：掌握 Skill 之后，建议继续学习 Multi-Agent + Skill 组合、MCP 协议、Context Engineering。

## 7. 学习路径

| 阶段 | 目标 | 推荐资料 | 验证方式 |
| ---- | ---- | -------- | -------- |
| 入门 | 知道 Skill 是什么 | Anthropic《Skills Explained》、Claude 官方博客 | 能讲出 Skill 与 Command 的区别 |
| 基础 | 读懂 SKILL.md 的 frontmatter | Claude Code / Codex CLI 文档中的 Skill 章节 | 读懂一个成熟 Skill 的元数据含义 |
| 实践 | 创建一个简单 Skill | WorkBuddy skill-creator Skill、OpenAI Codex Skill 教程 | 写一个"日期格式化 Skill"并测试 |
| 进阶 | 设计带脚本/资源的复杂 Skill | LangChain / LlamaIndex 的 Tool 文档、参考成熟开源 Skill | 写一个含 scripts/ + references/ 的多文件 Skill |
| 深入 | 在多 Agent 系统中编排 Skill | AutoGen / LangGraph 多 Agent 文档 | 设计"3 个 Agent + 各自 Skill"的协作流水线 |

## 8. 参考资料

- [Claude Skills Explained — Anthropic](https://claude.com/blog/skills-explained) — 官方对 Skill 的权威解释
- [A practical guide to building agents — OpenAI](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) — 涉及 Skill 与 Agent 的协作
- [Claude Skills vs Agents — findskills.co](https://findskills.co/vs/claude-skills-vs-agents) — Skill 与 Agent 的对比分析
- [WorkBuddy skill-creator Skill — 本仓库](.workbuddy/skills/skill-creator/) — 创建 Skill 的最佳实践指南
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — Agent 与 Skill 协同设计的官方模式
- [本仓库 concept-learner Skill](.workbuddy/skills/concept-learner/SKILL.md) — Skill 自身的实例

---

> 由 concept-learner Skill 生成于 2026-09-04。
