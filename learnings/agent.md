# Agent

> **能感知环境、自主决策并执行动作的 AI 系统，是把 LLM 从"会回答的聊天机器人"升级为"能完成任务的执行体"的关键架构。**

**通俗解释**：把 LLM 想象成一个博学但足不出户的专家——他知道很多事，但你问他才答。Agent 则是给这位专家配了一双手（Tools）、一张待办清单（Planning）、一本记事本（Memory），让他能主动规划任务、调用工具、记住历史，最终独立完成复杂工作。

---

## 1. 概念定义

- **正式定义**：AI Agent（智能体）是一种能够**感知环境、自主决策并执行任务**的智能实体。它以大语言模型（LLM）作为"推理内核"，结合规划、记忆、工具调用等能力，在数字或物理环境中完成多步骤、目标导向的工作。
- **通俗定义**：Agent = LLM（大脑）+ Planning（任务规划）+ Memory（记忆）+ Tools（工具），是一个"能自己动手做事"的 AI 系统。
- **关键术语**：Agent、LLM-based Agent、自主智能体、ReAct Loop、Tool Use、MCP。

> OpenAI 给出的工程化定义："Agents are systems that independently accomplish tasks on your behalf."（能独立代表用户完成任务的系统）。

## 2. 核心原理

### 原理 1：思考 → 行动 → 观察循环（ReAct Loop）
Agent 不再是"输入 → 输出"的单次响应，而是反复迭代：`观察环境 → 推理下一步该做什么 → 调用工具行动 → 观察新结果 → 再推理`。这个循环让 Agent 能在不确定的真实环境中自适应。  
*为什么这样*：单次 LLM 输出受限于上下文长度，无法处理需要数十步的长链路任务；ReAct 把任务拆成"小决策 + 小动作"，每一步都可被验证和修正。

### 原理 2：LLM 作为推理内核，工具作为执行四肢
LLM 本身只能输出文本，Agent 通过 **Function Calling / Tool Use** 把文本决策翻译成对外部系统的真实调用（搜索、读写文件、调用 API、操作浏览器）。LLM 是"决策者"，工具是"执行者"。  
*为什么这样*：LLM 的训练数据是静态的、无法触达实时信息；工具让 Agent 的能力边界由"训练截止日期"扩展到"当下"。

### 原理 3：记忆分层解决上下文瓶颈
Agent 把记忆分为 **短期记忆（当前任务上下文）** 和 **长期记忆（外部知识库、向量数据库）**。短期记忆靠 Prompt 内的对话历史，长期记忆靠相似度检索把"过去的事"重新注入 Prompt。  
*为什么这样*：Transformer 的注意力成本是 O(n²)，不可能把所有历史都塞进上下文；分层记忆是"用空间换智能"的工程妥协。

### 原理 4：规划与反思让任务可被分解
Agent 在执行前会**规划**（Task Decomposition / Chain-of-Thought / Tree-of-Thought），在执行中会**反思**（Reflection / Self-Critics），出错时能回到上一步或重新选择工具。  
*为什么这样*：现实任务的步骤间存在依赖和分支，朴素执行极易在第三步就偏离目标；规划 + 反思是把"会聊天"变成"会做事"的核心。

## 3. 关键组成

- **Model（推理内核）**：负责理解指令、做决策、选择工具的 LLM（如 GPT-4、Claude、Llama）。
- **Tools（工具集）**：Agent 与外部世界交互的接口，包括搜索、文件读写、代码执行、API 调用、浏览器操作等；每个工具有标准化定义（name、description、parameters）。
- **Memory（记忆系统）**：短期记忆（任务上下文）+ 长期记忆（向量库、外部知识库），决定 Agent 是否"记得住"。
- **Planning（规划模块）**：任务分解、CoT、ToT、ReAct 等推理策略，决定 Agent 是否"想得清楚"。
- **Controller / Loop（控制器）**：管理"观察 → 规划 → 行动 → 反馈 → 状态更新"循环的调度器，决定何时停止、何时回退。

> 工业实践中（如 OpenAI Agents SDK），Agent 通常被简化为三件套：**Model + Instructions + Tools**，规划与记忆由 SDK 隐式提供。

## 4. 应用场景

