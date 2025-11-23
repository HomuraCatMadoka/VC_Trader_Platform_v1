# Project K-Arb 开发时间线

## 文档说明
本文档定义了 Project K-Arb 的完整开发路线图，包括各阶段的时间分配、关键里程碑、资源需求和风险缓冲。

---

## 整体时间规划

| 阶段 | 周期 | 工作日 | 主要目标 | 团队规模 |
|------|------|---------|----------|----------|
| **Phase 0: 准备阶段** | 3 天 | 3 | 环境搭建 + 源码分析 | 1 人 |
| **Phase 1: 基础设施** | 2 周 | 10 | 核心引擎实现 | 1-2 人 |
| **Phase 2: 业务逻辑** | 2 周 | 10 | 策略与执行 | 1-2 人 |
| **Phase 3: 测试与优化** | 1 周 | 5 | 模拟交易 + 性能调优 | 2 人 |
| **Phase 4: 生产部署** | 3 天 | 3 | 部署 + 监控 | 1 人 |
| **Phase 5: Rust 优化** | 按需启动 | - | 性能瓶颈重构 | 1-2 人 |

**总计**: 约 6 周（不含 Phase 5）

---

## Phase 0: 准备阶段 (3 天)

### 时间分配
| 任务 | 时间 | 负责人 |
|------|------|--------|
| 环境搭建 | 0.5 天 | 开发者 |
| 下载并分析参考代码 | 1 天 | 开发者 |
| 创建项目骨架 | 0.5 天 | 开发者 |
| API 测试验证 | 1 天 | 开发者 |

### Day 1: 环境搭建与代码获取

#### 上午 (4h)
- [ ] 安装 Python 3.11+（使用 pyenv）
- [ ] 创建虚拟环境：`python -m venv .venv`
- [ ] 安装基础依赖：
  ```bash
  pip install aiohttp msgspec
  ```
- [ ] 配置 Git 仓库和 .gitignore
- [ ] 下载参考代码到 `references/` 目录：
  ```bash
  git clone https://github.com/sharebook-kr/pyupbit references/pyupbit
  git clone https://github.com/sharebook-kr/pybithumb references/pybithumb
  ```

#### 下午 (4h)
- [ ] 注册 Upbit 和 Bithumb 测试账号
- [ ] 生成 API Key（仅开通查询权限，暂不开通交易）
- [ ] 使用 `curl` 测试公开 API：
  ```bash
  # Upbit 获取 BTC 当前价格
  curl https://api.upbit.com/v1/ticker?markets=KRW-BTC

  # Bithumb 获取 BTC 当前价格
  curl https://api.bithumb.com/public/ticker/BTC_KRW
  ```
- [ ] 记录 API 响应格式到 `references/analysis/`

**交付物**:
- ✅ 可运行的 Python 环境
- ✅ 参考代码库
- ✅ API 访问验证报告

---

### Day 2: 源码分析

#### 全天 (8h)
**任务**: 深度阅读 `pyupbit` 和 `pybithumb` 源码

**分析清单**:

| 模块 | 需要提取的信息 | 输出文档 |
|------|---------------|----------|
| **鉴权部分** | JWT 生成逻辑、HMAC 签名细节 | `references/analysis/auth_analysis.md` |
| **API 端点** | 所有 REST 端点、参数、返回字段 | `references/analysis/api_endpoints.md` |
| **WebSocket** | 连接方式、订阅格式、消息结构 | `references/analysis/websocket_protocol.md` |
| **错误处理** | 常见错误码、重试策略 | `references/analysis/error_handling.md` |
| **限流逻辑** | 是否有内置限流、如何实现 | `references/analysis/ratelimit.md` |

**重点关注**:
- Upbit JWT 生成时的 `query_hash` 计算方法
- Bithumb 签名时的字符串拼接顺序
- WebSocket 心跳机制
- Orderbook 数据格式差异

**交付物**:
- ✅ 5 份源码分析文档
- ✅ API 字段映射表

---

### Day 3: 项目骨架搭建

#### 上午 (4h)
- [ ] 创建 `core/` 目录结构（按照架构文档）
- [ ] 编写 `core/interface.py`（定义所有抽象基类）
- [ ] 编写 `core/datatypes.py`（定义数据结构）
- [ ] 编写 `core/exceptions.py`（定义自定义异常）

