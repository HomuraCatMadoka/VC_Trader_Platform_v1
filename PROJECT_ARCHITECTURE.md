# Project K-Arb 技术架构文档

## 文档版本
| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0 | 2025-11-23 | System Architect | 初始版本 |

---

## 1. 项目概览

### 1.1 项目定位
**Project K-Arb** 是一个专注于韩国加密货币市场的高性能现货套利系统，主要在 Upbit 和 Bithumb 两个交易所之间进行价差套利。

### 1.2 核心设计原则
1. **零第三方依赖**：底层通信和数据处理完全自主实现
2. **接口化设计**：所有核心组件基于抽象接口，便于替换和测试
3. **性能优先**：内存级订单簿维护，异步并发架构
4. **渐进式优化**：Python 原型 → Rust 混合优化
5. **风险可控**：多层风控机制，完善的状态监控

### 1.3 技术栈选型

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| 开发语言 | Python 3.11+ | 快速原型开发，丰富的异步生态 |
| 性能优化 | Rust (Future) | 热点路径优化，零成本抽象 |
| 网络通信 | aiohttp | 高性能异步 HTTP/WebSocket |
| 数据序列化 | msgspec | 比标准 json 快 10-50 倍 |
| 数据结构 | dataclasses + typing | 类型安全，IDE 友好 |
| 部署环境 | AWS Seoul (ap-northeast-2) | 网络延迟最小化 |

---

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Business Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Strategy   │  │   Executor   │  │ Risk Manager │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                           │                                 │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │           OrderBook Manager (Memory)               │    │
│  └────────────────────────┬───────────────────────────┘    │
└───────────────────────────┼──────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                      Core Layer                              │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────┐       │
│  │              Wrapper Layer                       │       │
│  │  ┌──────────────────┐    ┌──────────────────┐   │       │
│  │  │  UpbitWrapper    │    │ BithumbWrapper   │   │       │
│  │  └────────┬─────────┘    └─────────┬────────┘   │       │
│  └───────────┼──────────────────────────┼───────────┘       │
│              │                          │                   │
│  ┌───────────▼──────────┐  ┌───────────▼──────────┐        │
│  │   Parser Layer       │  │   Gateway Layer      │        │
│  │  ┌────────────────┐  │  │  ┌────────────────┐ │        │
│  │  │ UpbitParser    │  │  │  │ UpbitGateway   │ │        │
│  │  │ BithumbParser  │  │  │  │ BithumbGateway │ │        │
│  │  └────────────────┘  │  │  └────────────────┘ │        │
│  └──────────────────────┘  └─────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Exchanges   │
                    │ Upbit/Bithumb │
                    └───────────────┘
