# Project K-Arb 验收标准文档

## 文档说明
本文档定义了 Project K-Arb 各开发阶段的详细验收标准、测试方法和交付物清单。每个阶段必须完成所有验收项才能进入下一阶段。

---

## 验收原则

### 1. 质量门禁 (Quality Gates)
每个阶段设置明确的质量门禁，包括：
- **功能完整性**: 所有计划功能已实现
- **代码质量**: 通过静态分析，无严重缺陷
- **测试覆盖率**: 单元测试覆盖率 > 80%
- **性能指标**: 满足性能要求
- **文档完整性**: 代码注释 + API 文档

### 2. 验收流程
```
开发完成 → 自测试 → 提交验收 → 评审 → 通过/退回 → 进入下一阶段
```

### 3. 验收角色
- **开发者**: 自测试并提交
- **Tech Lead**: 代码审查
- **QA**: 功能测试（Phase 3 开始）
- **Product Owner**: 最终验收

---

## Phase 0: 准备阶段验收标准

### 交付物清单

| # | 交付物 | 格式 | 负责人 |
|---|--------|------|--------|
| 1 | Python 环境配置文档 | `docs/setup/environment.md` | 开发者 |
| 2 | API 访问验证报告 | `docs/setup/api_verification.md` | 开发者 |
| 3 | 源码分析文档（5 份） | `references/analysis/*.md` | 开发者 |
| 4 | API 字段映射表 | `references/analysis/field_mapping.xlsx` | 开发者 |
| 5 | 项目骨架代码 | `core/`, `utils/`, `main.py` | 开发者 |

---

### 验收检查项

#### ✅ Checkpoint 0.1: 环境搭建

**验收命令**:
```bash
# 1. 检查 Python 版本
python --version  # 应输出: Python 3.11.x

# 2. 检查依赖安装
pip list | grep aiohttp  # 应显示 aiohttp 版本
pip list | grep msgspec  # 应显示 msgspec 版本

# 3. 验证虚拟环境
which python  # 应指向项目 .venv 目录
```

**通过标准**:
- ✅ Python 版本 >= 3.11
- ✅ 所有基础依赖已安装
- ✅ 虚拟环境激活成功

---

#### ✅ Checkpoint 0.2: API 访问

**测试脚本**: `scripts/verify_api_access.py`
```python
import aiohttp
import asyncio

async def test_upbit_public():
    async with aiohttp.ClientSession() as session:
        url = "https://api.upbit.com/v1/ticker"
        params = {"markets": "KRW-BTC"}
        async with session.get(url, params=params) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data[0]['market'] == 'KRW-BTC'
            print("✅ Upbit Public API: OK")

async def test_bithumb_public():
    async with aiohttp.ClientSession() as session:
        url = "https://api.bithumb.com/public/ticker/BTC_KRW"
        async with session.get(url) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data['status'] == '0000'
            print("✅ Bithumb Public API: OK")

asyncio.run(test_upbit_public())
asyncio.run(test_bithumb_public())
```

**执行验收**:
```bash
python scripts/verify_api_access.py
```

**通过标准**:
- ✅ 所有断言通过，无异常
- ✅ 输出显示 "✅ Upbit Public API: OK"
- ✅ 输出显示 "✅ Bithumb Public API: OK"

---

#### ✅ Checkpoint 0.3: 源码分析

**评审清单**:

| 文档 | 必须包含内容 | 页数要求 |
|------|-------------|----------|
| `auth_analysis.md` | JWT/HMAC 生成步骤 + 代码示例 | >= 2 页 |
| `api_endpoints.md` | 所有端点列表 + 参数说明 | >= 5 页 |
| `websocket_protocol.md` | 连接示例 + 消息格式 | >= 2 页 |
| `error_handling.md` | 错误码映射表 | >= 1 页 |
| `ratelimit.md` | 限流策略总结 | >= 1 页 |

**评审方式**: Tech Lead 人工审查

**通过标准**:
- ✅ 所有文档存在且符合页数要求
- ✅ 包含代码示例（非纯文字描述）
- ✅ 无明显理解错误

---

#### ✅ Checkpoint 0.4: 项目骨架

**目录结构检查**:
```bash
tree -L 3 -I '__pycache__|*.pyc|.venv'
```

**期望输出**:
```
.
├── core/
│   ├── __init__.py
│   ├── interface.py
│   ├── datatypes.py
│   └── exceptions.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── logger.py
├── config/
│   └── development.yaml
├── main.py
└── requirements.txt
```

**代码检查**:
```bash
# 1. 检查 interface.py 中是否定义了抽象基类
grep -q "class BaseGateway(ABC)" core/interface.py && echo "✅ BaseGateway defined"
grep -q "class BaseParser(ABC)" core/interface.py && echo "✅ BaseParser defined"
grep -q "class BaseWrapper(ABC)" core/interface.py && echo "✅ BaseWrapper defined"

# 2. 检查 datatypes.py 中是否定义了数据类
grep -q "@dataclass" core/datatypes.py && echo "✅ Dataclass used"
grep -q "class OrderBook" core/datatypes.py && echo "✅ OrderBook defined"

# 3. 运行 main.py
python main.py  # 应输出 "Hello World" 或类似内容
```