#### 下午 (4h)
- [ ] 创建 `utils/config.py`（配置文件加载）
- [ ] 创建 `utils/logger.py`（结构化日志）
- [ ] 编写 `config/development.yaml` 模板
- [ ] 编写 `main.py` 入口（仅打印 "Hello World"）
- [ ] 运行 `python main.py` 验证项目可启动

**交付物**:
- ✅ 完整的目录结构
- ✅ 核心接口定义
- ✅ 可运行的 main.py

---

## Phase 1: 基础设施层 (2 周)

### Week 1: Gateway Layer

#### Day 1-2: UpbitGateway 实现

**任务清单**:
- [ ] 实现 `core/gateway/base.py`（BaseGateway 抽象类）
- [ ] 实现 `core/gateway/auth/jwt_native.py`（原生 JWT 生成）
  ```python
  def generate_jwt(access_key, secret_key, query_params):
      # 1. 构造 Payload
      # 2. 计算 query_hash (SHA512)
      # 3. HMAC-SHA256 签名
      # 4. Base64 编码
      pass
  ```
- [ ] 实现 `core/gateway/upbit.py`（UpbitGateway）
  - [ ] `async def request()` 方法
  - [ ] `async def ws_connect()` 方法
  - [ ] 连接池管理（aiohttp.ClientSession）
- [ ] 单元测试：
  - [ ] 测试 JWT 生成（对比参考代码的输出）
  - [ ] 测试公开 API 请求（获取 ticker）
  - [ ] 测试私有 API 请求（获取账户余额）

**验收标准**:
```python
# 能成功运行以下代码
async def test():
    gateway = UpbitGateway(access_key, secret_key)
    balance = await gateway.request('GET', '/v1/accounts', signed=True)
    print(balance)  # 应显示账户余额 JSON

asyncio.run(test())
```

---

#### Day 3-4: BithumbGateway 实现

**任务清单**:
- [ ] 实现 `core/gateway/auth/hmac_signer.py`（HMAC-SHA512 签名）
- [ ] 实现 `core/gateway/bithumb.py`（BithumbGateway）
- [ ] 单元测试（同 Upbit）

**特别注意**:
- Bithumb 的签名字符串拼接规则与 Upbit 不同
- 需要正确处理 URL 编码

---

#### Day 5: 限流模块

**任务清单**:
- [ ] 实现 `core/gateway/ratelimit/token_bucket.py`
  ```python
  class TokenBucket:
      def __init__(self, capacity, refill_rate):
          self.capacity = capacity
          self.tokens = capacity
          self.refill_rate = refill_rate  # tokens per second
          self.last_refill = time.time()

      async def acquire(self):
          # 等待直到有可用 token
          pass
  ```
- [ ] 在 Gateway 中集成限流：
  ```python
  class UpbitGateway:
      def __init__(self):
          self.limiter = TokenBucket(capacity=10, refill_rate=10)

      async def request(self, ...):
          await self.limiter.acquire()
          # 发送请求
  ```
- [ ] 压力测试：连续发送 100 个请求，验证限流生效

---

### Week 2: Parser & Wrapper Layer

#### Day 1-2: Parser Layer

**任务清单**:
- [ ] 实现 `core/parser/base.py`（BaseParser）
- [ ] 实现 `core/parser/upbit.py`（UpbitParser）
  - [ ] `parse_orderbook()` - 将 Upbit 的 JSON 转为 `OrderBook` 对象
  - [ ] `parse_balance()` - 将余额 JSON 转为 `Balance` 对象
  - [ ] `parse_order_result()` - 将订单结果转为 `OrderResult` 对象
- [ ] 实现 `core/parser/bithumb.py`（BithumbParser）
- [ ] 单元测试：
  - [ ] 使用真实 API 响应数据作为测试用例
  - [ ] 验证解析后的数据类型和值

**性能测试**:
```python
import time
import msgspec

# 测试 10000 次解析耗时
data = b'{"orderbook_units": [...]}'
start = time.time()
for _ in range(10000):
    msgspec.json.decode(data)
print(f"Time: {time.time() - start}s")  # 应 < 0.1s
```

---

#### Day 3-4: Wrapper Layer

