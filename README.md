# workbuddy-skills

> 一个 WorkBuddy 项目级 Skill 仓库：内置两个 Skill —— `concept-learner`（输入任意概念名，输出一份**结构化的、可核查的** HTML 学习指南）与 `push-to-github`（把本地改动提交并推送到 GitHub 仓库，并在推送后**校验远程与本地是否真的一致**）。

---

## 一、仓库用途

这个仓库解决的问题有两个。

**其一：每学一个新概念，都要从零整理一遍资料。** 把"学一个概念"沉淀成一套可复用的流程：

- **一个通用 Skill**（`concept-learner`）——不是为某几个概念写的一次性提示词，而是接受**任意概念**（中英文不限）作为输入；
- **四份示范产出**——三份概念学习资料 + 一份概念关系图谱，展示 Skill 实际产出长什么样；
- **一套自检规范**——从资料源核查、章节结构到自测题设计，都有明确的硬性要求。

**其二：东西改完了，但不确定远程到底长什么样。** 这一层由 `push-to-github` 承接：

- **一个推送 Skill**（`push-to-github`）——把本地项目或新建的项目级 Skill **显式**提交、推送（不用 `git add -A`），并在推送后做**三源交叉校验**：远程 tip / 本地 `HEAD` / GitHub API 文件树**逐 blob 比对哈希**；
- **一份踩坑速查表**（`references/troubleshooting.md`）——本机实测过的证书吊销报错、curl 无法写文件、"本地缓存过期导致看起来像推送丢了"等问题的解法；
- **一个可执行校验脚本**（`scripts/verify_push.py`）——纯标准库，一条命令给出"远程与本地是否完全一致"的结论。

适用场景：

- 想系统学习某个技术概念，并留下一份可分享、可回顾的资料；
- 团队沉淀"概念入门手册"，新人可以照着自学；
- 想把本地产出交付到 GitHub 仓库，并且需要一个"推完能自查"的流程；
- 想给 WorkBuddy 写项目级 Skill，需要一个完整可参考的例子——本仓两个 Skill 都是。

---

## 二、Skill 的存放路径

项目级 Skill 放在仓库根目录的 `.workbuddy/skills/` 下：

```
workbuddy-skills/
├── .workbuddy/
│   └── skills/
│       ├── concept-learner/           ← Skill 1：概念学习资料生成
│       │   ├── SKILL.md               ← 入口：YAML 元数据 + 完整工作流
│       │   └── references/
│       │       └── template.html      ← 8 章节 HTML 模板
│       └── push-to-github/            ← Skill 2：推送至 GitHub 仓库
│           ├── SKILL.md               ← 入口：六段契约 + Step 0–9
│           ├── references/
│           │   └── troubleshooting.md ← 本机实测踩坑与一页诊断命令
│           └── scripts/
│               └── verify_push.py     ← 推送后三源交叉校验（纯标准库）
├── learning-materials/
│   ├── agent.html
│   ├── llm-context.html
│   ├── skill.html
│   ├── concept-relationship.html
│   └── vendor/
│       └── mermaid.min.js            ← 关系图渲染的本地依赖（确保离线可用）
├── README.md
└── .gitignore
```

**`SKILL.md` 的结构**（六段契约，本仓所有 Skill 都遵守，缺一不可）：

| 段落 | 内容 |
| --- | --- |
| 一、适用场景 | 什么时候触发、什么时候不触发、边界在哪 |
| 二、输入信息 | 必填字段、可选字段，以及字段有歧义时该问谁 |
| 三、执行步骤 | 编号 Step，每步不可跳过 |
| 四、输出结构 | 交付物必须包含哪几项 |
| 五、硬性要求 | 本领域不可妥协的规范（资料来源 / 凭据安全 ……） |
| 六、自检清单 | 强制勾选项，未通过不得交付 |

两个 Skill 的输入字段：

| Skill | 必填 | 可选 |
| --- | --- | --- |
| `concept-learner` | `concept` | `audience` / `focus` / `output_dir` / `slug` |
| `push-to-github` | `repo_url` | `paths` / `branch` / `message` / `mode`（`push` ｜ `verify` ｜ `dry-run`） |

---

## 三、如何在 WorkBuddy 中调用它们

在 WorkBuddy 中打开本仓库目录（`C:\Users\zay\Desktop\workbuddy-skills`）后，它会自动发现 `.workbuddy/skills/` 下的项目级 Skill。然后任意一种说法都能触发。

