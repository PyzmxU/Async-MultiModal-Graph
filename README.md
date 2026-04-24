# Async-MultiModal-Graph
多模态 Web 智能体
# 📸 Async-LangGraph-WebAgent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-State_Machine-orange.svg)](https://python.langchain.com/docs/langgraph)
[![AsyncIO](https://img.shields.io/badge/AsyncIO-Concurrency-green.svg)](https://docs.python.org/3/library/asyncio.html)

> **项目简介**：本项目是一个验证 LangGraph 状态机与 Playwright 无头浏览器结合可行性的实践项目（PoC）。重点解决了在复杂工具调用链路中，由于跨线程操作引发的并发死锁问题。

## 💡 核心实践总结

本项目并不侧重于复杂的业务逻辑堆砌，而是聚焦于打通坚固的底层工作流：

1. **从同步到异步的填坑记录**：
   在使用 LangGraph 的多节点流转时，传统的同步 Playwright 极易与底层线程池发生冲突，触发 `greenlet.error: cannot switch to a different thread` 死锁。本项目将所有节点与工具调用重写为 `async/await`，在一个事件循环内安全完成了所有的浏览器自动化操作。
2. **全局单例与热截图**：
   为避免大模型多次调用工具时反复开启和关闭浏览器进程，实现了浏览器的单例模式。如果模型要求对当前已加载的 URL 进行截图，系统将跳过网络请求，直接执行零延迟的显存截图。
3. **原子化工具设计**：
   遵循高内聚原则，将“文本抓取”与“网页截图”剥离为独立的原子 Tool，交由 LLM 根据用户 Prompt 动态规划调用顺序。

## 📂 架构演进说明

在 `architecture_evolution/` 目录下保留了重构前的历史版本，完整记录了从单体脚本 -> 同步死锁 -> 异步重构的排障过程，供交流参考。

## 🛠️ 运行测试
... (此处保留你的安装和运行命令) ...