**任务清单**:
- [ ] 实现 `core/wrapper/base.py`（BaseWrapper）
- [ ] 实现 `core/wrapper/upbit.py`（UpbitWrapper）
  - [ ] `get_ticker()`
  - [ ] `get_orderbook()`
  - [ ] `get_balance()`
  - [ ] `place_limit_order()`
  - [ ] `place_market_order()`
  - [ ] `cancel_order()`
  - [ ] `get_order_status()`
- [ ] 实现 `core/wrapper/bithumb.py`（BithumbWrapper）
- [ ] 集成测试：
  ```python
  async def test():
      wrapper = UpbitWrapper(gateway, parser)
      ob = await wrapper.get_orderbook('KRW-BTC')
      print(ob.bids[0].price)  # 应显示最优买价
  ```

---

#### Day 5: WebSocket 集成

**任务清单**:
- [ ] 在 Gateway 中实现 WebSocket 连接
- [ ] 实现心跳机制（60 秒无消息自动重连）
- [ ] 在 Wrapper 中添加订阅方法：
  ```python
  async def subscribe_orderbook(self, symbol, callback):
      async for message in self.gateway.ws_connect(url):
          orderbook = self.parser.parse_orderbook(message)
          await callback(orderbook)
  ```
- [ ] 测试：持续运行 1 小时，验证无断连

---

**Phase 1 里程碑验收**:

运行以下脚本，能正常输出数据：
```python
async def main():
    # 1. 创建 Wrapper
    upbit = UpbitWrapper(...)
    bithumb = BithumbWrapper(...)

    # 2. 获取订单簿
    upbit_ob = await upbit.get_orderbook('KRW-BTC')
    bithumb_ob = await bithumb.get_orderbook('BTC_KRW')

    # 3. 打印价差
    print(f"Upbit Bid: {upbit_ob.bids[0].price}")
    print(f"Bithumb Ask: {bithumb_ob.asks[0].price}")
    print(f"Spread: {upbit_ob.bids[0].price - bithumb_ob.asks[0].price}")

    # 4. 获取余额
    balance = await upbit.get_balance()
    print(f"My Balance: {balance}")

asyncio.run(main())
```

**输出示例**:
```
Upbit Bid: 95000000
Bithumb Ask: 94950000
Spread: 50000
My Balance: {'BTC': 0.5, 'KRW': 10000000}
```

---

## Phase 2: 业务逻辑层 (2 周)

### Week 3: OrderBook Manager

#### Day 1-2: 快照与增量更新

**任务清单**:
- [ ] 实现 `business/orderbook/snapshot.py`
  ```python
  class OrderBookSnapshot:
      def __init__(self, orderbook: OrderBook):
          self.bids = sorted(orderbook.bids, key=lambda x: x.price, reverse=True)
          self.asks = sorted(orderbook.asks, key=lambda x: x.price)
          self.sequence = orderbook.sequence
  ```
- [ ] 实现 `business/orderbook/delta.py`
  ```python
  class OrderBookDelta:
      def apply(self, snapshot, delta):
          # 根据 delta 更新 snapshot
          # 使用 bisect 模块保持有序
          pass
  ```
- [ ] 实现 `business/orderbook/manager.py`
  ```python
  class OrderBookManager:
      async def initialize(self, wrapper, symbol):
          # 获取全量快照
          pass

      async def start_streaming(self, wrapper, symbol):
          # 订阅 WebSocket 增量更新
          pass

      def get_top_n(self, n=10):
          # 返回最优 N 档
          pass
  ```

---

#### Day 3: 性能测试与优化

**任务清单**:
- [ ] 模拟高频更新：每秒 100 次增量更新
- [ ] 测试内存占用：持续运行 1 小时
- [ ] 优化：实现 Top 10 缓存
- [ ] 压力测试报告：
  - 平均更新延迟
  - 内存占用趋势
  - CPU 占用率

---

#### Day 4-5: 策略模块

**任务清单**:
- [ ] 实现 `business/strategy/base.py`（策略基类）
- [ ] 实现 `business/strategy/spread_arbitrage.py`
  ```python
  class SpreadArbitrageStrategy:
      def calculate_signal(self, upbit_ob, bithumb_ob):
          # 计算价差和方向
          pass

      def validate_signal(self, signal, balances):
          # 检查余额是否足够
          pass
  ```