**通过标准**:
- ✅ 目录结构完整
- ✅ 所有核心接口已定义
- ✅ `python main.py` 成功运行

---

**Phase 0 最终验收**:
- ✅ 所有 Checkpoint 通过
- ✅ 所有交付物已提交
- ✅ Tech Lead 签字批准

---

## Phase 1: 基础设施层验收标准

### 交付物清单

| # | 交付物 | 格式 | 负责人 |
|---|--------|------|--------|
| 1 | Gateway 层代码 | `core/gateway/*.py` | 开发者 |
| 2 | Parser 层代码 | `core/parser/*.py` | 开发者 |
| 3 | Wrapper 层代码 | `core/wrapper/*.py` | 开发者 |
| 4 | 单元测试 | `tests/unit/core/*.py` | 开发者 |
| 5 | 集成测试 | `tests/integration/*.py` | 开发者 |
| 6 | API 文档 | `docs/api/core_api.md` | 开发者 |

---

### 验收检查项

#### ✅ Checkpoint 1.1: UpbitGateway 实现

**单元测试**: `tests/unit/core/gateway/test_upbit_gateway.py`

```python
import pytest
from core.gateway.upbit import UpbitGateway

@pytest.mark.asyncio
async def test_jwt_generation():
    """测试 JWT 生成逻辑"""
    gateway = UpbitGateway(access_key="test_key", secret_key="test_secret")
    token = gateway._generate_jwt(query_params={})
    assert isinstance(token, str)
    assert token.startswith("Bearer ")
    print("✅ JWT Generation: OK")

@pytest.mark.asyncio
async def test_public_api():
    """测试公开 API 请求"""
    gateway = UpbitGateway()
    result = await gateway.request('GET', '/v1/ticker', params={'markets': 'KRW-BTC'})
    assert isinstance(result, bytes)
    print("✅ Public API Request: OK")

@pytest.mark.asyncio
async def test_private_api():
    """测试私有 API 请求（需要真实 API Key）"""
    gateway = UpbitGateway(access_key=REAL_ACCESS_KEY, secret_key=REAL_SECRET_KEY)
    result = await gateway.request('GET', '/v1/accounts', signed=True)
    assert isinstance(result, bytes)
    print("✅ Private API Request: OK")

@pytest.mark.asyncio
async def test_rate_limiting():
    """测试限流功能"""
    gateway = UpbitGateway()
    start = time.time()
    # 发送 20 个请求
    tasks = [gateway.request('GET', '/v1/ticker', params={'markets': 'KRW-BTC'}) for _ in range(20)]
    await asyncio.gather(*tasks)
    elapsed = time.time() - start
    # 10 req/s, 20 个请求应至少花费 2 秒
    assert elapsed >= 2.0
    print("✅ Rate Limiting: OK")
```

**执行验收**:
```bash
pytest tests/unit/core/gateway/test_upbit_gateway.py -v
```

**通过标准**:
- ✅ 所有测试用例通过（4/4）
- ✅ 测试覆盖率 > 80%
- ✅ 无 lint 警告（`pylint core/gateway/upbit.py` 评分 > 8.0）

---

#### ✅ Checkpoint 1.2: BithumbGateway 实现

**单元测试**: `tests/unit/core/gateway/test_bithumb_gateway.py`

（类似 UpbitGateway 的测试结构）

**通过标准**: 同 Checkpoint 1.1

---

#### ✅ Checkpoint 1.3: Parser 层实现

**单元测试**: `tests/unit/core/parser/test_upbit_parser.py`

```python
import pytest
from core.parser.upbit import UpbitParser
from core.datatypes import OrderBook

def test_parse_orderbook():
    """测试订单簿解析"""
    # 使用真实 API 响应数据
    raw_data = b'''[{
        "market": "KRW-BTC",
        "timestamp": 1700000000000,
        "total_ask_size": 10.5,
        "total_bid_size": 8.3,
        "orderbook_units": [
            {"ask_price": 95000000, "bid_price": 94990000, "ask_size": 0.5, "bid_size": 0.3}
        ]
    }]'''

    parser = UpbitParser()
    orderbook = parser.parse_orderbook(raw_data)

    assert isinstance(orderbook, OrderBook)
    assert orderbook.symbol == 'KRW-BTC'
    assert len(orderbook.asks) > 0
    assert len(orderbook.bids) > 0
    assert orderbook.asks[0].price == 95000000
    print("✅ Parse OrderBook: OK")

def test_parse_balance():
    """测试余额解析"""
    raw_data = b'''[{
        "currency": "BTC",
        "balance": "1.5",
        "locked": "0.2",
        "avg_buy_price": "90000000"
    }]'''

    parser = UpbitParser()
    balances = parser.parse_balance(raw_data)

    assert len(balances) > 0
    assert balances[0].currency == 'BTC'
    assert balances[0].total == 1.7
    print("✅ Parse Balance: OK")
```