### Skill 1 · concept-learner

**方式 1 · 显式点名**

> 用 concept-learner 学习 RAG

**方式 2 · 斜杠命令**

> /concept-learner Transformer

**方式 3 · 描述需求（靠 description 自动匹配）**

> 帮我系统学一下向量数据库，输出一份 HTML 学习资料

**可选参数**（写在同一句话里即可）：

> 用 concept-learner 学习 RAG，面向 beginner，侧重工程实现

触发后，Skill 会依次执行：划定范围 → 检索并**核查**资料源 → 写学习目标与核心问题 → 写个人化解释 → 拆解机制 → 找真实案例 → 辨析边界 → 设计 3–5 道递进自测题 → 输出 HTML → 自检。

**输出位置**：`learning-materials/<slug>.html`，单文件、内嵌 CSS，双击即可在浏览器打开。

### Skill 2 · push-to-github

同一套触发方式：

> 用 push-to-github 把这次的改动推到 workbuddy-skills
>
> /push-to-github
>
> 帮我提交并推送，然后确认远程和本地内容一致

它和"随手敲几条 git 命令"的区别在**三处硬约束**：

1. **不信口述的仓库信息**——默认分支、真实 `owner` 都先用 API 读一遍再动手（用户名笔误是真实发生过的事）；
2. **显式指定提交路径，不用 `git add -A`**——工作副本里常年躺着 `01.py`、随手建的空文件，一把梭会全部推上公开仓库。Skill 会先 `git status --porcelain` 逐条分类，把"不提交的东西"明确列出来；
3. **推送后必须三源校验**——只比"提交 SHA 相同"不足以说明问题，要逐 blob 比对文件哈希。

**输出**：提交清单 → 提交 SHA → 三源校验结论 → **本次未提交的文件及原因**。

推送后单独自查（纯标准库，无需安装依赖）：

```bash
cd C:/Users/zay/Desktop/workbuddy-skills
python .workbuddy/skills/push-to-github/scripts/verify_push.py
```

退出码 `0` = 远程与本地完全一致；`1` = 有差异（会列出仅本地、仅远程、内容不一致三类文件）；`2` = 网络或环境原因没校验完。

---

## 四、已生成的学习资料

> 本节内容全部由 `concept-learner` 产出。

| 文件 | 概念 | 核心内容 |
| --- | --- | --- |
| [`learning-materials/agent.html`](learning-materials/agent.html) | **Agent** | 用"控制流由谁决定"区分 Agent 与 Workflow；拆解模型/工具/循环三要素；ReAct 循环；错误累积与上下文预算这两个真实瓶颈 |
| [`learning-materials/llm-context.html`](learning-materials/llm-context.html) | **大模型的上下文** | 区分"窗口"与"长度"；自注意力 O(n²) 为何让上下文成为稀缺资源；Lost in the Middle 的 U 型曲线（含自绘 SVG 图）；Context Rot；四种上下文工程手段 |
| [`learning-materials/skill.html`](learning-materials/skill.html) | **Skill** | SKILL.md 的字段约束；渐进式披露三级加载；脚本为何只送输出进上下文；Skill 与 Prompt / Agent / MCP / Command 的分工边界 |
| [`learning-materials/concept-relationship.html`](learning-materials/concept-relationship.html) | **三者关系** | 3 张 Mermaid 图：整体依赖关系、上下文影响 Agent 的三条路径、Skill 的加载时序；上下文如何限制 Agent、Skill 如何沉淀知识 |

**每份资料的结构**（8 章节）：

1. 学习目标（用"能做"而非"能知道"）
2. 核心问题
3. 个人解释（含类比、反例、"我当初的误解"）
4. 核心机制 / 组成
5. 应用案例（真实可验证）
6. 概念辨析（≥3 条边界与误用）
7. **自测题（3–5 道，难度递进 ★ → ★★★★★，答案折叠）**
8. 参考来源（**全部为官方来源**，逐条 HTTP 验证 + 访问日期）

### 参考来源总览（去重后 18 条，全部为官方来源）

**厂商官方博客 / 官方文档（10 条）**