```

### 2.2 目录结构设计

```
k-arb/
├── docs/                           # 项目文档
│   ├── architecture/               # 架构设计文档
│   ├── api/                        # API 文档
│   └── deployment/                 # 部署文档
│
├── references/                     # 参考代码区（只读）
│   ├── pyupbit/                    # Upbit Python SDK 源码
│   ├── pybithumb/                  # Bithumb Python SDK 源码
│   └── analysis/                   # 源码分析笔记
│       ├── upbit_analysis.md       # Upbit API 分析
│       └── bithumb_analysis.md     # Bithumb API 分析
│
├── core/                           # 核心引擎层
│   ├── __init__.py
│   ├── interface.py                # 抽象基类定义
│   ├── datatypes.py                # 统一数据结构
│   ├── exceptions.py               # 自定义异常
│   │
│   ├── gateway/                    # 网络通信层
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseGateway 抽象类
│   │   ├── upbit.py                # UpbitGateway 实现
│   │   ├── bithumb.py              # BithumbGateway 实现
│   │   ├── auth/                   # 鉴权模块
│   │   │   ├── jwt_native.py      # 原生 JWT 实现
│   │   │   └── hmac_signer.py     # HMAC 签名实现
│   │   └── ratelimit/              # 限流模块
│   │       ├── token_bucket.py    # 令牌桶算法
│   │       └── exchange_limits.py # 交易所限制配置
│   │
│   ├── parser/                     # 数据解析层
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseParser 抽象类
│   │   ├── upbit.py                # UpbitParser 实现
│   │   └── bithumb.py              # BithumbParser 实现
│   │
│   └── wrapper/                    # API 封装层
│       ├── __init__.py
│       ├── base.py                 # BaseWrapper 抽象类
│       ├── upbit.py                # UpbitWrapper 实现
│       └── bithumb.py              # BithumbWrapper 实现
│
├── business/                       # 业务逻辑层
│   ├── __init__.py
│   ├── orderbook/                  # 订单簿管理
│   │   ├── __init__.py
│   │   ├── manager.py              # OrderBook 管理器
│   │   ├── snapshot.py             # 快照处理
│   │   └── delta.py                # 增量更新
│   │
│   ├── strategy/                   # 策略模块
│   │   ├── __init__.py
│   │   ├── base.py                 # 策略基类
│   │   ├── spread_arbitrage.py    # 价差套利策略
│   │   └── signal.py               # 信号生成器
│   │
│   ├── execution/                  # 执行模块
│   │   ├── __init__.py
│   │   ├── executor.py             # 订单执行器
│   │   ├── state_machine.py       # 订单状态机
│   │   └── concurrent.py           # 并发执行管理
│   │
│   └── risk/                       # 风控模块
│       ├── __init__.py
│       ├── balance_checker.py     # 余额检查
│       ├── position_limiter.py    # 仓位限制
│       └── circuit_breaker.py     # 熔断机制
│
├── utils/                          # 工具模块
│   ├── __init__.py
│   ├── logger.py                   # 日志工具
│   ├── config.py                   # 配置管理
│   ├── metrics.py                  # 性能监控
│   └── alert.py                    # 告警通知
│
├── tests/                          # 测试目录
│   ├── unit/                       # 单元测试
│   ├── integration/                # 集成测试
│   └── fixtures/                   # 测试数据
│
├── scripts/                        # 脚本工具
│   ├── setup_env.sh                # 环境设置
│   ├── deploy.sh                   # 部署脚本
│   └── monitor.py                  # 监控脚本
│
├── config/                         # 配置文件
│   ├── development.yaml            # 开发环境配置
│   ├── production.yaml             # 生产环境配置
│   └── secrets.yaml.template       # 密钥模板
│
├── main.py                         # 程序入口
├── requirements.txt                # Python 依赖
├── pyproject.toml                  # 项目配置
└── README.md                       # 项目说明
```

---

## 3. 核心模块详细设计

### 3.1 Interface Layer (接口层)

**文件**: `core/interface.py`

**职责**: 定义所有核心组件的抽象接口

```python
# 核心接口定义（伪代码）
class BaseGateway(ABC):
    """网络通信基类"""
    @abstractmethod
    async def request(self, method, endpoint, params, signed) -> bytes

    @abstractmethod
    async def ws_connect(self, url) -> AsyncIterator[bytes]

    @abstractmethod
    async def close(self)

class BaseParser(ABC):
    """数据解析基类"""
    @abstractmethod
    def parse_orderbook(self, raw_data: bytes) -> OrderBook

    @abstractmethod
    def parse_balance(self, raw_data: bytes) -> Balance

    @abstractmethod
    def parse_order_result(self, raw_data: bytes) -> OrderResult

class BaseWrapper(ABC):
    """API 封装基类"""
    @abstractmethod
    async def get_orderbook(self, symbol: str) -> OrderBook

    @abstractmethod
    async def get_balance(self) -> Balance

    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResult
```

**设计要点**:
- 使用 Python ABC (抽象基类) 强制子类实现接口
- 所有异步方法返回明确的类型提示
- 为未来 Rust 集成预留标准化数据结构

---

### 3.2 DataTypes (数据类型层)

**文件**: `core/datatypes.py`

**职责**: 定义系统内所有标准化数据结构

**核心数据结构**:

```python
@dataclass
class PriceLevel:
    """价格档位"""
    price: Decimal
    quantity: Decimal
    timestamp: int  # Unix timestamp in milliseconds