- [ ] 实现 `business/strategy/signal.py`（信号数据结构）
- [ ] 单元测试：
  - [ ] 测试正常价差计算
  - [ ] 测试边界情况（余额不足、价格反向等）

---

### Week 4: 执行模块与风控

#### Day 1-2: 订单执行器

**任务清单**:
- [ ] 实现 `business/execution/executor.py`
  ```python
  class OrderExecutor:
      async def execute_arbitrage(self, signal):
          # 并发下单
          tasks = [
              self.upbit.place_market_order(...),
              self.bithumb.place_market_order(...)
          ]
          results = await asyncio.gather(*tasks, return_exceptions=True)
          return results

      async def handle_partial_failure(self, results):
          # 处理部分成功的情况
          # 可能需要取消已成功的订单
          pass
  ```
- [ ] 实现 `business/execution/state_machine.py`（订单状态跟踪）
- [ ] 测试：DryRun 模式（不真实下单，仅打印）

---

#### Day 3: 风控模块

**任务清单**:
- [ ] 实现 `business/risk/balance_checker.py`
  ```python
  class BalanceChecker:
      def check(self, exchange, currency, required_amount):
          # 检查余额是否足够
          pass

      def reserve(self, exchange, currency, amount):
          # 预留余额（防止并发问题）
          pass
  ```
- [ ] 实现 `business/risk/position_limiter.py`
  ```python
  class PositionLimiter:
      MAX_POSITION_BTC = 0.1
      MAX_POSITION_KRW = 5000000

      def validate(self, signal):
          # 检查是否超过限制
          pass
  ```
- [ ] 实现 `business/risk/circuit_breaker.py`
  ```python
  class CircuitBreaker:
      def __init__(self, failure_threshold=5, timeout=300):
          self.failures = 0
          self.state = 'CLOSED'  # CLOSED / OPEN / HALF_OPEN

      def record_failure(self):
          # 记录失败，可能触发熔断
          pass

      def can_execute(self):
          # 检查是否可以执行
          pass
  ```

---

#### Day 4-5: 主流程整合

**任务清单**:
- [ ] 编写 `main.py` 主流程：
  ```python
  async def main():
      # 1. 初始化 Wrapper
      upbit = UpbitWrapper(...)
      bithumb = BithumbWrapper(...)

      # 2. 初始化 OrderBook Manager
      upbit_ob_manager = OrderBookManager()
      await upbit_ob_manager.initialize(upbit, 'KRW-BTC')

      bithumb_ob_manager = OrderBookManager()
      await bithumb_ob_manager.initialize(bithumb, 'BTC_KRW')

      # 3. 启动 WebSocket 流
      asyncio.create_task(upbit_ob_manager.start_streaming(upbit, 'KRW-BTC'))
      asyncio.create_task(bithumb_ob_manager.start_streaming(bithumb, 'BTC_KRW'))

      # 4. 策略循环
      strategy = SpreadArbitrageStrategy()
      executor = OrderExecutor(upbit, bithumb)
      risk_manager = RiskManager()

      while True:
          # 获取最新订单簿
          upbit_ob = upbit_ob_manager.get_top_n(10)
          bithumb_ob = bithumb_ob_manager.get_top_n(10)

          # 计算信号
          signal = strategy.calculate_signal(upbit_ob, bithumb_ob)

          if signal:
              # 风控检查
              if risk_manager.validate(signal):
                  # 执行交易
                  await executor.execute_arbitrage(signal)

          await asyncio.sleep(0.1)  # 100ms 轮询
  ```
- [ ] DryRun 模式测试：持续运行 24 小时
- [ ] 收集数据：记录所有触发的信号和模拟收益

---

**Phase 2 里程碑验收**:

**验收标准**:
- ✅ 程序能 24 小时稳定运行不崩溃
- ✅ 控制台输出类似：
  ```
  [2025-11-23 10:15:30] Signal Detected: upbit_sell, Spread: 0.52%, Volume: 0.05 BTC
  [2025-11-23 10:15:30] Risk Check: PASS
  [2025-11-23 10:15:30] [DryRun] Sell 0.05 BTC on Upbit at 95000000
  [2025-11-23 10:15:30] [DryRun] Buy 0.05 BTC on Bithumb at 94950000
  [2025-11-23 10:15:30] [DryRun] Estimated Profit: 25000 KRW (0.52%)
  ```
