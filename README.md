# Project K-Arb - 高性能韩国加密货币套利系统

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Status](https://img.shields.io/badge/status-Planning-yellow.svg)]()

---

## 项目概述

**Project K-Arb** 是一个专注于韩国加密货币市场（Upbit ↔ Bithumb）的高性能现货套利系统。系统采用 **零第三方依赖** 的底层实现，通过 **内存级订单簿维护** 和 **异步并发架构** 实现毫秒级套利执行。

### 核心特性

- **自主实现底层**: 完全自主实现网络通信、数据解析、鉴权签名，不依赖第三方 SDK
- **接口化设计**: Gateway/Parser/Wrapper 三层架构，为 Rust 优化预留接口
- **高性能**: 订单簿更新延迟 < 5ms，下单延迟 < 50ms
- **风控完善**: 多层风控机制（余额检查、仓位限制、熔断保护）
- **渐进式优化**: Python 原型 → Rust 混合优化路径

---

## 文档导航

本项目包含完整的技术规划文档，请按顺序阅读：

### 📐 核心文档

| 文档 | 描述 | 链接 |
|------|------|------|
| **技术架构** | 系统整体架构、模块设计、技术选型 | [PROJECT_ARCHITECTURE.md](./PROJECT_ARCHITECTURE.md) |
| **开发时间线** | 6 周开发计划、每日任务分解、里程碑 | [DEVELOPMENT_TIMELINE.md](./DEVELOPMENT_TIMELINE.md) |
| **验收标准** | 各阶段验收标准、测试方法、交付物清单 | [ACCEPTANCE_CRITERIA.md](./ACCEPTANCE_CRITERIA.md) |
| **风险评估** | 14 类技术风险、预防措施、应对方案 | [RISK_ASSESSMENT.md](./RISK_ASSESSMENT.md) |

### 📚 阅读顺序建议

```
1. README.md (当前文档) - 快速了解项目
   ↓
2. PROJECT_ARCHITECTURE.md - 理解系统设计
   ↓
3. DEVELOPMENT_TIMELINE.md - 掌握开发节奏
   ↓
4. ACCEPTANCE_CRITERIA.md - 明确质量标准
   ↓
5. RISK_ASSESSMENT.md - 识别潜在风险
```

---

## 快速开始

### 前置条件

- Python 3.11+
- Git
- Upbit 和 Bithumb 账户（用于测试）

### 环境搭建

```bash
# 1. 克隆仓库（或创建新项目）
git clone <your-repo-url> k-arb
cd k-arb

# 2. 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install aiohttp msgspec

# 4. 下载参考代码（用于 API 分析）
git clone https://github.com/sharebook-kr/pyupbit reference/pyupbit
git clone https://github.com/sharebook-kr/pybithumb reference/pybithumb

# 5. 验证环境
python --version  # 应显示 Python 3.11.x
```

### 项目初始化

```bash
# 创建目录结构（参照 PROJECT_ARCHITECTURE.md）
mkdir -p core/{gateway,parser,wrapper}
mkdir -p business/{orderbook,strategy,execution,risk}
mkdir -p utils tests/{unit,integration} config scripts

# 创建初始文件
touch core/__init__.py core/interface.py core/datatypes.py
touch utils/logger.py utils/config.py
touch main.py

# 运行测试（当前应该没有任何代码）
python main.py  # 添加一个 print("Hello K-Arb") 测试
```

---

## 开发路线图

整个项目分为 5 个阶段，总计约 **6 周**（不含 Rust 优化）：

### Phase 0: 准备阶段（3 天）
- ✅ 环境搭建
- ✅ API 分析
- ✅ 项目骨架

### Phase 1: 基础设施层（2 周）
- 🔧 Gateway Layer (网络通信 + 鉴权 + 限流)
- 🔧 Parser Layer (数据解析 + 标准化)
- 🔧 Wrapper Layer (API 封装)
- 🔧 WebSocket 集成

**里程碑**: 能成功获取订单簿和账户余额

### Phase 2: 业务逻辑层（2 周）
- 🔧 OrderBook Manager (内存订单簿)
- 🔧 Strategy Module (套利策略)
- 🔧 Execution Module (订单执行)
- 🔧 Risk Module (风控)

**里程碑**: DryRun 模式 24 小时稳定运行

### Phase 3: 测试与优化（1 周）
- 🔧 单元测试 + 集成测试（覆盖率 > 80%）
- 🔧 性能优化（延迟 < 5ms）
- 🔧 7 天模拟交易验证

**里程碑**: 所有测试通过，模拟交易盈利

### Phase 4: 生产部署（3 天）
- 🔧 AWS EC2 部署
- 🔧 监控 + 告警（CloudWatch + Grafana）
- 🔧 灰度上线（限制交易量）

**里程碑**: 真实交易验证成功

### Phase 5: Rust 优化（按需）
- 🔧 Rust Parser（性能提升 5-10 倍）
- 🔧 Rust OrderBook（更新延迟 < 1ms）

**触发条件**: 当 Python 版本性能瓶颈明显时

---

## 系统架构速览

```
┌─────────────────────────────────────────────────────┐
│                  Business Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Strategy │  │ Executor │  │   Risk   │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       └─────────────┴──────────────┘               │
│                     │                               │
│              ┌──────▼──────┐                       │
│              │  OrderBook  │                       │
│              │   Manager   │                       │
│              └──────┬──────┘                       │
└─────────────────────┼──────────────────────────────┘
                      │
┌─────────────────────┼──────────────────────────────┐
│                Core Layer                          │
│              ┌──────▼──────┐                       │
│              │   Wrapper   │                       │
│              └──┬───────┬──┘                       │
│        ┌────────┴───┐   └────────┐                │
│  ┌─────▼─────┐ ┌────▼──────┐     │                │
│  │  Parser   │ │  Gateway  │     │                │
│  └───────────┘ └───────────┘     │                │
└───────────────────────────────────┼────────────────┘
                                    │
                            ┌───────▼────────┐
                            │   Exchanges    │
                            │ Upbit/Bithumb  │
                            └────────────────┘
```

**核心设计理念**:
- **分层解耦**: 每层职责单一，易于测试和替换
- **自下而上**: 从底层网络到上层策略，逐步构建
- **接口优先**: 所有模块基于抽象接口，便于 Rust 集成

---

## 技术栈

### 开发语言
- **Python 3.11+**: 快速原型开发
- **Rust** (Phase 5): 性能优化

### 核心库
| 库 | 用途 | 为什么选择 |
|----|------|-----------|
| `aiohttp` | 异步 HTTP/WebSocket | Python 最成熟的异步网络库 |
| `msgspec` | 高性能 JSON 解析 | 比标准 json 快 10-50 倍 |
| `dataclasses` | 数据结构 | 类型安全，IDE 友好 |

### 基础设施
- **部署**: AWS EC2 (Seoul)
- **监控**: CloudWatch + Grafana
- **日志**: CloudWatch Logs
- **配置**: YAML + 环境变量

---

## 关键指标

### 性能目标

| 指标 | 目标值 | 测量点 |
|------|--------|--------|
| WebSocket 延迟 | < 10ms | 接收时间 - 交易所时间 |
| OrderBook 更新 | < 5ms | 更新完成 - 接收消息 |
| 下单延迟 | < 50ms | 订单返回 - 发送请求 |
| 内存占用 | < 500MB | 持续运行 24h |
| CPU 占用 | < 30% | 单核心利用率 |

### 业务目标

| 指标 | 目标值 |
|------|--------|
| 订单成功率 | > 95% |
| 日交易次数 | 10-50 次 |
| 单笔最小利润率 | > 0.5% |
| 最大回撤 | < 5% |

---

## 风险管理

### 高风险项（🔴）

| 风险 | 影响 | 应对方案 |
|------|------|----------|
| API 变更 | 系统失效 | 版本监控 + 兼容层 |
| 订单部分成交 | 资金风险 | 紧急对冲机制 |
| 滑点过大 | 亏损 | 流动性检查 + 动态调整 |
| 密钥泄露 | 资金被盗 | Secrets Manager + 权限最小化 |

**详细信息**: 参见 [RISK_ASSESSMENT.md](./RISK_ASSESSMENT.md)

---

## 开发规范

### Git 工作流

```bash
# 1. 创建功能分支
git checkout -b feature/gateway-layer

# 2. 开发 + 提交
git add .
git commit -m "feat: implement UpbitGateway with JWT auth"

# 3. 推送 + PR
git push origin feature/gateway-layer
# 在 GitHub 创建 Pull Request

# 4. Code Review 通过后合并
git checkout main
git merge feature/gateway-layer
```

### 提交信息规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
test: 测试相关
refactor: 重构
perf: 性能优化
chore: 构建/工具相关
```

### 代码质量

```bash
# 类型检查
mypy core/ business/

# 代码风格
pylint core/ business/ --fail-under=8.0

# 单元测试
pytest tests/ --cov=core --cov=business --cov-report=html

# 安全检查
bandit -r core/ business/
```

---

## 项目结构

```
k-arb/
├── docs/                    # 项目文档
│   ├── PROJECT_ARCHITECTURE.md
│   ├── DEVELOPMENT_TIMELINE.md
│   ├── ACCEPTANCE_CRITERIA.md
│   └── RISK_ASSESSMENT.md
│
├── reference/               # 参考代码（只读）
│   ├── pyupbit/
│   ├── pybithumb/
│   └── analysis/            # 源码分析笔记
│
├── core/                    # 核心引擎
│   ├── gateway/             # 网络通信层
│   ├── parser/              # 数据解析层
│   └── wrapper/             # API 封装层
│
├── business/                # 业务逻辑
│   ├── orderbook/           # 订单簿管理
│   ├── strategy/            # 套利策略
│   ├── execution/           # 订单执行
│   └── risk/                # 风控模块
│
├── utils/                   # 工具类
├── tests/                   # 测试
├── config/                  # 配置文件
├── scripts/                 # 运维脚本
└── main.py                  # 程序入口
```

---

## 常见问题

### Q: 为什么不直接使用 pyupbit/pybithumb？
**A**:
1. 这些库可能包含不需要的依赖
2. 无法深度定制和优化
3. 难以集成 Rust（需要稳定的接口）
4. 学习底层实现有助于理解交易所 API

### Q: 为什么选择 Python 而不是直接用 Rust？
**A**:
1. **开发效率**: Python 快速验证策略可行性
2. **生态成熟**: 异步、测试、日志工具完善
3. **渐进优化**: 先功能后性能，避免过早优化
4. Python 性能瓶颈明确后，再用 Rust 优化热点

### Q: 系统安全吗？
**A**:
1. API Key 仅授予交易权限，禁止提现
2. 使用 AWS Secrets Manager 存储密钥
3. 多层风控机制（余额检查、仓位限制、熔断）
4. 完善的监控和告警
5. 详细风险评估（见 RISK_ASSESSMENT.md）

### Q: 预期收益如何？
**A**:
- 韩国市场价差通常在 0.3%-1.5%
- 扣除手续费（Upbit 0.1% + Bithumb 0.25% = 0.35%）
- 理论单笔净利润：0.15%-1.15%
- **但实际收益受市场环境、滑点、竞争等多种因素影响**
- **建议先运行模拟交易验证盈利能力**

### Q: 需要多少初始资金？
**A**:
- 建议每个交易所至少：1 BTC + 5000万 KRW
- 总计：2 BTC + 1 亿 KRW (约 $200,000)
- **可根据实际情况调整，但资金越少，套利空间越有限**

---

## 团队协作

### 角色分工

| 角色 | 职责 | 人数 |
|------|------|------|
| Tech Lead | 架构设计、代码审查、技术决策 | 1 |
| 开发者 | 编码、测试、文档 | 1-2 |
| QA | 测试、验收 | 1 (Phase 3) |
| DevOps | 部署、监控、运维 | 1 (Phase 4) |

### 沟通机制

- **每日站会**: 15 分钟同步进度
- **每周评审**: 代码审查 + 风险评审
- **里程碑验收**: 每个 Phase 结束时

---

## 许可与免责声明

### 许可
本项目为私有项目，版权所有。未经授权不得复制、分发或使用。

### 免责声明
⚠️ **重要提示**:

1. **投资风险**: 加密货币交易存在高风险，可能导致资金损失
2. **策略风险**: 套利策略不保证盈利，市场环境可能导致亏损
3. **技术风险**: 系统可能存在 bug、故障或安全漏洞
4. **合规风险**: 使用者需自行确保符合当地法律法规

**使用本系统即表示您理解并接受以上风险。开发者不承担任何责任。**

---

## 下一步行动

### 立即开始

1. ✅ 阅读所有文档（2-3 小时）
2. ✅ 搭建开发环境（1 小时）
3. ✅ 分析参考代码（1 天）
4. ✅ 开始 Phase 1 开发

### 进度跟踪

建议使用项目管理工具跟踪进度：
- **GitHub Projects**: 集成 Issues/PRs
- **Trello**: 可视化看板
- **Jira**: 专业项目管理

### 获取帮助

- **技术问题**: 查阅文档 → 搜索 GitHub Issues → 联系 Tech Lead
- **API 问题**: 查阅交易所官方文档 → 社区论坛
- **紧急问题**: 联系 On-Call 负责人

---

## 更新日志

### v1.0 - 2025-11-23 (规划阶段)
- ✅ 完成技术架构文档
- ✅ 完成开发时间线
- ✅ 完成验收标准
- ✅ 完成风险评估
- 🔜 开始 Phase 0 环境搭建

---

## 联系方式

- **项目负责人**: [你的名字]
- **Email**: [你的邮箱]
- **紧急联系**: [On-Call 电话]

---

**最后更新**: 2025-11-23
**文档版本**: v1.0
**项目状态**: 📋 规划阶段

---

<p align="center">
  <strong>让我们开始构建这个高性能套利系统！🚀</strong>
</p>