**性能测试**:
```python
import time

def test_parse_performance():
    """测试解析性能"""
    parser = UpbitParser()
    raw_data = b'[{"market": "KRW-BTC", ...}]'  # 真实数据

    start = time.time()
    for _ in range(10000):
        parser.parse_orderbook(raw_data)
    elapsed = time.time() - start

    # 10000 次解析应 < 0.1 秒（即 100,000 次/秒）
    assert elapsed < 0.1
    print(f"✅ Parse Performance: {10000/elapsed:.0f} ops/sec")
```

**通过标准**:
- ✅ 功能测试全部通过
- ✅ 性能测试 > 100,000 ops/sec
- ✅ 类型检查通过（`mypy core/parser/`）

---

#### ✅ Checkpoint 1.4: Wrapper 层实现

**集成测试**: `tests/integration/test_wrapper.py`

```python
import pytest
from core.gateway.upbit import UpbitGateway
from core.parser.upbit import UpbitParser
from core.wrapper.upbit import UpbitWrapper

@pytest.mark.asyncio
async def test_get_orderbook():
    """测试获取订单簿"""
    gateway = UpbitGateway()
    parser = UpbitParser()
    wrapper = UpbitWrapper(gateway, parser)

    orderbook = await wrapper.get_orderbook('KRW-BTC')

    assert orderbook.symbol == 'KRW-BTC'
    assert len(orderbook.bids) > 0
    assert len(orderbook.asks) > 0
    assert orderbook.bids[0].price < orderbook.asks[0].price  # 买价 < 卖价
    print("✅ Get OrderBook: OK")

@pytest.mark.asyncio
async def test_get_balance():
    """测试获取余额（需要真实 API Key）"""
    gateway = UpbitGateway(access_key=REAL_ACCESS_KEY, secret_key=REAL_SECRET_KEY)
    parser = UpbitParser()
    wrapper = UpbitWrapper(gateway, parser)

    balances = await wrapper.get_balance()

    assert isinstance(balances, list)
    assert len(balances) > 0
    print("✅ Get Balance: OK")

@pytest.mark.asyncio
async def test_place_order_dryrun():
    """测试下单（模拟模式）"""
    gateway = UpbitGateway(dry_run=True)
    parser = UpbitParser()
    wrapper = UpbitWrapper(gateway, parser)

    from core.datatypes import OrderRequest
    order_req = OrderRequest(
        exchange='upbit',
        symbol='KRW-BTC',
        side='buy',
        order_type='limit',
        price=90000000,
        quantity=0.001
    )

    result = await wrapper.place_order(order_req)

    assert result.status in ['pending', 'submitted']
    print("✅ Place Order (DryRun): OK")
```

**通过标准**:
- ✅ 所有集成测试通过
- ✅ 真实 API 调用成功（非模拟模式）
- ✅ 错误处理正确（测试各种异常情况）

---

#### ✅ Checkpoint 1.5: WebSocket 集成

**稳定性测试**: `tests/integration/test_websocket.py`

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_websocket_stability():
    """测试 WebSocket 稳定性（运行 1 小时）"""
    wrapper = UpbitWrapper(...)

    message_count = 0
    async def callback(orderbook):
        nonlocal message_count
        message_count += 1
        assert orderbook.symbol == 'KRW-BTC'

    # 运行 1 小时
    await asyncio.wait_for(
        wrapper.subscribe_orderbook('KRW-BTC', callback),
        timeout=3600
    )

    # 1 小时应至少收到 1000 条消息（平均 <4s 一条）
    assert message_count >= 1000
    print(f"✅ WebSocket Stability: {message_count} messages in 1 hour")

@pytest.mark.asyncio
async def test_websocket_reconnection():
    """测试断线重连"""
    wrapper = UpbitWrapper(...)

    reconnect_count = 0
    async def on_reconnect():
        nonlocal reconnect_count
        reconnect_count += 1

    wrapper.on_reconnect = on_reconnect

    # 运行 10 分钟，手动模拟网络中断
    # （或者使用 toxiproxy 等工具注入故障）
    await asyncio.sleep(600)

    # 应至少成功重连 1 次（如果发生断线）
    print(f"✅ WebSocket Reconnection: {reconnect_count} times")
```

**通过标准**:
- ✅ 1 小时无崩溃
- ✅ 断线后 10 秒内自动重连
- ✅ 重连后数据正常

---

**Phase 1 里程碑验收**:

**集成验收脚本**: `scripts/phase1_acceptance.py`
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
    spread = (upbit_ob.bids[0].price - bithumb_ob.asks[0].price) / bithumb_ob.asks[0].price
    print(f"Spread: {spread * 100:.2f}%")

    # 4. 获取余额
    balance = await upbit.get_balance()
    print(f"My Balance: {balance}")

    print("✅ Phase 1 Acceptance: PASSED")

asyncio.run(main())
```

**执行验收**:
```bash
python scripts/phase1_acceptance.py
```

