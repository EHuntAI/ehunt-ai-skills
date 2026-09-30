---
name: ehunt-competitor-analysis
description: "分析竞品店铺与商品矩阵，识别其优势、价格带与可切入机会。"
version: 1.2.1
agent_created: true
metadata:
  title: "竞品与店铺分析"
  source: ehunt-agent builtin skill
  api_base_url: https://ehunt.ai
  auth_header: X-EHUNT-AI-KEY
  auth_key_prefix: eh_ai_
  tools:
    - search_shops
    - search_products
  endpoints:
    search_shops: "POST /api/agent/data/shops/list"
    search_products: "POST /api/agent/data/products/list"
---

# Data access

Use the runtime's native EHunt tools when `search_products`, `search_shops`, or `research_keywords` are available. In ehunt-agent, these tools call the website endpoints with the internal `X-EHUNT-INTERNAL-KEY` and `X-EHUNT-USER-ID` credentials supplied by the site; never request, expose, or reuse those internal credentials.

When native EHunt tools are unavailable, call the same etsyhunt-api data endpoints through this Skill's bundled client `scripts/ehunt_api.py` using the user's `EHUNT_AI_KEY`. The client sends `X-EHUNT-AI-KEY` and supports the shops and products resources required by this Skill. Resolve both paths relative to this Skill directory, and read `references/API.md` for endpoint and parameter details. Never invent data when the key is missing or the request fails. If `EHUNT_AI_KEY` is missing, explain that `EHUNT_AI_KEY` is the local environment variable and `X-EHUNT-AI-KEY` is the HTTP header added automatically by the client. Direct the user to create an `eh_ai_` key in the EHunt Agent API Key management page, provide the correct temporary configuration command for their operating system, ask them to confirm after setting it, then retry the original query. Do not ask the user to paste the key into chat, do not place it directly in a command argument, and never print or persist it. Only help configure a persistent user-level environment variable after the user explicitly requests and confirms that action.

Examples from this Skill directory:

```bash
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
python scripts/ehunt_api.py shops --json '{"country":"US","sort_by":"8","desc":"desc","page_size":10}'
python scripts/ehunt_api.py keywords --json '{"keyword":"wedding gift","long_tail":true,"page_size":10}'
```

Use only the commands needed by the current Skill. Analyze the returned `data.list`; preserve `data.item_count`, `data.credits_charged`, and any allowance fields in the interpretation.

# Instructions

分析竞品店铺和商品矩阵，识别其优势、价格带和可切入机会。
工作流：
1. 理解用户的竞品分析目标（指定店铺或指定品类）。指定店铺URL时，search_shops 使用 search_key_filter_type=store_url；指定店铺名使用 store_name。
2. 调用 search_shops 和 search_products 获取用户请求数量的店铺与商品数据；未指定数量时使用各工具默认值；商品或店铺结果表都必须展示用户明确提到的周销量、总销量、销售额、上架/开店时间等指标；周销量优先使用工具返回的 sales_weekly，缺失时才使用等价的 sales_30days，并明确标注为周销量，禁止改称月销量。店铺排序使用 sort_by=5，缺失字段时使用总销量 sales 作为近似并标明口径。
3. 商品/店铺表格列必须覆盖用户明确提到的指标，不得只按固定模板输出；用户说周销量就展示周销量，用户说总销量就展示总销量，用户说上架/开店时间就展示对应时间，缺失字段须说明而不能静默省略。
4. 分析维度与判据：
   - 价格带分布：竞品集中在哪个区间？高价位是否有空档？
   - 销量分布：是单一爆款驱动还是均衡铺货？单点依赖风险有多大？
   - 上新频率：近期上新多的店在试探市场，上新少的店靠老品吃存量。
   - 口碑结构：评分分布是否健康？低分高销量说明什么？
   - 流量标签：Bestseller / Etsy Pick 占比反映其平台资源获取能力。
4. 识别竞品优势（价格/品类/流量/评价），找可切入的空白点。
语言与列头：严格跟随用户本轮输入语言输出，表格标题、列头、指标标签、缺失值说明和分析文字必须同语种；英文提问不得出现中文列头，中文提问使用中文列头。
输出格式：先给竞品店铺概览表格，再给商品矩阵分析表格，最后给 3-5 条可切入机会建议，每条说明为什么这个缝是打开着的、怎么占。
必须给出明确的切入结论，不要只描述竞品。
Markdown 展示规则：最终回复必须按标准 Markdown 格式组织和渲染，不得把 Markdown 语法放入代码块。竞品店铺画像表和商品矩阵表的第一列固定为对应图片，图片必须使用 `![名称](图片URL)` Markdown 图片语法；第二列固定为店铺名称或商品名称。国家、类目、商品所属店铺、价格等每项信息分别独立成列，禁止把图片、名称或其他不同信息合并到同一列。只有同一指标的总量和周量可以合并为一列，例如销量、销售额、收藏、评论分别写成“总值 / 周值”。店铺名称和商品标题必须使用 `[名称](URL)` Markdown 链接，分别链接到 https://ehunt.ai/store-detail/{店铺名称} 和 https://ehunt.ai/product-detail/{商品ID}。禁止输出 `<img>`、`<a>` 或依赖 `target`、`style` 等 HTML 标签和属性；链接打开方式由宿主客户端决定。优先使用工具返回的图片、ID和名称，缺少字段时如实说明，不得编造。市场分析使用 Markdown 分节标题、短段落和项目符号，店铺画像和商品矩阵分成两张表，最后单独列出切入动作。
