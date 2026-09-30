---
name: ehunt-shop-query
description: "按任意维度筛选并查看 Etsy 店铺，输出店铺竞争力与可对标经验。"
version: 1.2.1
agent_created: true
metadata:
  title: "店铺查询"
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

When native EHunt tools are unavailable, call the same etsyhunt-api data endpoints through this Skill's bundled client `scripts/ehunt_api.py` using the user's `EHUNT_AI_KEY`. The client sends `X-EHUNT-AI-KEY` and supports the shops resources required by this Skill. Resolve both paths relative to this Skill directory, and read `references/API.md` for endpoint and parameter details. Never invent data when the key is missing or the request fails. If `EHUNT_AI_KEY` is missing, explain that `EHUNT_AI_KEY` is the local environment variable and `X-EHUNT-AI-KEY` is the HTTP header added automatically by the client. Direct the user to create an `eh_ai_` key in the EHunt Agent API Key management page, provide the correct temporary configuration command for their operating system, ask them to confirm after setting it, then retry the original query. Do not ask the user to paste the key into chat, do not place it directly in a command argument, and never print or persist it. Only help configure a persistent user-level environment variable after the user explicitly requests and confirms that action.

Examples from this Skill directory:

```bash
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
python scripts/ehunt_api.py shops --json '{"country":"US","sort_by":"8","desc":"desc","page_size":10}'
python scripts/ehunt_api.py keywords --json '{"keyword":"wedding gift","long_tail":true,"page_size":10}'
```

Use only the commands needed by the current Skill. Analyze the returned `data.list`; preserve `data.item_count`, `data.credits_charged`, and any allowance fields in the interpretation.

# Instructions

帮用户筛选并查看 Etsy 店铺。用户要看的是「这些店为什么做得好、我能学什么」。
参数处理：能识别店铺名、店铺链接或筛选条件时，直接调用 search_shops；不要因为缺少非必要参数而确认。仅当店铺对象和查询意图都完全无法判断时，才调用 ask_clarification。
工作流：
1. 理解查询意图，提取筛选维度（关键词/店铺名/店铺URL/类目/国家/总销量/7天销量/总销售额/7天销售额/总收藏/7天收藏/总评论/7天评论/商品数/评分/开店时间等）。销量、销售额、收藏和评论均存在总量与近7天两种口径，必须按用户表达准确区分。
   参数映射：7天销量或周销量用 sales_weekly；总销量用 sales；7天收藏或周收藏用 favorites_weekly，总收藏用 favorites；7天评论或周评论用 reviews_weekly，总评论用 reviews；7天销售额用 revenue_7days，总销售额用 revenue_total；以上区间均使用 min~max。商品数用 products；评分用 rating。类目传名称或完整路径即可，服务端按 product_category 表解析为 category_id；匹配不到时不要放宽为全类目查询。
   近N天开店用 listed_time=N，近一年开店用 listed_time=365；指定店铺URL必须设置 search_key_filter_type=store_url。
   按7天销量/周销量排序 sort_by=5，按7天评论/周评论排序 sort_by=6，按7天收藏/周收藏排序 sort_by=7，按总销量排序 sort_by=8，按商品数排序 sort_by=9，按开店时间排序 sort_by=10，按30天销量排序 sort_by=19，按总销售额排序 sort_by=20，按7天销售额排序 sort_by=21；店铺总评论和总收藏目前只支持区间筛选与结果展示，没有独立排序值，不得编造排序映射；最高/最多用 desc=desc，最低/最少用 desc=asc。
   美国店铺用 country=US；明星卖家用 is_star=1；有评论用 is_review=1；区间统一使用 min~max，单边范围留空一侧。
2. 调用 search_shops 取数；如果某个用户条件没有对应工具字段，使用最接近的已支持字段，并在结论中说明近似口径，不要静默丢弃条件。
   若用户要求指定店铺的商品、热销商品或新品，店铺查询只是定位步骤：从精确匹配结果的 _source 提取 shop_id/store_id，再调用 search_products。热销未指定周期时使用 sort_by=1、desc=true，Top N 使用 page_size=N；拿到商品结果前不得只返回店铺信息。
3. 表格列必须覆盖用户明确提到的筛选、排序和分析指标，并按用户提到的时间口径统一其他指标：用户提到某个周指标（周/7天/近7天）时，该指标必须同时展示周值和总值，其他销量、销售额、收藏、评论指标统一展示周值。例如用户提到“周收藏”，必须展示“周收藏、总收藏”，并展示“周评论、周销量、周销售额”；用户提到某个总指标时，该指标必须同时展示总值和周值，其他销量、销售额、收藏、评论指标统一展示总值。例如用户提到“总销量”，必须展示“总销量、周销量”，并展示“总收藏、总评论、总销售额”。如果用户同时明确要求多个不同口径，分别保留用户明确要求的指标，不得用默认口径覆盖。用户说开店时间时展示“开店时间”。其余列从店铺名、商品数、评分、发货地中补充。不得用月销量替代7天销量，也不得混用总量与周量字段。
   店铺表格列结构必须统一：第一列固定为店铺图片，第二列为店铺名称；国家、类目、开店时间、评分、商品数等每项信息分别独立成列，禁止把图片、店铺名称或其他不同信息合并到同一列。只有同一指标的总量和周量可以合并为一列，例如销量列写成“总 100 / 周 10”，销售额、收藏和评论同理；也可以按用户要求拆列。
4. 表格之后给出实质性分析，至少覆盖（有数据才写）：
   - 头部集中度：销量是否集中在少数店铺？头部店占比多少？
   - 店铺效率：单商品均销量（总销量 ÷ 商品数）谁最高？说明什么？
   - 口碑质量：评分与评论量是否匹配？低评分高销量说明什么？
   - 上新节奏：商品数与销量的关系，是大铺货还是精品店模式？
   - 地域特征：发货地分布对物流时效和定价的影响。
5. 给出可对标建议：这些店的做法里哪些可复制、哪些是壁垒，新卖家切入的差异点在哪。
语言与列头：严格跟随用户本轮输入语言输出，表格标题、列头、指标标签、缺失值说明和分析文字必须同语种；英文提问不得出现中文列头，中文提问使用中文列头。
输出格式：先表格，再分点分析（结论 + 依据），最后给可执行建议。要下判断，不要罗列数字。
统一 Markdown 展示规则：最终回复必须按标准 Markdown 格式组织和渲染，不得把 Markdown 语法放入代码块。只要输出商品或店铺查询列表，图片必须使用 `![名称](图片URL)` 语法展示工具返回的图片；商品标题和店铺名称必须使用 `[名称](URL)` Markdown 链接，分别链接到 https://ehunt.ai/product-detail/{商品ID} 和 https://ehunt.ai/store-detail/{店铺名称}。禁止输出 `<img>`、`<a>` 或依赖 `target`、`style` 等 HTML 标签和属性；链接打开方式由宿主客户端决定。优先使用工具返回的图片、ID和名称，缺少字段时如实说明，不得编造图片或链接。市场分析使用 Markdown 分节标题、短段落和项目符号，表格只保留核心指标，避免把所有分析文案塞进一张宽表。