| 来源 | 类型 | 用于 |
| --- | --- | --- |
| [Building effective agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents) | 官方工程博客 | Agent、关系图谱 |
| [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 官方工程博客 | 上下文、Agent、关系图谱 |
| [Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | 官方工程博客 | Skill、关系图谱 |
| [Prompt caching with Claude — Anthropic](https://claude.com/blog/prompt-caching) | 官方博客 | 上下文 |
| [A practical guide to building agents — OpenAI（PDF）](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) | 官方指南 | Agent |
| [OpenAI Agents SDK — 官方文档](https://openai.github.io/openai-agents-python/) | 官方文档 | Agent |
| [Agent Development Kit (ADK) — Google 官方文档](https://adk.dev/) | 官方文档 | Agent |
| [Microsoft Agent Framework — 官方文档](https://learn.microsoft.com/en-us/agent-framework/overview/) | 官方文档 | Agent |
| [Claude Code — Skills 官方文档](https://code.claude.com/docs/en/skills) | 官方文档 | Skill |
| [上下文硬盘缓存 — DeepSeek 官方 API 文档](https://api-docs.deepseek.com/guides/kv_cache) | 官方文档 | 上下文 |

**官方开源仓库（1 条）**

| 来源 | 类型 | 用于 |
| --- | --- | --- |
| [anthropics/skills](https://github.com/anthropics/skills) | 官方开源仓库 | Skill |

**开放标准 / 规范（3 条）**

| 来源 | 类型 | 用于 |
| --- | --- | --- |
| [Model Context Protocol — 官方规范（2026-07-28）](https://modelcontextprotocol.io/specification/2026-07-28) | 官方规范 | Agent、关系图谱 |
| [Agent Skills 格式规范](https://agentskills.io/specification) | 开放标准 | Skill |
| [Agent Skills 开放标准站点](https://agentskills.io/home) | 开放标准 | Skill、关系图谱 |

**论文原文（4 条）**

| 来源 | 类型 | 用于 |
| --- | --- | --- |
| [ReAct: Synergizing Reasoning and Acting in Language Models（arXiv:2210.03629）](https://arxiv.org/abs/2210.03629) | 论文原文 | Agent、关系图谱 |
| [Lost in the Middle: How Language Models Use Long Contexts（arXiv:2307.03172）](https://arxiv.org/abs/2307.03172) | 论文原文 | 上下文、关系图谱 |
| [Attention Is All You Need（arXiv:1706.03762）](https://arxiv.org/abs/1706.03762) | 论文原文 | 上下文 |
| [RoFormer: Enhanced Transformer with Rotary Position Embedding（arXiv:2104.09864）](https://arxiv.org/abs/2104.09864) | 论文原文 | 上下文 |

**来源准入门槛**——只接受四类：

1. **厂商官方文档 / 官方博客**：域名与发布主体必须是该概念的所有者或维护者；
2. **官方开源仓库**：组织账号下的一手代码与示例；
3. **开放标准 / 规范**：标准制定方发布的正式文本；
4. **论文原文**：作者发布或正式出版物页面。

个人博客、公众号、知乎 / CSDN / 掘金等二手转述，教程站、聚合站、AI 内容农场，一律不进入引用列表。**条数不设上限**：官方来源足够时不必压缩，涉及多个厂商时优先覆盖多家，让同一结论有两条以上官方原文互相印证。

---

## 五、AI 与人工核查的分工记录

这一节如实记录哪些是 AI 生成的、哪些经过了人工阅读和修改。**AI 是起草工具，不是事实来源**——所有引用和结论都经过人工核对。

### AI 做了什么

- 按方案生成 SKILL.md 的初稿结构与文案；
- 起草四份 HTML 资料的正文，并按模板生成排版；
- 执行资料检索与链接可访问性验证（脚本批量检查 HTTP 状态码）；
- 生成 Git 提交信息。

### 人工做了什么（核查与修改）

| 核查项 | 具体做法 |
| --- | --- |
| **来源全部收敛为官方** | 按"只引用官方来源"重新审了一遍全部引用：删除唯一一条非官方来源——Lilian Weng 的 LLM Agent 综述（虽属高引工程综述，但发布主体是个人博客而非机构），替换为 OpenAI 官方 PDF 指南，并补充 OpenAI Agents SDK、Google ADK、Microsoft Agent Framework 三家官方文档，使来源覆盖 4 家厂商 / 机构，便于交叉印证 |
| **链接真实性 + 最终跳转地址检查** | 逐条做 HTTP 验证，并**额外检查最终跳转地址**。过程中查出几条"看着是官方、实际打不开"的链接：`docs.claude.com` / `platform.claude.com` 在本网络环境会被重定向到「区域不可用」占位页，`platform.openai.com` 与 `openai.com` 返回 403，`ai.google.dev` 不可达。这些一律**不纳入引用**，改用可访问的等价官方入口（`claude.com/blog`、`cdn.openai.com`、`adk.dev` 等）。最终收录 18 条，全部为官方来源且实测可打开 |
| **表述与原文一致** | 对照原文逐条核对关键结论的措辞。例如 Anthropic 对 Agent 的定义是"LLM 在循环中自主使用工具"，Workflow 与 Agent 的区分标准是"控制流是否由预定义代码路径决定"——这些表述都回到原文确认过 |
| **技术结论复核** | 例如"自注意力复杂度为 O(n²)"这一条，确认原始论文中的表述是 O(n²·d)，并在正文加脚注说明现代实现（FlashAttention、稀疏注意力、KV 压缩）已大幅降低常数与显存开销——避免读者理解成"长度一翻倍就必然慢四倍" |
| **时效性限定** | Lost in the Middle 的实验数据来自 2023 年的模型，正文明确标注"后续模型代际有所缓解但未消除，幅度依赖具体模型，应当自行实测"，不把这组数字当成永恒常量 |
| **个人视角补充** | 每份资料的"个人解释"都包含类比、反例和"我当初的误解"三部分，这些内容是基于对原文的理解重新组织后写的，不是对检索结果的整段摘录 |
| **概念辨析扩展** | 在初稿基础上补充了实际踩过的坑，如"能放进去 ≠ 能用上"、"Skill 写得越全越好其实破坏了渐进式披露"、"Skill 与 MCP 不是二选一" |
| **关系图谱重做** | 初稿用纯文字表格描述三者关系，改为 3 张 Mermaid 图，分别对应整体依赖、上下文的三种影响路径、Skill 的加载时序 |
| **离线可用性** | 发现 Mermaid 通过 CDN 加载时在断网/受限环境下会渲染失败（页面显示空白），改为下载 `vendor/mermaid.min.js` 到仓库内用相对路径引用，确保双击 HTML 就能看图 |
| **自测题设计** | 按"记忆 → 理解 → 应用 → 辨析 → 综合"五个层次设计 5 道题并标注难度星标，每题答案都要求解释"为什么"而不只给结论 |

### 一处需要说明的取舍

本仓库的写作是"AI 起草 + 人工核查修改"完成的。核查的重点放在**事实层**（链接是否可访问、表述是否与原文一致、结论是否有来源支撑）；"个人解释"部分虽然由 AI 起草，但结构（类比 / 反例 / 误解）和观点是人工确认后才保留的。

### `push-to-github` 的分工

| 项 | 说明 |
| --- | --- |
| AI 做了什么 | 起草 SKILL.md / 踩坑速查表 / 校验脚本；执行工作区清点、敏感信息扫描、选择性暂存与提交 |
| 人工做了什么 | 划定 Skill 范围（只管"提交—推送—校验"，建仓与仓库可见性由人决定）；确认"不提交散落临时文件"与"凭据只进 local config"两条硬约束 |
| 为什么把校验单独做成脚本 | "推送成功"是**工具自报的结果**，不足为凭。本机实测过 `git update-ref` 返回 0 却没落盘、`Start-Process -Wait` 返回 1 但安装其实成功——退出码会骗人，所以结论必须来自独立数据源 |

---

## 六、版本与安全

- **不提交任何敏感信息**：无 API Key、无密码、无个人隐私文件。`.gitignore` 中已排除 `.env*`、`*.pem`、`*.key`、`secrets/` 等常见敏感文件类型；
- **文中提到的凭据**：仓库内容中不含任何访问令牌（token）；
- **提交前扫描**：`push-to-github` 每次提交前跑一遍模式扫描（`ghp_*` / `github_pat_*` / `sk-*` / 私钥头），命中即停止提交；
- **本地 `.git/config` 里的凭据**：若 remote URL 中拼接了 PAT，它会**明文**保存在 `.git/config`。该文件不被 Git 追踪，但会随目录拷贝 / 备份一起扩散——不要把它打包进任何交付物，用完及时 revoke；
- **环境依赖**：唯一的外部依赖是 `learning-materials/vendor/mermaid.min.js`，已随仓库提交，确保离线可渲染。`push-to-github` 的校验脚本只依赖 Python 标准库。

---

## 七、许可与反馈

内容用于学习与分享。如发现链接失效、表述有误，或对某个结论有不同看法，欢迎提 issue 指出——尤其是**技术表述的准确性问题**，这类反馈最有价值。
