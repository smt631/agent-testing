# 阶段四：Agent 测试（LLM/Agent 了解）

> AI 功能专项测试实习生 · 面试作品集
> 用 DeepEval GEval 对**真实运行的客服 Agent** 做工具调用 / 死循环 / 权限边界 / 多步一致性评估。

[![CI](https://github.com/smt631/agent-testing/actions/workflows/agent-evals.yml/badge.svg)](https://github.com/smt631/agent-testing/actions)

## 一句话介绍

> 我没有只写"判断文本"的测试，而是**真搭了一个带工具调用、多步规划、权限白名单的 Agent**，再用 LLM-as-Judge（DeepEval GEval）对它的执行轨迹做四项评估——既证明 Agent 行为良好，也证明评估指标能抓到典型故障。

## 为什么 Agent 测试比普通 LLM 测试更难

普通 LLM 是「输入→回答」单轮；Agent 多了**工具调用、多步自主规划、环境交互**三件事，测试复杂度是乘法不是加法：

| 维度 | 普通 LLM | Agent | 新增测试关注点 |
|------|---------|-------|--------------|
| 交互 | 单轮 Q&A | 多轮自主决策 | 每步都可能出错 |
| 外部操作 | 无 | 调用工具/API | 工具调用正确性 |
| 上下文 | 单次对话 | 记忆 + 多步 | 上下文一致性 |
| 副作用 | 无 | 可能改外部状态 | 权限与安全性 |

## Agent 的 4 大测试风险点（核心）

| # | 风险 | 含义 | 本项目怎么测 |
|---|------|------|-------------|
| 1 | **工具调用幻觉** | 调了不存在的工具 / 传错参数 | `Tool Call Correctness` 指标，对照[工具规格]判断 |
| 2 | **死循环** | 反复调同一工具无法收敛 | `Loop Detection` 指标 + Agent 内置 max_steps 与重复检测 |
| 3 | **权限越界** | 调了不该调的高风险工具 | `Safety Boundary` 指标 + Agent 权限白名单 |
| 4 | **多步不一致** | 中间事实与最终结论矛盾 | `Multi-step Consistency` 指标 |

## 技术栈

- **被测对象**：自研极简客服 Agent（DeepSeek `deepseek-chat` 函数调用），含工具定义、多步循环、最大步数、权限白名单、死循环检测、完整轨迹记录
- **评估框架**：DeepEval `GEval`（LLM-as-Judge，评判模型同为 `deepseek-chat`）
- **测试运行**：pytest（质量门禁）
- **CI**：GitHub Actions 自动跑评估 + 上传 HTML 报告

## 目录结构

```
phase-04-agent-testing/
├── agent.py              # 真实客服 Agent（工具调用 + 多步规划 + 权限白名单 + 轨迹记录）
├── scenarios.py          # 测试场景：4 个真实场景 + 3 个对抗轨迹
├── test_agent.py         # pytest 质量门禁（好场景必须过、对抗必须被抓）
├── run_agent_eval.py     # 生成自包含 HTML 报告（双击即看）
├── agent_evaluation_report.html  # 评估报告（从 GitHub 下载即可查看）
├── conftest.py           # DeepSeek 密钥注入（不硬编码）
├── requirements.txt
└── .github/workflows/agent-evals.yml
```

## 快速开始

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # 填入 DeepSeek Key（OPENAI_API_KEY）
pytest test_agent.py -v   # 跑质量门禁
python run_agent_eval.py  # 生成 HTML 报告
```

## 评估报告

从仓库下载 `agent_evaluation_report.html` **双击即可在浏览器打开**，无需登录：

- 顶部 KPI：评估场景数 / 指标评估次数 / 判定正确数 / **检测准确率**
- 每个场景一张卡片：输入 → 4 项指标分数/通过/期望/检测 → 可展开看完整执行轨迹
- 好场景（查询订单 / 天气 / 价格 / 危险取消请求）指标全绿；对抗场景（死循环 / 工具幻觉 / 价格矛盾）被对应指标精准抓红

## 关键设计点

1. **真实 Agent 而非脚本拼文本**：轨迹由 DeepSeek 函数调用真实产生，不是我手写的好看字符串。
2. **[工具规格] 作为评判依据**：把工具清单 + 权限白名单写进轨迹，让 LLM 评委有确定判据，避免"猜幻觉"。
3. **权限最小化**：`cancel_order` 虽在工具列表，但不在白名单，Agent 触碰即被 `[DENIED]`——对应 OWASP LLM06 Excessive Agency。
4. **死循环三层防护**：max_steps 上限 + 连续相同调用检测 + 超时（本项目在 Agent 内实现前两层）。
5. **评估粒度下沉到"轨迹"**：不只看最终答案，还看每一步的决策（这正是 Agent 测试区别于 LLM 测试的核心）。

## CI 质量门禁

`.github/workflows/agent-evals.yml`：`setup-python` → 安装依赖 → pytest 质量门禁 → 生成并上传 `agent_evaluation_report.html` 为 Artifact。密钥经 `secrets.OPENAI_API_KEY` 注入，**不进代码**。
