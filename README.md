# Async-MultiModal-Graph
多模态 Web 智能体
# 📸 Async-MultiModal-Graph: 工业级全异步多模态 Web 智能体

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-State_Machine-orange.svg)](https://python.langchain.com/docs/langgraph)
[![Playwright](https://img.shields.io/badge/Playwright-Async_Visual-green.svg)](https://playwright.dev/python/)

> 🚀 **核心愿景**：打破大语言模型（LLM）与物理网络世界的文本隔离。本项目基于 LangGraph 状态机重构，彻底解决复杂 Agent 在高并发下的线程死锁问题，实现具备“零延迟视觉快门”与“高维逻辑推演”的单例池化多模态智能体。



## ✨ 核心技术特性 (Key Features)

本项目并非简单的 API 堆砌，而是针对企业级多模态 Agent 落地痛点进行的系统级重构：

* **⚡️ 全异步高并发架构 (Pure AsyncIO)**：重写 LangChain/LangGraph 默认的线程池调度机制。通过底层的纯异步事件循环 (Event Loop)，彻底根除在跨线程调用无头浏览器时极其棘手的 `greenlet.error` 死锁问题。
* **⚙️ 浏览器单例资源池化 (Singleton Browser Pooling)**：摒弃“即开即焚”的高耗能模式。实现全局生命周期内的 Chromium 内核复用，大幅降低内存开销与反复握手延迟。
* **📸 零延迟热截图与复合视觉传感器**：首创“热快门”机制。当 Agent 处于目标 URL 时，跨过所有网络层直接从显存中执行全网页长截图；单一传感器可同时完成 DOM 结构化文本解析与视觉快照留存，完美绕过重度动态 JS 渲染与反爬虫机制。
* **🧠 图谱状态机流转 (StateGraph Routing)**：基于 ReAct 范式构建的动态图路由。赋予 Agent 根据工具反馈结果进行自我纠错、多步推理循环的闭环能力。

---

## 📂 架构演进路径 (Architecture Evolution)

优秀的架构是在踩坑中进化而来的。为了展示解决复杂系统冲突的思考过程，本仓库在 `architecture_evolution/` 目录下保留了历史迭代版本：

* **v1.0 巨石单体架构 (Monolithic)**：使用 `urllib` 与单文件构建的原始大模型工具调用链。（*痛点：无法解析动态网页与反爬防御*）
* **v2.0 同步多模态架构 (Sync Modular)**：引入 Playwright 赋予 Agent 视觉能力。（*痛点：LangGraph 底层线程池调度与 Playwright 同步内核产生严重冲突，频繁触发跨线程死锁，且多次开销极速恶化性能*）
* **v3.0 异步池化架构 (Current/Async)**：**当前生产环境版本**。底层重写为全异步架构，引入 `AsyncBrowserManager` 资源池，实现极速、稳定、无锁的工业级流转。

---

## 🛠️ 快速复现 (Quick Start)

### 1. 环境准备
建议使用 Conda 创建隔离环境：
```bash
conda create -n Async-MultiModal-Graph python=3.10
conda activate Async-MultiModal-Graph