@dataclass
class OrderBook:
    """统一订单簿"""
    symbol: str
    exchange: str  # 'upbit' or 'bithumb'
    bids: List[PriceLevel]  # 买单，价格降序
    asks: List[PriceLevel]  # 卖单，价格升序
    sequence: int  # 序列号，用于处理 WS 乱序
    timestamp: int

@dataclass
class Balance:
    """账户余额"""
    exchange: str
    currency: str
    available: Decimal  # 可用余额
    locked: Decimal     # 冻结余额
    total: Decimal      # 总余额

@dataclass
class OrderRequest:
    """下单请求"""
    exchange: str
    symbol: str
    side: str  # 'buy' or 'sell'
    order_type: str  # 'limit' or 'market'
    price: Optional[Decimal]
    quantity: Decimal

@dataclass
class OrderResult:
    """订单结果"""
    order_id: str
    exchange: str
    symbol: str
    status: str  # 'pending', 'filled', 'cancelled', 'failed'
    filled_quantity: Decimal
    average_price: Optional[Decimal]
```

---

### 3.3 Gateway Layer (通信层)

#### 3.3.1 核心功能
1. **连接管理**: TCP Keep-Alive，连接池复用
2. **请求签名**:
   - Upbit: JWT (HS256) + Query Hash
   - Bithumb: HMAC-SHA512
3. **限流控制**: 基于令牌桶的请求限流
4. **错误处理**: 自动重试，指数退避

#### 3.3.2 鉴权实现细节

**Upbit JWT 生成** (`core/gateway/auth/jwt_native.py`):
```
步骤:
1. 构造 Payload: {"access_key": "...", "nonce": "..."}
2. 如果有查询参数，计算 SHA512 Hash 并加入 Payload
3. 使用 Secret Key 进行 HS256 签名
4. 构造 Header: "Bearer {jwt_token}"
```

**Bithumb HMAC 签名** (`core/gateway/auth/hmac_signer.py`):
```
步骤:
1. 拼接字符串: endpoint + "\0" + json(params) + "\0" + nonce
2. 使用 Secret Key 进行 HMAC-SHA512
3. 添加到 Header: "Api-Sign: {signature}"
```

#### 3.3.3 限流策略

| 交易所 | REST API | WebSocket | 策略 |
|--------|----------|-----------|------|
| Upbit | 10 req/sec (Public)<br>8 req/sec (Private) | 5 connections | Token Bucket (容量=10, 速率=10/s) |
| Bithumb | 20 req/sec | 无限制 | Token Bucket (容量=20, 速率=20/s) |

---

### 3.4 Parser Layer (解析层)

**设计要点**:
- 使用 `msgspec` 库进行高性能 JSON 解析
- 字段映射表驱动，便于维护
- 异常数据降级处理（打日志但不中断）

**字段映射示例**:

| 原始字段 (Upbit) | 原始字段 (Bithumb) | 统一字段 |
|------------------|--------------------| ---------|
| `orderbook_units` | `order_currency` | `bids/asks` |
| `bid_price` | `price` | `price` |
| `ask_size` | `quantity` | `quantity` |

---

### 3.5 Wrapper Layer (封装层)

**设计模式**: 组合模式 (Composition)

**核心方法清单**:

```python
class UpbitWrapper:
    # 行情相关
    async def get_ticker(self, symbol)
    async def get_orderbook(self, symbol)
    async def get_trades(self, symbol)

    # 账户相关
    async def get_balance(self)
    async def get_all_balances(self)

    # 交易相关
    async def place_limit_order(self, symbol, side, price, quantity)
    async def place_market_order(self, symbol, side, quantity)
    async def cancel_order(self, order_id)
    async def get_order_status(self, order_id)

    # WebSocket
    async def subscribe_orderbook(self, symbol, callback)
    async def subscribe_trades(self, symbol, callback)