**期望输出**:
```
Upbit Bid: 95000000
Bithumb Ask: 94950000
Spread: 0.05%
My Balance: [Balance(currency='BTC', total=0.5, ...)]
✅ Phase 1 Acceptance: PASSED
```

**最终检查**:
- ✅ 所有单元测试通过（覆盖率 > 80%）
- ✅ 所有集成测试通过
- ✅ WebSocket 稳定性测试通过
- ✅ 验收脚本运行成功
- ✅ 代码审查通过（Tech Lead 签字）

---

## Phase 2: 业务逻辑层验收标准

### 交付物清单

| # | 交付物 | 格式 | 负责人 |
|---|--------|------|--------|
| 1 | OrderBook Manager | `business/orderbook/*.py` | 开发者 |
| 2 | Strategy 模块 | `business/strategy/*.py` | 开发者 |
| 3 | Execution 模块 | `business/execution/*.py` | 开发者 |
| 4 | Risk 模块 | `business/risk/*.py` | 开发者 |
| 5 | 主流程代码 | `main.py` | 开发者 |
| 6 | DryRun 测试报告 | `docs/dryrun_report.md` | 开发者 |

---

### 验收检查项

#### ✅ Checkpoint 2.1: OrderBook Manager

**功能测试**: `tests/unit/business/test_orderbook_manager.py`

```python
import pytest
from business.orderbook.manager import OrderBookManager

@pytest.mark.asyncio
async def test_initialize():
    """测试初始化"""
    manager = OrderBookManager()
    await manager.initialize(wrapper, 'KRW-BTC')

    top10 = manager.get_top_n(10)
    assert len(top10['bids']) == 10
    assert len(top10['asks']) == 10
    print("✅ OrderBook Initialize: OK")

@pytest.mark.asyncio
async def test_delta_update():
    """测试增量更新"""
    manager = OrderBookManager()
    await manager.initialize(wrapper, 'KRW-BTC')

    initial_bid = manager.get_top_n(1)['bids'][0].price

    # 模拟一次增量更新
    from business.orderbook.delta import OrderBookDelta
    delta = OrderBookDelta(
        bids=[{'price': 95001000, 'quantity': 0.5}],
        asks=[]
    )
    manager.apply_delta(delta)

    updated_bid = manager.get_top_n(1)['bids'][0].price
    assert updated_bid >= initial_bid  # 价格应更新
    print("✅ OrderBook Delta Update: OK")

def test_update_performance():
    """测试更新性能"""
    manager = OrderBookManager()
    # ... 初始化

    import time
    start = time.time()
    for _ in range(10000):
        delta = OrderBookDelta(...)
        manager.apply_delta(delta)
    elapsed = time.time() - start

    avg_latency = (elapsed / 10000) * 1000  # ms
    assert avg_latency < 5  # 每次更新 < 5ms
    print(f"✅ OrderBook Update Performance: {avg_latency:.2f}ms")
```

**通过标准**:
- ✅ 功能测试通过
- ✅ 更新延迟 < 5ms (P99)
- ✅ 内存占用 < 100MB（单个订单簿）

---

#### ✅ Checkpoint 2.2: Strategy 模块

**单元测试**: `tests/unit/business/test_strategy.py`

```python
import pytest
from business.strategy.spread_arbitrage import SpreadArbitrageStrategy
from core.datatypes import OrderBook, PriceLevel

def test_calculate_signal_positive_spread():
    """测试正价差信号"""
    strategy = SpreadArbitrageStrategy(
        min_profit_rate=0.005,  # 0.5%
        upbit_fee=0.001,
        bithumb_fee=0.0025
    )

    # 构造测试数据
    upbit_ob = OrderBook(
        symbol='KRW-BTC',
        bids=[PriceLevel(price=95000000, quantity=0.5)],
        asks=[PriceLevel(price=95010000, quantity=0.5)]
    )

    bithumb_ob = OrderBook(
        symbol='BTC_KRW',
        bids=[PriceLevel(price=94980000, quantity=0.5)],
        asks=[PriceLevel(price=94950000, quantity=0.5)]
    )

    signal = strategy.calculate_signal(upbit_ob, bithumb_ob)

    assert signal is not None
    assert signal.direction == 'upbit_sell'  # Upbit 卖，Bithumb 买
    assert signal.expected_profit > 0.005
    print("✅ Calculate Signal (Positive Spread): OK")

def test_calculate_signal_no_opportunity():
    """测试无套利机会"""
    strategy = SpreadArbitrageStrategy(...)

    # 价差不足
    upbit_ob = OrderBook(...)
    bithumb_ob = OrderBook(...)

    signal = strategy.calculate_signal(upbit_ob, bithumb_ob)

    assert signal is None
    print("✅ Calculate Signal (No Opportunity): OK")

def test_validate_signal_insufficient_balance():
    """测试余额不足"""
    strategy = SpreadArbitrageStrategy(...)

    signal = Signal(direction='upbit_sell', volume=10.0)  # 需要 10 BTC
    balances = {
        'upbit': {'BTC': 0.5},  # 只有 0.5 BTC
        'bithumb': {'KRW': 100000000}
    }

    is_valid = strategy.validate_signal(signal, balances)

    assert is_valid == False
    print("✅ Validate Signal (Insufficient Balance): OK")
```

