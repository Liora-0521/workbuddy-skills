# workbuddy-skills

> 一个 WorkBuddy 项目级 Skill 集合仓库 —— 用 AI 自动生成结构化概念学习资料。

本仓库包含：

- **`.workbuddy/skills/concept-learner/`** — 核心 Skill：输入任意概念名，自动生成结构化的 8 章节学习资料。
- **`learnings/`** — 用 `concept-learner` Skill 生成的真实学习资料样例（Agent / 大模型的上下文 / Skill）。

## 仓库结构

```
workbuddy-skills/
├── .workbuddy/
│   └── skills/
│       └── concept-learner/      # 项目级 Skill：概念学习资料生成器
│           ├── SKILL.md
│           └── references/
│               └── template.md
├── learnings/                    # 用 Skill 生成的学习资料
│   ├── agent.md
│   ├── context.md
│   └── skill.md
└── README.md
```

## 概念学习资料生成 Skill (`concept-learner`)

**用途**：输入概念名（Agent / RAG / Transformer / Skill ……），自动生成一份结构化的 Markdown 学习资料。

**输出 8 个章节**：

1. 概念定义
2. 核心原理
3. 关键组成
4. 应用场景
5. 具体例子
6. 与其他概念的关系
7. 学习路径
8. 参考资料

**使用方式**：

在 WorkBuddy 中打开本仓库后，对话中说：

> "用 concept-learner 学习 RAG"
> "/concept-learner Transformer"

即可在 `learnings/<概念名>.md` 生成结构化学习资料。

## 已生成的学习资料

| 文件 | 概念 | 说明 |
| ---- | ---- | ---- |
| [`learnings/agent.md`](learnings/agent.md) | Agent | AI 智能体——LLM + 规划 + 记忆 + 工具 |
| [`learnings/context.md`](learnings/context.md) | 大模型的上下文 | 上下文窗口、Token、注意力机制的容量边界 |
| [`learnings/skill.md`](learnings/skill.md) | Skill | 装在 Agent 里的"岗位手册"，让通用 Agent 变专家 |

## 适用对象

- 想系统化学习 AI / 工程概念的开发者
- 想给团队沉淀领域知识（Skills）的 Tech Lead
- 想在项目里使用 WorkBuddy 项目级 Skill 的人

## 许可

MIT License