```

**注意事项**:
- 所有方法必须参考 `references/` 目录下的源码实现
- 每个方法需要注释说明对应的官方 API 端点
- 错误码映射为统一的异常类型

---

### 3.6 OrderBook Manager (订单簿管理)

#### 3.6.1 数据结构选择

**方案对比**:
| 方案 | 插入复杂度 | 查询 Top N | 内存占用 | 选择 |
|------|-----------|-----------|----------|------|
| List + bisect | O(n) | O(1) | 低 | ✅ 初期使用 |
| SortedDict (sortedcontainers) | O(log n) | O(log n) | 中 | 备选 |
| Red-Black Tree (Rust) | O(log n) | O(log n) | 低 | 终极方案 |

#### 3.6.2 更新逻辑

```
初始化:
1. 调用 Wrapper.get_orderbook() 获取全量快照
2. 存储 sequence number

增量更新 (WebSocket):
1. 检查 sequence 是否连续
2. 如果跳跃 > 5，重新拉取快照
3. 根据价格定位需要更新的档位
4. 如果 quantity = 0，删除该档位
5. 否则更新或插入
```

#### 3.6.3 性能优化

- **懒删除**: 标记删除，定期批量清理
- **缓存 Top 10**: 单独存储最优 10 档，避免频繁排序
- **内存预分配**: 初始化时预分配 100 档空间

---

### 3.7 Strategy Module (策略模块)

#### 3.7.1 核心策略：价差套利

**信号计算**:

```python
def calculate_signal(upbit_ob, bithumb_ob):
    """
    计算套利信号

    Returns:
        direction: 'upbit_sell' or 'bithumb_sell' or None
        expected_profit: Decimal (预期利润率)
        max_volume: Decimal (最大可交易量)
    """
    # 场景 1: Upbit 卖 + Bithumb 买
    upbit_bid_price = upbit_ob.bids[0].price
    bithumb_ask_price = bithumb_ob.asks[0].price

    spread_1 = (upbit_bid_price - bithumb_ask_price) / bithumb_ask_price

    # 场景 2: Bithumb 卖 + Upbit 买
    bithumb_bid_price = bithumb_ob.bids[0].price
    upbit_ask_price = upbit_ob.asks[0].price

    spread_2 = (bithumb_bid_price - upbit_ask_price) / upbit_ask_price

    # 费用和最小利润
    total_fee = UPBIT_FEE + BITHUMB_FEE  # 例如 0.001 + 0.0025 = 0.0035
    min_profit = 0.005  # 最小利润率 0.5%

    threshold = total_fee + min_profit

    if spread_1 > threshold:
        return 'upbit_sell', spread_1, min(
            upbit_ob.bids[0].quantity,
            bithumb_ob.asks[0].quantity
        )
    elif spread_2 > threshold:
        return 'bithumb_sell', spread_2, min(
            bithumb_ob.bids[0].quantity,
            upbit_ob.asks[0].quantity
        )
    else:
        return None, 0, 0
```

#### 3.7.2 风控参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MIN_PROFIT_RATE` | 0.5% | 最小利润率 |
| `MAX_POSITION_BTC` | 0.1 BTC | 单次最大交易量 |
| `MAX_POSITION_KRW` | 500万 KRW | 单次最大交易金额 |
| `DAILY_LOSS_LIMIT` | 100万 KRW | 日亏损限制 |
| `MIN_BALANCE_BTC` | 0.05 BTC | 最小保留 BTC |
| `MIN_BALANCE_KRW` | 100万 KRW | 最小保留 KRW |

---

### 3.8 Execution Module (执行模块)

#### 3.8.1 并发执行策略

```python
async def execute_arbitrage(signal):
    """
    并发执行套利订单
    """
    if signal.direction == 'upbit_sell':
        tasks = [
            upbit_wrapper.place_market_order('KRW-BTC', 'sell', signal.volume),
            bithumb_wrapper.place_market_order('BTC', 'buy', signal.volume)
        ]
    else:
        tasks = [
            bithumb_wrapper.place_market_order('BTC', 'sell', signal.volume),
            upbit_wrapper.place_market_order('KRW-BTC', 'buy', signal.volume)
        ]

    # 并发发送，最小化时间差
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 检查结果
    if any(isinstance(r, Exception) for r in results):
        # 处理部分失败的情况
        await handle_partial_failure(results)
```

