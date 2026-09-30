---
name: ehunt-product-query
description: "按任意维度筛选并查看 Etsy 商品，输出可直接用于选品决策的分析结论。"
version: 1.2.1
agent_created: true
metadata:
  title: "商品查询"
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

When native EHunt tools are unavailable, call the same etsyhunt-api data endpoints through this Skill's bundled client `scripts/ehunt_api.py` using the user's `EHUNT_AI_KEY`. The client sends `X-EHUNT-AI-KEY` and supports the products resources required by this Skill. Resolve both paths relative to this Skill directory, and read `references/API.md` for endpoint and parameter details. Never invent data when the key is missing or the request fails. If `EHUNT_AI_KEY` is missing, explain that `EHUNT_AI_KEY` is the local environment variable and `X-EHUNT-AI-KEY` is the HTTP header added automatically by the client. Direct the user to create an `eh_ai_` key in the EHunt Agent API Key management page, provide the correct temporary configuration command for their operating system, ask them to confirm after setting it, then retry the original query. Do not ask the user to paste the key into chat, do not place it directly in a command argument, and never print or persist it. Only help configure a persistent user-level environment variable after the user explicitly requests and confirms that action.

Examples from this Skill directory:

```bash
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
python scripts/ehunt_api.py shops --json '{"country":"US","sort_by":"8","desc":"desc","page_size":10}'
python scripts/ehunt_api.py keywords --json '{"keyword":"wedding gift","long_tail":true,"page_size":10}'
```

Use only the commands needed by the current Skill. Analyze the returned `data.list`; preserve `data.item_count`, `data.credits_charged`, and any allowance fields in the interpretation.

# Instructions

帮用户按任意维度筛选并查看 Etsy 商品。用户要的不是数据搬运，而是「这个市场值不值得做、该怎么做」的决策依据。
参数处理：能从用户输入中识别商品关键词、链接、ID、类目或筛选条件时，直接调用工具；不要因为缺少非必要参数而确认。仅当商品对象和查询意图都完全无法判断时，才调用 ask_clarification。
工作流：
1. 理解查询意图，提取筛选维度（关键词/商品ID/商品URL/店铺名/店铺URL/类目/国家/价格区间/总销量/7天销量/销售额/总收藏/7天收藏/总评论/7天评论/商品类型/上架时间/排序字段等）。收藏和评论与销量一样存在总量和近7天两种口径，必须按用户表达准确区分。
   用户指定店铺名或店铺URL并要求该店商品时，必须先调用 search_shops 精确定位店铺：店铺名使用 search_key_filter_type=store_name，店铺URL使用 search_key_filter_type=store_url，page_size=1；然后从结果 _source 提取 shop_id/store_id，再调用 search_products。拿到商品结果前不得用店铺信息直接结束回答。
   “新品/最近 N 天”映射为 listed_time=N；“美国市场”优先映射为 ships_from=US；类目筛选应从用户表达中提取最关键的类目词，去掉“产品/商品/类/products/items/category”等泛化词，并转换为商品类目表使用的英文核心词，例如“数字产品”取 Digital、“家居产品”取 Home；不要把整段自然语言作为 category。服务端会先精确匹配 category_name，未命中再按 category_name 前缀匹配，并按表主键 id 升序取第一条；route_path 是类目 ID 层级链路，不用于名称匹配；“按总评论排序”映射为 sort_by=3、desc=true；“按总收藏排序”映射为 sort_by=4、desc=true；“按7天评论/周评论排序”映射为 sort_by=11、desc=true；“按7天收藏/周收藏排序”映射为 sort_by=12、desc=true；“按周销量/近7天销量排序”映射为 sort_by=1、desc=true；“按总销量排序”映射为 sort_by=2、desc=true；“热销”未指定周期时默认按周销量 sort_by=1、desc=true 并在结果中注明口径；“按月销量排序”映射为 sort_by=13、desc=true；“按上架时间排序”映射为 sort_by=16；“前 N 个”映射为 page_size=N。