**通过标准**:
- ✅ 所有测试用例通过
- ✅ 信号计算逻辑正确
- ✅ 边界条件处理正确

---

#### ✅ Checkpoint 2.3: Execution 模块

**模拟测试**: `tests/integration/test_executor.py`

```python
import pytest
from business.execution.executor import OrderExecutor

@pytest.mark.asyncio
async def test_execute_arbitrage_dryrun():
    """测试并发下单（模拟模式）"""
    executor = OrderExecutor(upbit_wrapper, bithumb_wrapper, dry_run=True)

    signal = Signal(
        direction='upbit_sell',
        volume=0.05,
        upbit_price=95000000,
        bithumb_price=94950000
    )

    results = await executor.execute_arbitrage(signal)

    assert len(results) == 2
    assert all(r.status == 'submitted' for r in results)
    print("✅ Execute Arbitrage (DryRun): OK")

@pytest.mark.asyncio
async def test_handle_partial_failure():
    """测试部分失败处理"""
    executor = OrderExecutor(...)

    # 模拟一个成功，一个失败
    results = [
        OrderResult(status='filled', ...),
        Exception("Network Error")
    ]

    await executor.handle_partial_failure(results)

    # 应取消已成功的订单
    # （具体逻辑取决于设计）
    print("✅ Handle Partial Failure: OK")
```

**通过标准**:
- ✅ 并发下单成功
- ✅ 部分失败正确处理
- ✅ 状态机正确流转

---

#### ✅ Checkpoint 2.4: Risk 模块

**单元测试**: `tests/unit/business/test_risk.py`

```python
import pytest
from business.risk.balance_checker import BalanceChecker
from business.risk.circuit_breaker import CircuitBreaker

def test_balance_checker():
    """测试余额检查"""
    checker = BalanceChecker(balances={
        'upbit': {'BTC': 1.0, 'KRW': 50000000},
        'bithumb': {'BTC': 1.0, 'KRW': 50000000}
    })

    # 检查足够余额
    assert checker.check('upbit', 'BTC', 0.5) == True

    # 检查不足余额
    assert checker.check('upbit', 'BTC', 2.0) == False

    print("✅ Balance Checker: OK")

def test_circuit_breaker():
    """测试熔断器"""
    breaker = CircuitBreaker(failure_threshold=3, timeout=60)

    assert breaker.can_execute() == True

    # 记录 3 次失败
    for _ in range(3):
        breaker.record_failure()

    # 应熔断
    assert breaker.can_execute() == False
    assert breaker.state == 'OPEN'

    print("✅ Circuit Breaker: OK")

def test_circuit_breaker_recovery():
    """测试熔断恢复"""
    breaker = CircuitBreaker(failure_threshold=3, timeout=1)

    # 触发熔断
    for _ in range(3):
        breaker.record_failure()

    # 等待超时
    import time
    time.sleep(2)

    # 应恢复
    assert breaker.can_execute() == True

    print("✅ Circuit Breaker Recovery: OK")
```

**通过标准**:
- ✅ 所有风控逻辑正确
- ✅ 熔断机制生效
- ✅ 恢复机制正常

---

#### ✅ Checkpoint 2.5: 主流程集成

**DryRun 测试**: 运行 24 小时模拟交易

**测试脚本**: `python main.py --dry-run`

**监控指标**:
```python
# 在 main.py 中记录统计数据
class Statistics:
    total_signals = 0
    valid_signals = 0
    executed_orders = 0
    failed_orders = 0
    total_profit = 0
    total_loss = 0

    def print_summary(self):
        print(f"""
        === 24 Hour DryRun Summary ===
        Total Signals: {self.total_signals}
        Valid Signals: {self.valid_signals}
        Executed Orders: {self.executed_orders}
        Failed Orders: {self.failed_orders}
        Total Profit: {self.total_profit} KRW
        Total Loss: {self.total_loss} KRW
        Net Profit: {self.total_profit - self.total_loss} KRW
        Success Rate: {self.executed_orders / self.valid_signals * 100:.2f}%
        """)
```

**通过标准**:
- ✅ 24 小时无崩溃
- ✅ 捕获信号 >= 50 个
- ✅ 执行成功率 >= 95%
- ✅ 模拟净收益 > 0
- ✅ 无内存泄漏（内存占用稳定）
- ✅ 日志无 ERROR（允许偶尔的网络 WARNING）

**Phase 2 最终验收**: Tech Lead 审查 DryRun 报告并签字

---

## Phase 3: 测试与优化验收标准

### 交付物清单