#### 3.8.2 订单状态机

```
States: PENDING → SUBMITTED → FILLED / CANCELLED / FAILED

Transitions:
- PENDING → SUBMITTED: 订单已发送
- SUBMITTED → FILLED: 完全成交
- SUBMITTED → CANCELLED: 手动取消 / 超时取消
- SUBMITTED → FAILED: 余额不足 / 网络错误
```

---

## 4. 非功能性需求

### 4.1 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| WebSocket 延迟 | < 10ms | 接收时间戳 - 交易所时间戳 |
| 订单簿更新延迟 | < 5ms | 更新完成时间 - 接收时间 |
| 下单延迟 | < 50ms | 订单返回时间 - 发送时间 |
| 内存占用 | < 500MB | Python memory_profiler |
| CPU 占用 | < 30% | 单核心利用率 |

### 4.2 可靠性

1. **异常恢复**: 所有网络异常自动重试（最多 3 次，指数退避）
2. **状态持久化**: 关键状态（订单、余额）写入本地数据库
3. **心跳监控**: WebSocket 60 秒无数据自动重连
4. **熔断机制**: 连续 5 次失败触发熔断，暂停 5 分钟

### 4.3 可观测性

1. **日志**: 结构化日志 (JSON 格式)，包含 trace_id
2. **监控**:
   - 实时价差曲线
   - 订单成功率
   - 账户余额变化
3. **告警**:
   - 余额低于阈值
   - 连续订单失败
   - WebSocket 断连超过 1 分钟

---

## 5. 部署架构

### 5.1 开发环境
- **OS**: macOS / Linux
- **Python**: 3.11+ (pyenv 管理)
- **IDE**: VS Code + Pylance

### 5.2 生产环境

```
AWS EC2 (ap-northeast-2 - Seoul)
├── Instance Type: t3.medium (2 vCPU, 4GB RAM)
├── OS: Ubuntu 22.04 LTS
├── 运行方式: systemd service
├── 日志: CloudWatch Logs
└── 监控: CloudWatch Metrics + Grafana
```

**网络优化**:
- 使用 AWS Seoul 区域，最接近韩国交易所
- 启用 Enhanced Networking (SR-IOV)
- 使用 Elastic IP 确保稳定连接

---

## 6. 安全设计

### 6.1 API 密钥管理
- 使用 AWS Secrets Manager 存储
- 运行时通过环境变量注入
- 永远不在代码中硬编码

### 6.2 权限控制
- API Key 仅授予必要权限（交易 + 查询，禁止提现）
- IP 白名单限制（如果交易所支持）

### 6.3 审计
- 所有交易操作记录到审计日志
- 每日生成交易对账报告

---

## 7. 未来扩展

### 7.1 Rust 集成计划

**Phase 1**: 替换 Parser
- 使用 `serde_json` 替换 Python msgspec
- 通过 PyO3 编译为 `.so` 扩展

**Phase 2**: 替换 OrderBook Manager
- 使用 Rust BTreeMap 实现高性能订单簿
- 提供 Python 绑定接口

**Phase 3**: 完全迁移
- 核心引擎全部 Rust 实现
- Python 仅保留策略逻辑层

### 7.2 多交易所扩展
- 抽象设计已支持扩展新交易所
- 只需实现对应的 Gateway/Parser/Wrapper

### 7.3 高级策略
- 三角套利
- 跨期套利
- 做市策略

---

## 8. 参考资料

### 8.1 官方文档
- [Upbit API Docs](https://docs.upbit.com)
- [Bithumb API Docs](https://apidocs.bithumb.com)

### 8.2 技术参考
- [aiohttp Documentation](https://docs.aiohttp.org)
- [msgspec Documentation](https://jcristharif.com/msgspec/)
- [PyO3 Documentation](https://pyo3.rs)

---

**文档维护者**: 架构团队
**最后更新**: 2025-11-23
**下次审阅**: 每个开发阶段结束后