- ✅ 24 小时内至少捕获 50+ 个有效信号
- ✅ 无内存泄漏（内存占用稳定）

---

## Phase 3: 测试与优化 (1 周)

### Day 1-2: 单元测试与集成测试

**任务清单**:
- [ ] 编写单元测试（覆盖率 > 80%）：
  - [ ] Gateway 测试
  - [ ] Parser 测试
  - [ ] Wrapper 测试
  - [ ] Strategy 测试
  - [ ] Risk 测试
- [ ] 编写集成测试：
  - [ ] 完整流程测试（从订单簿更新到下单）
  - [ ] 异常恢复测试（WebSocket 断连、API 错误）
- [ ] 使用 `pytest` 运行所有测试：
  ```bash
  pytest tests/ --cov=core --cov=business --cov-report=html
  ```

---

### Day 3: 性能优化

**任务清单**:
- [ ] 使用 `cProfile` 分析性能瓶颈：
  ```bash
  python -m cProfile -o profile.stats main.py
  ```
- [ ] 使用 `snakeviz` 可视化：
  ```bash
  snakeviz profile.stats
  ```
- [ ] 优化热点代码：
  - [ ] OrderBook 更新逻辑
  - [ ] JSON 解析
- [ ] 优化后性能测试：
  - [ ] OrderBook 更新延迟 < 5ms
  - [ ] 内存占用 < 500MB
  - [ ] CPU 占用 < 30%

---

### Day 4-5: 模拟交易验证

**任务清单**:
- [ ] 启用模拟账户（初始余额：1 BTC + 5000万 KRW）
- [ ] 运行 7 天模拟交易
- [ ] 收集数据：
  - [ ] 总交易次数
  - [ ] 成功率
  - [ ] 总收益 / 总亏损
  - [ ] 最大回撤
- [ ] 生成报告：`docs/simulation_report.md`

**验收标准**:
- ✅ 7 天内无系统崩溃
- ✅ 订单成功率 > 95%
- ✅ 模拟收益 > 0（即使微利也算通过）
- ✅ 无重大风控漏洞（如过度交易、余额为负）

---

## Phase 4: 生产部署 (3 天)

### Day 1: 部署准备

**任务清单**:
- [ ] 创建 AWS 账户并配置 Seoul 区域
- [ ] 启动 EC2 实例（t3.medium）
- [ ] 配置安全组（仅允许必要端口）
- [ ] 安装依赖：
  ```bash
  sudo apt update
  sudo apt install python3.11 python3.11-venv
  ```
- [ ] 配置 systemd service：
  ```ini
  [Unit]
  Description=K-Arb Trading Bot
  After=network.target

  [Service]
  Type=simple
  User=ubuntu
  WorkingDirectory=/home/ubuntu/k-arb
  ExecStart=/home/ubuntu/k-arb/.venv/bin/python main.py
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```

---

### Day 2: 监控与告警

**任务清单**:
- [ ] 配置 CloudWatch Logs：
  ```python
  # 在 logger.py 中添加 CloudWatch Handler
  import watchtower
  logger.addHandler(watchtower.CloudWatchLogHandler())
  ```
- [ ] 配置 CloudWatch Metrics：
  - 自定义指标：价差、订单成功率、余额
- [ ] 配置告警：
  - 余额低于阈值
  - 连续订单失败 > 5 次
  - WebSocket 断连 > 1 分钟
- [ ] 配置 Grafana Dashboard（可选）

---

### Day 3: 灰度上线

**任务清单**:
- [ ] 限制最大交易量（0.01 BTC / 次）
- [ ] 启动程序：
  ```bash
  sudo systemctl start k-arb
  sudo systemctl status k-arb
  ```
- [ ] 实时监控日志：
  ```bash
  sudo journalctl -u k-arb -f
  ```
- [ ] 运行 24 小时
- [ ] 验证：
  - [ ] 至少完成 1 笔真实交易
  - [ ] 无资金损失
  - [ ] 日志无 ERROR 级别错误

**里程碑**: 🎉 **系统正式上线**