| # | 交付物 | 格式 | 负责人 |
|---|--------|------|--------|
| 1 | 单元测试套件 | `tests/unit/**/*.py` | 开发者 |
| 2 | 集成测试套件 | `tests/integration/**/*.py` | 开发者 |
| 3 | 性能测试报告 | `docs/performance_report.md` | 开发者 |
| 4 | 模拟交易报告 | `docs/simulation_report.md` | QA |
| 5 | 代码覆盖率报告 | `htmlcov/index.html` | 开发者 |

---

### 验收检查项

#### ✅ Checkpoint 3.1: 测试覆盖率

**执行命令**:
```bash
pytest tests/ --cov=core --cov=business --cov-report=html --cov-report=term
```

**通过标准**:
- ✅ 总覆盖率 >= 80%
- ✅ 核心模块覆盖率 >= 90% (`core/gateway`, `core/parser`, `business/strategy`)
- ✅ 无未测试的关键路径

**覆盖率报告示例**:
```
Name                               Stmts   Miss  Cover
------------------------------------------------------
core/gateway/upbit.py                150     10    93%
core/parser/upbit.py                  80      5    94%
business/strategy/spread_arbitrage   120     15    88%
------------------------------------------------------
TOTAL                               1200    120    90%
```

---

#### ✅ Checkpoint 3.2: 性能优化

**性能测试**: `tests/performance/benchmark.py`

```python
import time
import asyncio
from business.orderbook.manager import OrderBookManager

async def benchmark_orderbook_updates():
    """基准测试：订单簿更新"""
    manager = OrderBookManager()
    await manager.initialize(...)

    # 测试 10000 次更新
    deltas = [generate_random_delta() for _ in range(10000)]

    start = time.time()
    for delta in deltas:
        manager.apply_delta(delta)
    elapsed = time.time() - start

    avg_latency = (elapsed / 10000) * 1000  # ms
    print(f"OrderBook Update: {avg_latency:.2f}ms per update")
    assert avg_latency < 5  # 目标: < 5ms

async def benchmark_json_parsing():
    """基准测试：JSON 解析"""
    parser = UpbitParser()
    raw_data = generate_sample_json()

    start = time.time()
    for _ in range(100000):
        parser.parse_orderbook(raw_data)
    elapsed = time.time() - start

    ops_per_sec = 100000 / elapsed
    print(f"JSON Parsing: {ops_per_sec:.0f} ops/sec")
    assert ops_per_sec > 100000  # 目标: > 100k ops/sec
```

**性能指标**:

| 指标 | 目标值 | 实测值 | 状态 |
|------|--------|--------|------|
| OrderBook 更新延迟 | < 5ms | ___ ms | ✅/❌ |
| JSON 解析速度 | > 100k ops/s | ___ ops/s | ✅/❌ |
| WebSocket 延迟 | < 10ms | ___ ms | ✅/❌ |
| 下单延迟 | < 50ms | ___ ms | ✅/❌ |
| 内存占用 | < 500MB | ___ MB | ✅/❌ |
| CPU 占用 | < 30% | ___ % | ✅/❌ |

**通过标准**: 所有指标达标

---

#### ✅ Checkpoint 3.3: 模拟交易验证

**测试周期**: 7 天连续运行

**监控脚本**: `scripts/monitor_simulation.py`
```python
import time
import psutil

def monitor():
    """监控系统资源和交易指标"""
    while True:
        # 1. 系统资源
        memory = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent()

        # 2. 交易指标（从日志解析）
        stats = parse_latest_stats()

        print(f"""
        [Monitor] {time.strftime('%Y-%m-%d %H:%M:%S')}
        Memory: {memory}% | CPU: {cpu}%
        Signals: {stats['total_signals']}
        Orders: {stats['executed_orders']}
        Profit: {stats['net_profit']} KRW
        """)

        time.sleep(60)  # 每分钟输出一次
```

**模拟交易报告**: `docs/simulation_report.md`

**必须包含**:
1. **概况**
   - 运行时长: 7 天
   - 初始资金: 1 BTC + 5000万 KRW（每个交易所）
   - 交易对: KRW-BTC

2. **交易统计**
   - 总信号数
   - 有效信号数
   - 执行订单数
   - 成功订单数
   - 失败订单数

3. **收益分析**
   - 总收益（KRW）
   - 总亏损（KRW）
   - 净收益（KRW）
   - 收益率（%）
   - 最大回撤（%）

4. **异常记录**
   - WebSocket 断连次数
   - API 错误次数
   - 风控拦截次数

5. **结论**
   - 系统稳定性评估
   - 盈利能力评估
   - 风险控制评估

**通过标准**:
- ✅ 7 天无崩溃
- ✅ 订单成功率 >= 95%
- ✅ 净收益 > 0（允许微利）
- ✅ 无重大风控漏洞
- ✅ WebSocket 断连后均成功重连

---

**Phase 3 最终验收**:
- ✅ 所有性能指标达标
- ✅ 测试覆盖率 >= 80%
- ✅ 7 天模拟交易成功
- ✅ QA 签字批准
- ✅ Product Owner 最终审批

---

## Phase 4: 生产部署验收标准