- **场景 1：AI 编程助手**（Cursor / Claude Code / Devin）—— Agent 在代码仓库里读文件、跑命令、写代码、修 bug，最终完成一个 PR。
- **场景 2：企业流程自动化** —— 客服 Agent 自动读工单、查知识库、判断是否升级、转交人工；财务 Agent 自动对账、识别异常、生成报告。
- **场景 3：深度研究助手** —— 用户给一个研究问题，Agent 自动检索文献、读 PDF、做对比、整理成结构化报告（典型如 OpenAI Deep Research、Perplexity Pro）。
- **场景 4：浏览器 / 桌面操作代理** —— Agent 通过浏览器自动化或 Computer Use 操作网页和桌面应用，替代重复性 GUI 操作。
- **场景 5：多 Agent 协作** —— 由一个 Orchestrator Agent 调度多个子 Agent（如研究 Agent + 写作 Agent + 校对 Agent）协同完成复杂项目。

## 5. 具体例子

### 例子 1：天气查询 Agent（OpenAI Agents SDK 官方示例）

```python
from agents import Agent

def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

weather_agent = Agent(
    name="Weather agent",
    instructions="You are a helpful agent who can talk to users about the weather",
    tools=[get_weather],
)

# 用户问："北京今天天气怎么样？"
# Agent 内部循环：
#   1. 推理：用户问天气 → 需要调 get_weather 工具
#   2. 行动：调 get_weather("北京")
#   3. 观察：返回 "The weather in 北京 is sunny."
#   4. 推理：够了，可以回答用户
#   5. 输出："北京今天是晴天。"
```

### 例子 2：代码修复 Agent

```
用户：项目里有个登录页面的 bug，帮我修一下。
Agent 循环：
  1. 用 ListFiles 工具列出项目结构
  2. 用 Read 工具读取 login.py
  3. 用 Grep 工具查找相关函数
  4. 推理：发现 password 字段没有 trim()，是 bug 根因
  5. 用 Edit 工具修改代码
  6. 用 Bash 工具跑测试，验证修复
  7. 输出修复总结
```

## 6. 与其他概念的关系

- **相似概念 vs LLM**：LLM 是"输入 → 输出"的单次响应；Agent 是"循环 → 行动 → 闭环"的持续执行体。LLM 是大脑，Agent 是大脑+手+脚。
- **相似概念 vs Workflow**：Workflow 是预设的确定性流程（if-else + 顺序执行）；Agent 是基于 LLM 推理的动态流程，能处理未定义分支。
- **相似概念 vs Copilot**：Copilot 是"用户主导、AI 辅助"；Agent 是"AI 主导、用户审批"。
- **前置概念**：要理解 Agent，先要懂 LLM、Prompt Engineering、Function Calling / Tool Use、ReAct 框架。
- **后续概念**：掌握 Agent 之后，可以继续学习 Multi-Agent 系统、MCP（Model Context Protocol）、Agentic Workflow 编排（如 LangGraph、AutoGen）。
- **对比概念**：与 MCP Server 的边界——MCP 提供"工具和数据接入能力"，Agent 决定"何时调用、怎么组合这些工具"。

## 7. 学习路径

| 阶段 | 目标 | 推荐资料 | 验证方式 |
| ---- | ---- | -------- | -------- |
| 入门 | 知道 Agent 是什么 | OpenAI《A practical guide to building agents》、Lil'Log "LLM Powered Autonomous Agents" | 能用一段话解释 Agent 与 LLM 的区别 |
| 基础 | 理解 ReAct / Tool Use | ReAct 论文（Yao et al., 2022）、OpenAI Function Calling 文档 | 手写一个 ReAct 风格的 50 行 Agent |
| 实践 | 用框架搭一个 Agent | OpenAI Agents SDK / LangGraph / AutoGen 文档 | 搭一个能查天气 + 发邮件的 Agent |
| 进阶 | 理解多 Agent 协作 | Anthropic Multi-Agent Research、AutoGen 论文 | 设计一个 2-3 Agent 的研究流水线 |
| 深入 | 设计与改进 Agent 架构 | "The Rise and Potential of LLM Based Agents: A Survey"、Agentic Design Patterns 系列 | 提出自己对 Agent 架构的改进观点 |

## 8. 参考资料

- [A practical guide to building agents — OpenAI](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) — OpenAI 官方工程实践指南
- [LLM Powered Autonomous Agents — Lil'Log (Lilian Weng)](https://lilianweng.github.io/posts/2023-06-23-agent/) — Agent 架构经典综述
- [The Rise and Potential of Large Language Model Based Agents: A Survey — 知乎](https://zhuanlan.zhihu.com/p/650307840) — 中文综述
- [ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)](https://arxiv.org/abs/2210.03629) — ReAct 框架原始论文
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic 对 Agent 工作流模式的总结

---

> 由 concept-learner Skill 生成于 2026-09-04。
