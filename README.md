# ehunt-ai-skills

EHunt AI Agent 的通用 Etsy 电商数据 Skill 库，共 6 个 Skill，分为基础查询层和研究分析层。所有 Skill 都遵循：先展示结构化数据，再输出有数据依据的分析结论。

> 当前 `skills/` 内容由 ehunt-agent 的内置 Skill 同步生成，版本为 `1.2.0`；每个 Skill 都包含可独立运行的 API 客户端和接口参考。

## 六个 Skill

| 层级 | Skill | 数据域 | 工具 |
|---|---|---|---|
| 基础查询层 | `ehunt-product-query` 商品查询 | 商品 | `search_shops`, `search_products` |
| 基础查询层 | `ehunt-shop-query` 店铺查询 | 店铺 | `search_shops`, `search_products` |
| 基础查询层 | `ehunt-keyword-query` 关键词查询 | 关键词 | `research_keywords` |
| 研究分析层 | `ehunt-product-research` 选品研究 | 商品 + 关键词 | `search_products`, `research_keywords` |
| 研究分析层 | `ehunt-competitor-analysis` 竞品与店铺分析 | 店铺 + 商品 | `search_shops`, `search_products` |
| 研究分析层 | `ehunt-keyword-research` 关键词研究与 Listing 优化 | 关键词 + 商品 | `research_keywords`, `search_products` |

基础查询层负责结构化查询、比较和基础判断；研究分析层负责机会发现、竞品拆解、关键词布局和可执行建议。

## 数据调用与鉴权

6 个 Skill 会直接查询 etsyhunt-api 的同一组数据端点，不经过第三方数据源：

```text
站内 ehunt-agent
  → X-EHUNT-INTERNAL-KEY + X-EHUNT-USER-ID
  → etsyhunt-api /api/agent/data/*

第三方 AI / 本地 Skill
  → 用户自己的 X-EHUNT-AI-KEY
  → etsyhunt-api /api/agent/data/*
```

两条链路最终解析为同一个 EHunt 用户，使用同一套数据服务、日额度、积分余额和计费账本。内部 Token 只用于站点与 ehunt-agent 之间，不写入公开仓库；第三方工具使用用户自己的 `eh_ai_` 前缀 API Key。

设置站外调用凭证：

```bash
# macOS / Linux（仅当前终端会话，输入时不回显）
read -s -p "EHunt AI Key: " EHUNT_AI_KEY && export EHUNT_AI_KEY && echo
```

```powershell
# Windows PowerShell（仅当前终端会话）
$env:EHUNT_AI_KEY = Read-Host "EHunt AI Key"
```

用户可在 ehunt.ai 的 Agent API Key 管理页面创建 `eh_ai_` 前缀的 Key。这里需要区分两个名称：用户配置的是本地环境变量 `EHUNT_AI_KEY`；每个 Skill 自带的 `scripts/ehunt_api.py` 会读取它，并自动转换为 HTTP 请求头 `X-EHUNT-AI-KEY`。用户不需要手动构造请求头。

如果安装后没有配置 Key，Skill 必须停止数据查询并引导用户完成配置：说明如何创建 Key、按当前操作系统给出临时环境变量命令、要求用户在自己的终端输入 Key（不得粘贴到 AI 对话中），随后重试原查询。只有用户明确要求并确认时，AI 才可协助配置持久化的用户级环境变量。

每个 Skill 均自带 `scripts/ehunt_api.py`，仅使用 Python 标准库，并通过 `X-EHUNT-AI-KEY` 请求生产接口。例如：

```bash
python skills/ehunt-product-query/scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
```

接口与参数说明见各 Skill 内的 `references/API.md`。

## Skill 选择边界

Skill 选择按完整用户意图判断，不按单个词硬匹配：

- 商品、价格、销量、热销、低于/高于某价格、商品列表或筛选，即使用户说“分析一下”，优先使用 `ehunt-product-query`。
- 只有明确要求市场机会、选品方向、商品与关键词交叉验证、需求验证、利润空间或切入建议，才使用 `ehunt-product-research`。
- `ehunt-product-query` 只调用商品工具；`ehunt-product-research` 先查商品，只有需要需求/季节性验证时再查关键词。
- 结果为空时不要重复改参数调用同一个工具；应说明暂无匹配数据并建议用户放宽条件。

## 安装全部 Skill

推荐使用 Skills CLI：

```bash
npx skills add EHuntAI/ehunt-ai-skills --all
```

安装指定 Skill：

```bash
npx skills add EHuntAI/ehunt-ai-skills --skill ehunt-product-query
```

## 工具与接口

| 工具 | 接口 |
|---|---|
| `search_products` | `POST /api/agent/data/products/list` |
| `search_shops` | `POST /api/agent/data/shops/list` |
| `research_keywords` | `POST /api/agent/data/keywords/research` |

站外调用使用 `X-EHUNT-AI-KEY`，值为用户的 `eh_ai_` 前缀 API Key；ehunt-agent 内部调用使用运行时注入的 service-to-service 鉴权，公开 Skill 只描述流程，不包含内部密钥值。

如果某个站点接口尚未开放，运行时应明确返回「能力暂未开放」，不能静默失败。

## 文件结构

```text
ehunt-ai-skills/
├── README.md
├── ONE_CLICK_PROMPT.md
└── skills/
    ├── ehunt-product-query/
    │   ├── SKILL.md
    │   ├── scripts/ehunt_api.py
    │   └── references/API.md
    ├── ehunt-shop-query/          # 同样包含 SKILL.md、scripts/、references/
    ├── ehunt-keyword-query/       # 同上
    ├── ehunt-product-research/    # 同上
    ├── ehunt-competitor-analysis/ # 同上
    └── ehunt-keyword-research/    # 同上
```

## GitHub 上传范围

上传当前目录中的全部剩余文件即可：

- `.gitignore`
- `README.md`
- `ONE_CLICK_PROMPT.md`
- `skills/` 下 6 个完整 Skill 目录

不要上传本地 IDE 配置、缓存、虚拟环境、环境变量文件或任何真实 API Key。`.gitignore` 已覆盖 `.idea/`、`.vscode/`、`__pycache__/`、`.venv/`、`.env*` 和 `node_modules/`。

## 本地验证

```bash
npx skills add . --list
npx skills add . --all
```