### 交付物清单

| # | 交付物 | 格式 | 负责人 |
|---|--------|------|--------|
| 1 | 部署脚本 | `scripts/deploy.sh` | DevOps |
| 2 | 系统配置文件 | `k-arb.service` | DevOps |
| 3 | 监控 Dashboard | Grafana JSON | DevOps |
| 4 | 告警规则配置 | CloudWatch Alarms | DevOps |
| 5 | 运维手册 | `docs/operations.md` | DevOps |

---

### 验收检查项

#### ✅ Checkpoint 4.1: 部署验证

**部署流程**:
```bash
# 1. 连接 EC2
ssh ubuntu@<ec2-ip>

# 2. 克隆代码
git clone <repo-url> k-arb
cd k-arb

# 3. 运行部署脚本
./scripts/deploy.sh

# 4. 检查服务状态
sudo systemctl status k-arb
```

**验证命令**:
```bash
# 检查进程
ps aux | grep python

# 检查日志
sudo journalctl -u k-arb -n 50

# 检查网络连接
netstat -an | grep ESTABLISHED
```

**通过标准**:
- ✅ 服务成功启动
- ✅ 日志显示正常运行
- ✅ WebSocket 连接建立

---

#### ✅ Checkpoint 4.2: 监控验证

**CloudWatch 指标验证**:

| 指标名称 | 命名空间 | 数据来源 | 验收 |
|---------|---------|----------|------|
| `Spread` | KArb/Trading | 应用程序 | ✅ 有数据 |
| `OrderSuccessRate` | KArb/Trading | 应用程序 | ✅ 有数据 |
| `BalanceBTC` | KArb/Account | 应用程序 | ✅ 有数据 |
| `BalanceKRW` | KArb/Account | 应用程序 | ✅ 有数据 |
| `CPUUtilization` | AWS/EC2 | CloudWatch | ✅ 有数据 |
| `MemoryUtilization` | CWAgent | CloudWatch Agent | ✅ 有数据 |

**告警验证**:
```bash
# 手动触发告警测试
# 1. 测试低余额告警
aws cloudwatch put-metric-data --namespace KArb/Account \
  --metric-name BalanceKRW --value 500000

# 2. 检查是否收到告警邮件/短信
```

**通过标准**:
- ✅ 所有指标正常上报
- ✅ Grafana Dashboard 显示正常
- ✅ 告警触发正常

---

#### ✅ Checkpoint 4.3: 灰度运行

**灰度配置**:
```yaml
# config/production.yaml
trading:
  enabled: true
  max_volume_per_trade: 0.01  # 限制 0.01 BTC
  max_trades_per_day: 10       # 限制每天 10 笔
  min_profit_rate: 0.01        # 提高最小利润率到 1%
```

**运行监控**: 24 小时

**验收日志示例**:
```
[2025-11-30 10:00:00] INFO: System started in production mode
[2025-11-30 10:05:23] INFO: Signal detected, spread: 1.2%
[2025-11-30 10:05:23] INFO: Risk check: PASS
[2025-11-30 10:05:24] INFO: Order placed: Upbit SELL 0.01 BTC @ 95000000
[2025-11-30 10:05:24] INFO: Order placed: Bithumb BUY 0.01 BTC @ 94950000
[2025-11-30 10:05:25] INFO: Order filled: Upbit order_id=abc123
[2025-11-30 10:05:25] INFO: Order filled: Bithumb order_id=def456
[2025-11-30 10:05:25] INFO: Trade completed, profit: 4500 KRW (0.95%)
```

**通过标准**:
- ✅ 24 小时无异常停止
- ✅ 至少完成 1 笔真实交易
- ✅ 无资金损失
- ✅ 日志无 ERROR
- ✅ 所有交易符合风控规则

---

**Phase 4 最终验收**:
- ✅ 系统稳定运行 24 小时
- ✅ 真实交易验证通过
- ✅ 监控和告警正常
- ✅ 运维文档完整
- ✅ Product Owner 最终签字：**允许全量运行**

---

## Phase 5: Rust 优化验收标准

### 交付物清单

| # | 交付物 | 格式 | 负责人 |
|---|--------|------|--------|
| 1 | Rust Parser 库 | `.so` 文件 | Rust 开发者 |
| 2 | Rust OrderBook 库 | `.so` 文件 | Rust 开发者 |
| 3 | 性能对比报告 | `docs/rust_optimization_report.md` | Rust 开发者 |
| 4 | 集成测试 | `tests/integration/test_rust_modules.py` | 开发者 |

---

### 验收检查项

#### ✅ Checkpoint 5.1: Rust Parser