2. 调用 search_products 取用户请求数量的商品数据；按店铺查询时必须传入上一步得到的 shop_id/store_id；未指定数量时使用工具默认值；禁止调用商品详情、历史数据或历史趋势能力。
3. 表格列必须覆盖用户明确提到的筛选、排序和分析指标，并按用户提到的时间口径统一其他指标：用户提到某个周指标（周/7天/近7天）时，该指标必须同时展示周值和总值，其他销量、收藏、评论指标统一展示周值。例如用户提到“周收藏”，必须展示“周收藏、总收藏”，并展示“周评论、周销量”；用户提到某个总指标时，该指标必须同时展示总值和周值，其他销量、收藏、评论指标统一展示总值。例如用户提到“总销量”，必须展示“总销量、周销量”，并展示“总收藏、总评论”。如果用户同时明确要求多个不同口径，分别保留用户明确要求的指标，不得用默认口径覆盖。用户说月销量时展示“月销量”；用户说上架时间时展示“上架时间”。不得用“月销量”或 monthly_sales 代替周销量。其余列从图片、标题、价格、店铺、发货地中补充。
   商品表格列结构必须统一：第一列固定为商品图片，第二列为商品名称；店铺名称、价格、上架时间等每项信息分别独立成列，禁止把图片、商品名称、店铺名称或其他不同信息合并到同一列。只有同一指标的总量和周量可以合并为一列，例如销量列写成“总 100 / 周 10”，收藏和评论同理；也可以按用户要求拆列。
   商品接口返回的 sales_weekly 是7天销量；sales_30days 在当前商品接口业务口径中也是7天销量的兼容字段；favorites_weekly 是7天收藏、favorites 是总收藏；reviews_weekly 是7天评论、reviews 是总评论。monthly_sales 不是月销量字段，除非用户明确要求月销量，否则不得将其标为月销量。表格是证据，不是结论。
4. 表格之后必须给出实质性分析，至少覆盖以下角度（有数据支撑才写，没有则跳过）：
   - 市场结构：价格带如何分布？主流价格区间在哪？有没有高价空间？
   - 需求验证：销量是否集中在少数爆款？头部占比多少？是长尾还是寡头？
   - 进入难度：评论数高的商品是否占据头部（说明老店壁垒高）？
     上新时间近但销量已起来的商品是否多（说明新品有突围机会）？
   - 动销质量：收藏/销量比、评论/销量比是否健康？比值过高可能转化差，过低可能刷量。
   - 竞争格局：头部店铺是否集中？头部卖家的共同特征（价格、风格、发货地）是什么？
   - 关键词匹配度：返回商品是否真的匹配用户意图？有无跑偏的品类需要提示用户。
5. 最后给出明确建议：这个方向适合什么样的卖家切入、主推什么价位、避开什么、定价与差异化可以怎么做。
语言与列头：严格跟随用户本轮输入语言输出，表格标题、列头、指标标签、缺失值说明和分析文字必须同语种；英文提问不得出现中文列头，中文提问使用中文列头。
输出格式：先表格，再分点分析（每点一句话结论 + 数据依据），最后给可执行建议。
分析要有观点、要下判断，不要只罗列数字，也不要写「仅供参考」这类空话。
统一 Markdown 展示规则：最终回复必须按标准 Markdown 格式组织和渲染，不得把 Markdown 语法放入代码块。只要输出商品或店铺列表，商品图片必须使用 `![商品名称](图片URL)` 语法展示工具返回的图片；商品标题和店铺名称必须使用 `[名称](URL)` Markdown 链接，分别链接到 https://ehunt.ai/product-detail/{商品ID} 和 https://ehunt.ai/store-detail/{店铺名称}。禁止输出 `<img>`、`<a>` 或依赖 `target`、`style` 等 HTML 标签和属性；链接打开方式由宿主客户端决定。优先使用工具返回的图片、ID和名称，缺少字段时如实说明，不得编造。市场分析使用 Markdown 分节标题、短段落和项目符号，表格只保留核心指标，避免把所有分析文案塞进一张宽表。
