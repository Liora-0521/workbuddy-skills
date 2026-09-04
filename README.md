# workbuddy-skills

> 一个 WorkBuddy 项目级 Skill 仓库：内置 `concept-learner` Skill，输入任意概念名，自动生成结构化的 HTML 学习指南。

## 一、仓库用途

本仓库的核心目的是**让"学一个新概念"这件事变得可复用、可分享、可审计**：

- 提供一个**通用的 Skill**（`concept-learner`），不只为 Agent / 上下文 / Skill 三个概念服务，可以学习任意概念；
- 提供**三个示例概念 + 一份关系图谱**作为示范，让你看到 Skill 实际产出长什么样；
- 提供**完整的工作流**：从 SKILL.md 的 frontmatter、references 模板、HTML 输出规范、到 README 的诚实说明。

适用场景：

- 团队需要沉淀"概念入门手册"，新人入职可以照着学；
- 个人想系统化学习 AI / 工程概念，并保留一份可分享的 HTML 资料；
- 想给 WorkBuddy 增加项目级 Skill 的人，需要一个真实可参考的例子。

## 二、Skill 的存放路径

```
.workbuddy/
└── skills/
    └── concept-learner/
        ├── SKILL.md
        └── references/
            └── template.html
```

- `SKILL.md` — Skill 的入口文件，含 YAML frontmatter（`name` / `description`）+ 详细工作流（适用场景 / 输入信息 / 生成步骤 / 输出结构 / 资料来源要求 / 自检要求）。
- `references/template.html` — 生成 HTML 学习资料的 7 章节标准模板。

## 三、如何在 WorkBuddy 中调用

**前提**：在 WorkBuddy Desktop 中打开本仓库根目录（`C:\Users\zay\Desktop\workbuddy-skills`），WorkBuddy 会自动扫描 `.workbuddy/skills/` 并加载 `concept-learner`。

**调用方式 1 — 自然语言触发**：

> "用 concept-learner 学习 RAG"
> "帮我生成一份 Transformer 的学习资料"
> "用 Skill 学习注意力机制"

Agent 会根据 description 自动匹配 `concept-learner` Skill，按其工作流检索信息、生成 HTML、写入 `learning-materials/<slug>.html`。

**调用方式 2 — 斜杠命令触发**：

> `/concept-learner RAG`

（前提是 Skill 描述里同时声明支持斜杠语法；当前 SKILL.md 的 description 重点在语义触发，如需斜杠调用，可手动 `/load .workbuddy/skills/concept-learner` 后调用。）

**调用方式 3 — 直接复用 Skill 输出**：

不需要运行 Skill 时，可直接浏览 `learning-materials/` 下已生成的 HTML 文件，每份都是单文件可独立打开、自带 CSS、移动端友好的学习资料。

## 四、已生成的学习资料

| 文件 | 大小 | 说明 |
| --- | --- | --- |
| [`learning-materials/agent.html`](learning-materials/agent.html) | 13.8 KB | Agent 概念学习指南 |
| [`learning-materials/llm-context.html`](learning-materials/llm-context.html) | 13.1 KB | 大模型的上下文学习指南 |
| [`learning-materials/skill.html`](learning-materials/skill.html) | 14.4 KB | Skill 概念学习指南 |
| [`learning-materials/concept-relationship.html`](learning-materials/concept-relationship.html) | 13.4 KB | 三个概念的关系图谱（含 Mermaid 图） |

每份 HTML 都遵循统一的 7 章节结构：学习目标 / 核心问题 / 个人理解 / 应用案例 / 概念辨析 / 自测问题 / 参考来源。**关系图谱**额外包含 Mermaid 流程图，重点呈现：

- 上下文窗口如何影响 Agent 的信息密度、决策可靠性、循环长度；
- Skill 如何把"一次性 Prompt"沉淀为"团队可复用的过程资产"。

## 五、人工核查与修改记录

> 本节诚实记录 AI 协助与人工核查的分工。资料来源不得伪造，概念解释不得整段照搬 AI 对话结果——本仓库所有产出都经过核查与修改。

### AI 做了什么

- 检索 Agent / 上下文窗口 / Skill 的权威资料来源（OpenAI、Anthropic、Lilian Weng、百度百科、ArXiv 等）；
- 起草 Skill 的 SKILL.md 与 references 模板；
- 起草三份概念 HTML 与关系 HTML 的初版结构与文案。

### 人工核查了什么、修改了什么

1. **资料来源核查** —— 每条参考链接都手工核对了 URL 与标题一致性，未引用任何未经验证的"AI 编造链接"；
2. **概念辨析扩展** —— AI 初稿的边界描述偏通用，人工追加了"Agent ≠ 更聪明 LLM"、"上下文 ≠ Token 数"、"Skill 装太多会撑爆上下文"等<strong>真实踩坑场景</strong>；
3. **个人视角补充** —— 每个概念都补了"我当初的误解"段落，避免成为纯百科复述；
4. **关系图谱重构** —— 用 Mermaid 重画了 3 张关系图（总体关系 / 上下文 3 层面影响 / 真实工作流时序），比初稿的纯文本表格更直观；
5. **HTML 单文件化** —— 把所有 CSS 内嵌到每个 HTML，确保双击即可在浏览器打开，<strong>不依赖任何外部资源（CDN 仅 Mermaid 渲染关系图例外）</strong>；
6. **README 透明化** —— 本节就是人工核查的产物：明确告知哪些是 AI 写、哪些是人改。

### 仍待改进

- 概念 HTML 没有内嵌 Mermaid，目前关系图谱独占 CDN 依赖；如需完全离线，可改为预渲染 SVG；
- `concept-learner` Skill 还没有跑过真实多概念压力测试（除本次 3 个外），发现 bug 请开 issue。

## 六、目录结构

```
workbuddy-skills/
├── .gitignore                                # 排除 OS 垃圾、构建产物、敏感文件
├── README.md                                 # 你正在读的文件
├── .workbuddy/
│   └── skills/
│       └── concept-learner/                  # 项目级 Skill
│           ├── SKILL.md
│           └── references/
│               └── template.html
└── learning-materials/                       # 已生成的概念学习资料
    ├── agent.html
    ├── llm-context.html
    ├── skill.html
    └── concept-relationship.html
```

## 七、安全说明

- 本仓库**不包含任何 API Key、PAT、密码或个人隐私信息**；
- `.gitignore` 已排除常见的敏感文件（`.env`、`*.pem`、`*.key`、`secrets/` 等）；
- 若曾临时把 PAT 写在文件里，请立刻从历史中清除：`git filter-repo --invert-paths --path <泄漏文件>`。

## 八、许可

MIT License