**性能对比测试**:
```python
import time
from core.parser.upbit import UpbitParser as PythonParser
from k_arb_parser_rust import UpbitParser as RustParser

def benchmark():
    data = b'...'  # 真实 JSON 数据

    # Python 版本
    parser_py = PythonParser()
    start = time.time()
    for _ in range(100000):
        parser_py.parse_orderbook(data)
    py_time = time.time() - start

    # Rust 版本
    parser_rust = RustParser()
    start = time.time()
    for _ in range(100000):
        parser_rust.parse_orderbook(data)
    rust_time = time.time() - start

    speedup = py_time / rust_time
    print(f"Python: {py_time:.2f}s")
    print(f"Rust: {rust_time:.2f}s")
    print(f"Speedup: {speedup:.2f}x")

    assert speedup >= 5  # 至少 5 倍提升
```

**通过标准**:
- ✅ 性能提升 >= 5 倍
- ✅ 功能测试通过（输出与 Python 版本一致）
- ✅ 内存占用更低

---

#### ✅ Checkpoint 5.2: Rust OrderBook

**性能对比测试**:
（类似 Parser 的测试方法）

**通过标准**:
- ✅ 更新延迟 < 1ms
- ✅ 性能提升 >= 10 倍
- ✅ 功能正确性验证通过

---

**Phase 5 最终验收**:
- ✅ 所有 Rust 模块集成成功
- ✅ 性能提升达到预期
- ✅ 生产环境验证通过
- ✅ 可支持 10+ 交易对同时运行

---

## 总验收报告

### 验收报告模板

```markdown
# Project K-Arb 验收报告

## 项目信息
- **项目名称**: Project K-Arb
- **验收阶段**: Phase X
- **验收日期**: YYYY-MM-DD
- **验收人**: XXX

## 验收结果概览
| 检查项 | 通过/失败 | 备注 |
|--------|----------|------|
| Checkpoint X.1 | ✅ PASS | |
| Checkpoint X.2 | ✅ PASS | |
| ... | ... | ... |

## 交付物检查
- [x] 交付物 1
- [x] 交付物 2
- ...

## 性能指标
| 指标 | 目标 | 实测 | 状态 |
|------|------|------|------|
| ... | ... | ... | ✅/❌ |

## 问题与风险
（列出验收过程中发现的问题）

## 改进建议
（对下一阶段的建议）

## 最终结论
☑️ **通过验收，允许进入下一阶段**
☐ **验收失败，需要返工**

---
**签字**:
- 开发者: ___________ 日期: ___________
- Tech Lead: ___________ 日期: ___________
- QA: ___________ 日期: ___________
- Product Owner: ___________ 日期: ___________
```

---

## 附录：自动化验收脚本

### 完整验收脚本: `scripts/run_acceptance.sh`

```bash
#!/bin/bash
set -e

PHASE=$1

if [ -z "$PHASE" ]; then
    echo "Usage: ./scripts/run_acceptance.sh <phase_number>"
    exit 1
fi

echo "========================================="
echo "Running Phase $PHASE Acceptance Tests"
echo "========================================="

case $PHASE in
    0)
        echo "✓ Checking Python version..."
        python --version | grep "3.11"

        echo "✓ Checking dependencies..."
        pip list | grep aiohttp
        pip list | grep msgspec

        echo "✓ Running API verification..."
        python scripts/verify_api_access.py

        echo "✓ Checking project structure..."
        test -f core/interface.py
        test -f core/datatypes.py
        test -f main.py

        echo "✅ Phase 0 Acceptance: PASSED"
        ;;

    1)
        echo "✓ Running unit tests..."
        pytest tests/unit/core/ -v --cov=core --cov-report=term

        echo "✓ Running integration tests..."
        pytest tests/integration/ -v

        echo "✓ Running Phase 1 acceptance script..."
        python scripts/phase1_acceptance.py

        echo "✅ Phase 1 Acceptance: PASSED"
        ;;

    2)
        echo "✓ Running all unit tests..."
        pytest tests/unit/ -v --cov=core --cov=business --cov-report=html

        echo "✓ Checking test coverage..."
        coverage report --fail-under=80

        echo "✓ Checking DryRun report..."
        test -f docs/dryrun_report.md

        echo "✅ Phase 2 Acceptance: PASSED"
        ;;

    3)
        echo "✓ Running performance tests..."
        python tests/performance/benchmark.py

        echo "✓ Checking simulation report..."
        test -f docs/simulation_report.md

        echo "✓ Verifying coverage..."
        coverage report --fail-under=80

        echo "✅ Phase 3 Acceptance: PASSED"
        ;;

    4)
        echo "✓ Checking service status..."
        sudo systemctl is-active k-arb

        echo "✓ Checking logs..."
        sudo journalctl -u k-arb -n 100 | grep -q "INFO"

        echo "✓ Checking CloudWatch metrics..."
        python scripts/verify_cloudwatch.py

        echo "✅ Phase 4 Acceptance: PASSED"
        ;;

    *)
        echo "Unknown phase: $PHASE"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "All acceptance tests passed! 🎉"
echo "========================================="
```

**使用方法**:
```bash
# 验收 Phase 1
./scripts/run_acceptance.sh 1

# 验收 Phase 2
./scripts/run_acceptance.sh 2
```

---

**文档维护者**: QA Team
**最后更新**: 2025-11-23
**下次审阅**: 每个 Phase 结束后