---

## Phase 5: Rust 优化 (按需启动)

### 触发条件
满足以下任一条件时启动 Phase 5：
1. WebSocket 处理延迟 > 5ms（P99）
2. OrderBook 更新延迟 > 5ms（P99）
3. CPU 占用 > 50%
4. 需要支持 10+ 交易对同时套利

---

### Week 1-2: Parser 层 Rust 重写

**任务清单**:
- [ ] 创建 Rust 项目：
  ```bash
  cargo new --lib k-arb-parser
  ```
- [ ] 添加依赖：
  ```toml
  [dependencies]
  pyo3 = "0.20"
  serde = { version = "1.0", features = ["derive"] }
  serde_json = "1.0"
  ```
- [ ] 实现 Rust Parser：
  ```rust
  use pyo3::prelude::*;
  use serde::{Deserialize, Serialize};

  #[pyclass]
  struct OrderBook {
      #[pyo3(get)]
      symbol: String,
      #[pyo3(get)]
      bids: Vec<PriceLevel>,
      #[pyo3(get)]
      asks: Vec<PriceLevel>,
  }

  #[pyfunction]
  fn parse_orderbook(json_str: &str) -> PyResult<OrderBook> {
      // 使用 serde_json 解析
      Ok(orderbook)
  }

  #[pymodule]
  fn k_arb_parser(_py: Python, m: &PyModule) -> PyResult<()> {
      m.add_function(wrap_pyfunction!(parse_orderbook, m)?)?;
      Ok(())
  }
  ```
- [ ] 编译：
  ```bash
  maturin develop --release
  ```
- [ ] Python 中使用：
  ```python
  import k_arb_parser
  ob = k_arb_parser.parse_orderbook(json_data)
  ```
- [ ] 性能测试：对比 Python 版本，应有 5-10 倍提升

---

### Week 3-4: OrderBook Manager Rust 重写

**任务清单**:
- [ ] 使用 Rust BTreeMap 实现订单簿
- [ ] 实现增量更新逻辑
- [ ] 编译为 Python 扩展
- [ ] 替换 Python 版本
- [ ] 性能测试：更新延迟应 < 1ms

---

**Phase 5 里程碑**:
- ✅ 关键路径性能提升 10 倍以上
- ✅ 支持 10+ 交易对同时运行
- ✅ CPU 占用 < 20%

---

## 人员与资源规划

### 人员配置

| 阶段 | 开发人员 | 测试人员 | DevOps | 总计 |
|------|----------|----------|--------|------|
| Phase 0 | 1 | 0 | 0 | 1 |
| Phase 1-2 | 1-2 | 0 | 0 | 1-2 |
| Phase 3 | 1 | 1 | 0 | 2 |
| Phase 4 | 1 | 0 | 1 | 2 |
| Phase 5 | 1 (需熟悉 Rust) | 0 | 0 | 1 |

### 技能要求

**核心开发者** (必须):
- Python 异步编程（asyncio, aiohttp）
- 数据结构与算法
- 加密货币交易基础知识

**Rust 开发者** (Phase 5):
- Rust 所有权系统
- PyO3 绑定
- 性能优化经验

### 预算估算 (AWS 成本)

| 资源 | 规格 | 月成本 (USD) |
|------|------|-------------|
| EC2 t3.medium | 2 vCPU, 4GB RAM | ~$30 |
| CloudWatch | 日志 + 监控 | ~$10 |
| Elastic IP | 1 个 | ~$3 |
| **总计** | | **~$43/月** |

---

## 风险缓冲

### 时间缓冲
每个 Phase 预留 10% 的缓冲时间，用于：
- 不可预见的技术难题
- API 变更
- 交易所维护

### 技术风险应对
见 `RISK_ASSESSMENT.md`

---

## 下一步行动

完成本文档阅读后，立即开始：
1. ✅ 阅读 `PROJECT_ARCHITECTURE.md`
2. ✅ 阅读 `ACCEPTANCE_CRITERIA.md`
3. ✅ 创建项目看板（Trello / Jira / GitHub Projects）
4. ✅ 开始 Phase 0 Day 1 任务

---

**文档维护者**: 项目经理
**最后更新**: 2025-11-23
**下次审阅**: 每周五
