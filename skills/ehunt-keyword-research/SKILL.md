---
name: ehunt-keyword-research
description: "研究关键词并产出 Listing 标题、标签与描述优化建议。"
version: 1.2.1
agent_created: true
metadata:
  title: "关键词研究与 Listing 优化"
  source: ehunt-agent builtin skill
  api_base_url: https://ehunt.ai
  auth_header: X-EHUNT-AI-KEY
  auth_key_prefix: eh_ai_
  tools:
    - research_keywords
    - search_products
  endpoints:
    research_keywords: "POST /api/agent/data/keywords/research"
    search_products: "POST /api/agent/data/products/list"
---

# Data access

Use the runtime's native EHunt tools when `search_products`, `search_shops`, or `research_keywords` are available. In ehunt-agent, these tools call the website endpoints with the internal `X-EHUNT-INTERNAL-KEY` and `X-EHUNT-USER-ID` credentials supplied by the site; never request, expose, or reuse those internal credentials.

When native EHunt tools are unavailable, call the same etsyhunt-api data endpoints through this Skill's bundled client `scripts/ehunt_api.py` using the user's `EHUNT_AI_KEY`. The client sends `X-EHUNT-AI-KEY` and supports the keywords and products resources required by this Skill. Resolve both paths relative to this Skill directory, and read `references/API.md` for endpoint and parameter details. Never invent data when the key is missing or the request fails. If `EHUNT_AI_KEY` is missing, explain that `EHUNT_AI_KEY` is the local environment variable and `X-EHUNT-AI-KEY` is the HTTP header added automatically by the client. Direct the user to create an `eh_ai_` key in the EHunt Agent API Key management page, provide the correct temporary configuration command for their operating system, ask them to confirm after setting it, then retry the original query. Do not ask the user to paste the key into chat, do not place it directly in a command argument, and never print or persist it. Only help configure a persistent user-level environment variable after the user explicitly requests and confirms that action.

Examples from this Skill directory:

```bash
python scripts/ehunt_api.py products --json '{"search_key":"personalized necklace","page_size":10}'
python scripts/ehunt_api.py shops --json '{"country":"US","sort_by":"8","desc":"desc","page_size":10}'
python scripts/ehunt_api.py keywords --json '{"keyword":"wedding gift","long_tail":true,"page_size":10}'
```

Use only the commands needed by the current Skill. Analyze the returned `data.list`; preserve `data.item_count`, `data.credits_charged`, and any allowance fields in the interpretation.

# Instructions

研究 Etsy 关键词并产出 Listing 标题、标签和描述优化建议。
工作流：
1. 理解用户的 Listing 优化目标（商品品类、当前关键词、目标市场等）。长尾词映射 long_tail=true，排除词映射 exclude，相关指标/竞争度区间统一使用 min~max。
2. 调用 research_keywords 和 search_products 获取用户请求数量的关键词与商品参考；未指定数量时使用各工具默认值；缺少直接字段时使用最接近的指标补偿，并说明口径。
3. 最终回复必须按标准 Markdown 格式组织和渲染，不得把 Markdown 语法放入代码块。关键词表格最多展示 7 列（不是 7 个关键词），优先展示用户提到的指标，并始终展示关键词和分数。不要展示“月搜索量”。浏览量、收藏量、销量、评论量均按总量和近一个月量区分；未指定总/月时默认展示近一个月指标。分数 = 使用此关键词的 Top100 热销商品总浏览量 ÷ 竞争度 ÷ 100；分数越高，代表搜索量越高或竞争度越低，越推荐使用。关键词名称必须使用 `[关键词](URL)` Markdown 链接，链接到 https://ehunt.ai/keyword-tool?keyword={关键词各单词以加号拼接}。禁止输出 `<a>` 或依赖 `target`、`style` 等 HTML 标签和属性；链接打开方式由宿主客户端决定。
4. 分析判据：
   - 主关键词选择：分数较高且与商品真实相关的 2-3 个词放在标题前段，不相关的关键词会拉低转化并影响平台权重。
   - 长尾词补充：浏览量中等但竞争度低的词，用于覆盖更精准的购买意图。
   - 竞品词参考：头部商品标题里反复出现的词，说明平台已认可其相关性。
   - 标签去重：13 个标签不要互相重复，要覆盖不同搜索意图（材质/风格/用途/尺寸/受众）。
4. 产出可直接使用的优化结果：推荐标题（含核心关键词，控制在 140 字符内）、13 个标签、描述优化要点。
语言与列头：严格跟随用户本轮输入语言输出，表格标题、列头、指标标签、缺失值说明和分析文字必须同语种；英文提问不得出现中文列头，中文提问使用中文列头。
输出格式：先给关键词机会表格，再给推荐 Listing 标题和标签列表，最后给 3-5 条描述优化建议。标题和标签必须是可直接复制使用的成品，不要给模板占位符。
如果输出头部商品或商品参考列表，第一列固定为商品图片，图片必须使用 `![商品名称](图片URL)` Markdown 图片语法；第二列为商品名称。商品所属店铺名称、价格等每项信息分别独立成列，禁止把图片、商品名称、店铺名称或其他不同信息合并到同一列。只有同一指标的总量和周量可以合并为一列。商品标题和商品所属店铺名称必须使用 `[名称](URL)` Markdown 链接，分别链接到 https://ehunt.ai/product-detail/{商品ID} 和 https://ehunt.ai/store-detail/{店铺名称}。禁止输出 `<img>`、`<a>` 或依赖 `target`、`style` 等 HTML 标签和属性；链接打开方式由宿主客户端决定。缺少图片或 ID 时如实说明，不得编造。关键词和 Listing 分析使用 Markdown 分节标题、短段落和项目符号，关键词表只保留核心指标，标题、Tags、描述建议分块展示。
