# Polymarket On-chain Data Indexer (Stage 1)

> **Polymarket 链上数据索引器**：基于 Python 构建的专业预测市场数据解析工具。

本项目的目标是深度解析 Polymarket（Polygon 链上）的交易行为与市场参数，涵盖从基础的日志解码到复杂的头寸（Position）衍生算法。当前处于 **移动阶段一：架构与解析核心**。

---

## 🚀 核心能力

- **Transaction Decoder (交易解析器)**：
    - 自动提取链上 `OrderFilled` 事件。
    - 智能判定交易方向 (BUY/SELL) 与价格计算。
    - 内置逻辑自动过滤 Taker 重复日志，确保数据准确性。
- **Market Decoder (市场解析器)**：
    - 支持通过 Gamma API Slug 或 `ConditionPreparation` 日志获取市场信息。
    - 完整实现 Gnosis CTF (Conditional Token Framework) 的 TokenId 衍生逻辑。
    - 实现链上计算值与 API 结果的 100% 对齐校验。
- **Modular Integration (模块化集成)**：
    - 集成 `Web3.py` 与链上原生交互。
    - 对接 Polymarket Gamma API 获取元数据。

---

## 🛠️ 环境准备

### 1. 基础要求
- Python 3.10+
- Polygon 网络 RPC 节点 (推荐使用 Alchemy 或 Infura)

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制根目录下的 `.env.example` 并重命名为 `.env`：
```bash
cp .env.example .env
```
在 `.env` 中填入你的 RPC 配置：
```env
RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```

---

## 📖 使用指南

### 1. 交易日志解码
解析指定交易哈希中的 Polymarket 撮合详情：
```bash
python -m src.trade_decoder --tx-hash 0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946
```

### 2. 市场参数解码
通过市场 Slug 计算该市场的 YES/NO TokenId 及其关联参数：
```bash
python -m src.market_decoder --market-slug will-there-be-another-us-government-shutdown-by-january-31
```

### 3. 综合演示
一键运行全流程演示（交易解析 + 市场元数据对齐）：
```bash
python -m src.demo --tx-hash <HASH> --event-slug <SLUG>
```

---

## 📂 项目结构

```text
.
├── src/
│   ├── ctf/                # Gnosis Conditional Token Framework 相关工具类
│   │   └── derive.py       # 实现 TokenId 衍生哈希算法
│   ├── indexer/            # 核心索引逻辑
│   │   └── gamma.py        # Polymarket Gamma API 集成
│   ├── trade_decoder.py    # 交易日志解析器核心
│   ├── market_decoder.py   # 市场参数解析器核心
│   └── demo.py             # 综合示例脚本
├── data/                   # 缓存与输出数据目录
├── .env.example            # 环境变量模板
└── stage1.md               # 阶段一技术设计文档
```

---

## 📊 输出定义

解析器输出的交易数据结构 (JSON 示例)：

```json
{
  "tx_hash": "0x916cad...",
  "price": "0.19",         // 成交单价 (USDC)
  "side": "BUY",           // 交易方向
  "token_id": "0x...",     // 参与交易的 Outcome TokenID
  "maker_amount": "19000", // Maker 支付数额 (原始精度)
  "taker_amount": "100000" // Taker 支付数额 (原始精度)
}
```

---

## ⚖️ 技术协议与背景

本项目深度依赖以下协议：
- **Gnosis Conditional Token Framework (CTF)**: 用于处理预测市场的支票与头寸。
- **Polymarket CLOB (Central Limit Order Book)**: 链上订单撮合引擎。
- **UMA Optimistic Oracle**: 作为市场结算的信标。

---

## 📝 贡献指南

1. 遵循 **KISS 原则**，代码应保持简洁。
2. 内部逻辑修改后，请务必运行 `src/demo.py` 进行回归测试。
