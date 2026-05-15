<div align="center">

# AI Data Extraction Studio

**一个基于字段 Schema 的 AI 数据清洗与结构化抽取平台。**

*把表格里那些乱七八糟的自然语言文本，自动整理成干净的结构化数据表。无需编码。*

![Status][status-shield]
[![License: MIT][license-shield]][license-url]
![PRs Welcome][prs-shield]

[![Python][python-shield]][python-url]
[![FastAPI][fastapi-shield]][fastapi-url]
[![Pydantic][pydantic-shield]][pydantic-url]
[![SQLAlchemy][sqlalchemy-shield]][sqlalchemy-url]
[![SQLite][sqlite-shield]][sqlite-url]
[![Next.js][nextjs-shield]][nextjs-url]
[![TypeScript][typescript-shield]][typescript-url]
[![Tailwind CSS][tailwind-shield]][tailwind-url]
[![Anthropic Claude][anthropic-shield]][anthropic-url]
[![Docker][docker-shield]][docker-url]

[它能做什么](#它能做什么30-秒看懂) · [快速开始](#快速开始) · [使用手册](#使用手册) · [FAQ](#faq) · [评测](#评测) · [English](./README.md)

</div>

---

## 它能做什么（30 秒看懂）

你手头有一列长这样的 Excel 数据：

```
experience
─────────────────────────────────────────────────────────────────
2018年9月-2022年6月 北京大学 计算机科学与技术 本科
{"from":"2019","to":"2023","school":"MIT","major":"EE","degree":"MS"}
June 2018 - present, Google, Senior Software Engineer, search infra
Sept 2017 to May 2021 — University of Toronto, Mech Eng, BASc
2021年7月起，我加入字节跳动担任数据科学家至今
???
```

把这列丢给 AI Data Extraction Studio，几秒钟一行，得到这个：

```
from     to        school              major                  scholar    is_work    _status
─────────────────────────────────────────────────────────────────────────────────────────────
2018-09  2022-06   北京大学            计算机科学与技术       Bachelor   false      success
2019     2023      MIT                 Electrical Engineering Master     false      success
2018-06  present   Google              Senior SWE             —          true       success
2017-09  2021-05   University of Toronto  Mechanical Engineering Bachelor false      success
2021-07  present   字节跳动            数据科学家             —          true       success
—        —         —                   —                      —          —          archived
```

每个字段都能在网页上手动修改。整个 CSV/XLSX 一键下载。像 `???` 这种垃圾输入会被路由到独立的"归档"桶，不会污染你的数据集。

## 适合哪些人

- **任何手头有脏 Excel 列的人** —— 不想写代码、不想学 prompt engineering、不想把数据交给第三方 SaaS。
- **数据团队** —— 老是收到"帮我解析一下这个表"的一次性需求，需要一个可复用的内部工具。
- **正在调研 LLM 抽取管线的开发者** —— 想看一份带测试、带 1000 行评测脚手架、抽象清晰的参考实现。
- **正在做作品集的人** —— 这个仓库故意按"成熟开源项目"的样子组织，不是教程。

只要你会装 Docker Desktop 并能在终端跑一行命令，就能用这个工具。

## 快速开始

两条路，按你电脑上已经装了什么挑一条。

### 路径 1：我只是想用一下（Docker，约 5 分钟）

这条路不需要懂 Python、不需要懂 Node.js、不需要折腾 `pip install`。

**第 1 步 —— 装 Docker Desktop。** Mac / Windows / Linux 免费下载：<https://www.docker.com/products/docker-desktop/>。装完后启动一次，让那个鲸鱼图标停在菜单栏 / 任务栏上。

**第 2 步 —— 下载本仓库。** 在 GitHub 页面点绿色 "Code" 按钮 → "Download ZIP" → 解压到一个方便的位置。或者会用 git 的话：

```bash
git clone https://github.com/<your-username>/AI-Driven_Data_Cleaning_Pipeline.git
cd AI-Driven_Data_Cleaning_Pipeline
```

**第 3 步 —— 准备配置文件。** 在项目目录里打开终端，复制示例环境文件：

```bash
cp .env.example .env
```

不需要改 `.env` 也能跑 —— 默认是 **demo 模式**（不需要 API key）。等你想用真模型抽取时，再看下面的 [配置真实 AI](#配置真实-ai-anthropic)。

**第 4 步 —— 启动应用。** 一行命令：

```bash
docker compose up --build
```

首次构建大约 3 分钟（在拉两个容器镜像）。之后启动几秒钟。日志里看到这两行就 OK 了：

```
ai-data-extraction-api  | INFO:     Application startup complete.
ai-data-extraction-web  | ✓ Ready in 1.4s
```

**第 5 步 —— 打开 app。** 浏览器访问 <http://localhost:3000>。

就这样。直接跳到下面的 [使用手册](#使用手册) 走一遍 UI。

停止：终端里 `Ctrl+C`，或者 `docker compose down`。

### 路径 2：我是开发者（本地运行，约 3 分钟）

如果你要改代码，本地跑能用前后端热重载更舒服。

**前置条件：** Python 3.11+、Node.js 20+、npm。

```bash
git clone https://github.com/<your-username>/AI-Driven_Data_Cleaning_Pipeline.git
cd AI-Driven_Data_Cleaning_Pipeline
cp .env.example .env
```

**终端 1 —— 后端：**

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端在 <http://localhost:8000>，交互式 Swagger 文档在 <http://localhost:8000/docs>。

**终端 2 —— 前端：**

```bash
cd apps/web
npm install
npm run dev
```

UI 在 <http://localhost:3000>。

### 配置真实 AI（Anthropic）

Demo 模式用的是启发式 Mock 客户端，跑示例 CSV 能出像样的结果，但碰到没见过的输入就很弱。要真模型的抽取效果：

1. 到 <https://console.anthropic.com/settings/keys> 申请 API key。**只显示一次**，赶紧复制。
2. 编辑 `.env`：
   ```ini
   MODEL_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...你的key...
   ANTHROPIC_MODEL=claude-sonnet-4-6   # 模型档位见下面
   ```
3. 重启后端（`docker compose restart api` 或者重新跑 `uvicorn`）。

**选哪个模型？** `claude-sonnet-4-6` 是平衡推荐档。`claude-haiku-4-5` 更便宜更快（适合大批量）。`claude-opus-4-7` 质量最高（准确率比成本更重要时用）。

**成本** 大致随行数 × 模型档位线性增长。Sonnet 4.6 上清洗 1000 行 Excel 大约 **$0.40**。Haiku 大约便宜 10 倍。

## 使用手册

从"我刚打开浏览器"走到"我下载了清洗后的 CSV" —— 用自带示例，约 3 分钟。

### 首页 —— `/`

打开 <http://localhost:3000>。

```
┌──────────────────────────────────────────────────────────────────┐
│  AI Data Extraction Studio                          Upload  Run  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Turn messy spreadsheet text into clean structured tables.       │
│                                                                  │
│  [  Start Extraction  →  ]                                       │
│                                                                  │
│  Workflow:                                                       │
│    1. Upload Excel/CSV                                           │
│    2. Pick the input column                                      │
│    3. Run AI extraction                                          │
│    4. Review & edit                                              │
│    5. Export CSV / XLSX                                          │
└──────────────────────────────────────────────────────────────────┘
```

点 **Start Extraction**。

### 上传页 —— `/upload`

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 1 — Upload your file                                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │            ↥  Click to choose a file                     │    │
│  │            或试试 examples/education_experience_sample.csv│    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Preview — education_experience_sample.csv     [ Continue → ]    │
│  10 rows total · showing first 10                                │
│  ┌──┬────────────────┬───────────────────────────────────────┐   │
│  │id│name            │experience                             │   │
│  ├──┼────────────────┼───────────────────────────────────────┤   │
│  │ 1│张伟            │2018年9月-2022年6月 北京大学…         │   │
│  │ 2│Alice Johnson   │2015/09 - 2019/06, Stanford University │   │
│  │ 3│李娜            │2020.09~2023.07 清华大学 软件工程     │   │
│  └──┴────────────────┴───────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

- 支持格式：`.xlsx`、`.csv`。最大 25 MB。
- 自带示例：`examples/education_experience_sample.csv`（也有 `.xlsx` 版本）。
- 也可以拖拽到虚线框里。

点 **Continue**。

### 配置页 —— `/run`

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 2 — Configure extraction                                   │
│                                                                  │
│  File: education_experience_sample.csv · 10 rows                 │
│                                                                  │
│  Input column:    [ experience               ▼ ]                 │
│  Template:        [ Education Experience Cleaner ▼ ]             │
│  Max rows:        [ 100                          ]               │
│                                                                  │
│  [    Run Extraction    ]                                        │
│                                                                  │
│  ── Template fields ─────────────────                            │
│   • from               (string)                                  │
│   • to                 (string)                                  │
│   • school             (string)                                  │
│   • major              (string)                                  │
│   • scholar            (string)                                  │
│   • is_work_experience (boolean)   required                      │
└──────────────────────────────────────────────────────────────────┘
```

- **Input column** 列出 Excel 的所有表头，挑你想清洗的那一列。
- **Template** V1 只有 *Education Experience Cleaner*（6 个字段）。V2 会让你自定义。
- **Max rows** 限制本次处理多少行。第一次试建议设小一点（比如 10），先看效果再放量。

点 **Run Extraction**。

### 任务进度页 —— `/jobs/<id>`

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 3 — Job running                                            │
│                                                                  │
│  Job #7                          ████████░░░░░░  62%             │
│  Status: running                                                 │
│                                                                  │
│  ┌──────────┬───────────┬──────────┬────────┬──────────┐         │
│  │ Total    │ Processed │ Success  │ Failed │ Archived │         │
│  │   10     │     6     │    5     │   0    │    1     │         │
│  └──────────┴───────────┴──────────┴────────┴──────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

页面每 2 秒轮询一次。状态变成 `completed` 时自动跳转到结果页。中途出错（比如 Anthropic API 故障）会跳成 `failed`，并显示错误卡片 + 查看部分结果的链接。

### 结果页 —— `/results/<id>`

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 4 — Review & export                                        │
│  Job #7 · 8/10 success · 1 failed · 1 archived                   │
│                                                                  │
│       [ Retry failed ]   [ ↓ CSV ]   [ ↓ XLSX ]                  │
│                                                                  │
│  [ All (10) ] [ Success (8) ] [ Failed (1) ] [ Archived (1) ]    │
│                                                                  │
│  ┌─┬──────────────────────┬────────┬────────┬─────────┬──────┐   │
│  │#│ Input text           │ from   │ to     │ school  │ ✏    │   │
│  ├─┼──────────────────────┼────────┼────────┼─────────┼──────┤   │
│  │1│ 2018年9月-2022年6月 …│ 2018-09│ 2022-06│ 北京大学│ ✏    │   │
│  │2│ 2015/09 - 2019/06, … │ 2015-09│ 2019-06│ Stanford│ ✏    │   │
│  │3│ ???                  │ —      │ —      │ —       │ ✏    │   │ archived
│  └─┴──────────────────────┴────────┴────────┴─────────┴──────┘   │
└──────────────────────────────────────────────────────────────────┘
```

- **过滤 tab** 让你按状态查看：All / Success / Failed / Archived。
- **编辑任意行** 点铅笔图标。必填字段会在前端校验，不会出现"误改成空"的情况。
- **Retry failed** 把失败行重新跑一遍。API 偶尔抖动或者你刚改了模板后特别有用。
- **归档行** 鼠标悬停灰色徽章可看 LLM 给的归档原因。这些行不会被"Retry failed"重跑（模型已经说过没救了）。但你可以手动编辑促进它为 success。

### 导出

右上角两个大按钮：

- **CSV** —— 原始列 + 抽取列 + `_status` 列。带 UTF-8 BOM，Windows Excel 打开中文不乱码。
- **XLSX** —— 主 sheet 同上。如果有归档行，会额外多一个 `archived` sheet，列出每条归档行的源文本和归档原因。

CSV 输出示例（截断）：

```csv
id,name,experience,from,to,school,major,scholar,is_work_experience,_status
1,张伟,2018年9月-2022年6月 北京大学 计算机科学与技术 本科,2018-09,2022-06,北京大学,计算机科学与技术,Bachelor,false,success
2,Alice Johnson,"2015/09 - 2019/06, Stanford University, Computer Science, BSc",2015-09,2019-06,Stanford University,Computer Science,Bachelor,false,success
...
```

完整闭环就这五步：上传 → 选列 → 运行 → 审核 → 导出。原始 Excel 一字不动，清洗后的列追加在后面。

## FAQ

**我不会写代码能用吗？**
能。整个工作流就是 UI：上传、点击、编辑、下载。你只需要在最开始的安装阶段在终端跑一次 `docker compose up`。这条命令在 Mac / Windows / Linux 上完全一样。

**必须要 API key 吗？**
试用不需要。默认 demo 模式用内置启发式客户端，跑自带示例 CSV 就能看到完整 UI 流程。要在自己数据上看真实清洗效果，配一下 Anthropic key（见 [配置真实 AI](#配置真实-ai-anthropic)）。

**Anthropic key 在哪申请？**
<https://console.anthropic.com/settings/keys>。点 "Create Key"，复制（只显示一次），粘进 `.env`。

**花多少钱？**
Claude Sonnet 4.6 上大约 **$0.40 / 1000 行**。Haiku 4.5 便宜大约 10 倍。Opus 4.7 比 Sonnet 贵大约 3 倍。你只付 Anthropic 的钱 —— 工具本身免费开源。

**我的数据会被发到哪里？**
只发给 Anthropic（且只发你选的那一列；Excel 其它列留在本地）。Demo 模式（`MODEL_PROVIDER=mock`）下不会有任何数据离开你的机器。上传文件存在你本地 `storage/uploads`，SQLite 数据库在 `data/app.db`。没有任何 analytics / telemetry。

**为什么我的某行被丢到 Archived 桶了？**
LLM 看了一眼觉得这不是一条记录。常见触发：空单元格、`???` 或 `TBD` 这种占位、日志行、跟记录无关的句子（"今天天气真好"）。如果你不同意，点铅笔图标手动填字段 —— 行会被提升为 success。

**Mock 抽错了我的某行，是产品坏了吗？**
基本不是。Mock 只是个 regex + 关键词启发式，存在的唯一原因是让 demo 没有 key 也能跑。1000 行评测集上 Mock 整行准确率约 27%，真 Claude Sonnet 4.6 约 99%。如果 Mock 的结果看着奇怪，正常 —— 换 Anthropic 看真实结果。

**能用 OpenAI / DeepSeek / 本地模型吗？**
暂时不行 —— V1 只支持 Anthropic 和 Mock。`BaseLLMClient` 抽象就是为新增 provider 设计的，OpenAI 和 DeepSeek 在 V3 路线图。

**支持哪些文件类型？**
V1 是 `.xlsx` 和 `.csv`。`.docx`、`.pdf`、`.txt`、`.md` 在 V4 路线图。

**能自定义字段吗？**
V1 暂时不能在 UI 上自定义（内置模板是固定的）。如果你会改代码，可以编辑 `apps/api/app/services/builtin_templates.py` 加一个新内置模板再重启。完整 schema 构建器 UI 是 V2。

**PDF 呢？OCR 呢？**
V4 加文本型 PDF，V5 加扫描版 PDF 的 OCR。V1 都不支持。

**这个跟我自己写脚本比有啥优势？**
你自己写的话要处理：文件解析、prompt 工程、JSON 校验、重试逻辑、进度跟踪、结果审核、导出格式化、多 provider 抽象、归档路由、非技术用户用的 UI。这个工具把这些全给你做好了，本质就是你自己迟早要写的那种一次性脚本的产品化版本。

**能部署到云上吗？**
Docker 配置在哪都能跑。但带认证、多用户、持久化队列的生产部署 —— 那是 V6 路线图；当前设计就是单用户本地工具。

## 内置模板

**名称：** *Education Experience Cleaner* · **模式：** row-wise

| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| `from` | string | no | 起始日期 `YYYY-MM` / `YYYY` / null |
| `to` | string | no | 截止日期 `YYYY-MM` / `YYYY` / `present` / null |
| `school` | string | no | 学校或公司名称，原样保留 |
| `major` | string | no | 专业（教育）或职位（工作） |
| `scholar` | string | no | `Bachelor` / `Master` / `PhD` / null 之一 |
| `is_work_experience` | boolean | yes | true 表示工作记录 |

完整 prompt 在 `apps/api/app/services/builtin_templates.py`。里面有 8 条明确规则，覆盖 null 处理、日期归一、scholar 映射（BSc → Bachelor / 学士 → Bachelor 等）、school 原文保留、归档路由协议。

## 归档桶

有些输入本来就不是记录：空单元格、`???`、`TBD`、日志行、`lorem ipsum`、随机 emoji。强迫 LLM 给这种行造一个 `school` 或 `from`，下游数据反而被污染。

Prompt 里有一条 **Rule 0**：当输入不是记录时，模型返回

```json
{"_unprocessable": true, "reason": "<一句简短原因>"}
```

后端识别这个信号，把这一行存为 `status="archived"`。归档行：

- 在任务摘要里有独立计数；
- 在结果页有独立 tab；
- 导出时 XLSX 单独 sheet（或 CSV 中 `_status=archived` 行）；
- **不会**被"Retry failed"按钮重跑（模型已经说过没救了）；
- 用户如果不同意，可以手动编辑促进为 `success`。

离线 `MockLLMClient` 通过启发式规则实现（捕获约 91% 的明显垃圾）；真实 Anthropic 客户端通过 prompt Rule 0 路由。

## 评测

抽取器在一个合成的 1000 行数据集上做评测，数据集混合：

- 自然语言句子（中英文混合，教育和工作）
- 分隔符乱码型（`key:value`、斜杠分隔、方括号标签…）
- 表面脏格式（拼写错误、全大写、无空格、撇号年份 `'24`）
- 116 行归档 case（空白、乱码、日志行、无关文本…）

ground truth 由生成器的参数直接给出，标签 100% 可靠。重新生成：`python evaluation/generate_dataset.py --n 1000 --seed 42`。

### 结果

| Provider | 整行 | from | to | school | major | scholar | is_work | Archive |
|---|---|---|---|---|---|---|---|---|
| **MockLLMClient**（regex 基准） | 26.8% | 82.5% | 78.2% | 47.9% | 41.6% | 92.5% | 95.4% | 90.5% |
| **Anthropic Claude Sonnet 4.6** ¹ | ~99% | 100% | 100% | 100% | 100% | 100% | 100% | v3 数据集尚未跑 |

¹ Anthropic 是在更早的 1000 行数据集（无归档 case）上评测的。在余额耗尽前完成的 360 行中，整行准确率 357/360 ≈ **99.2%**。v3 数据集（含归档 case）由完全相同的生成器制造；prompt + extractor 端到端代码也完全相同。完整 runner 和原始结果见 [`evaluation/`](./evaluation/)。

### 自己跑

```bash
# 免费启发式基准：
python evaluation/run_eval.py --provider mock --dataset evaluation/eval_dataset_1000.json

# 真实模型（Sonnet 4.6 上 1000 行大约 $0.40）：
ANTHROPIC_API_KEY=sk-ant-... python evaluation/run_eval.py \
    --provider anthropic --dataset evaluation/eval_dataset_1000.json --concurrency 8
```

Runner 会输出每字段准确率、`is_work_experience` 混淆矩阵、归档路由准确率，以及配置数量的失败行 diff（`--show-failures 30`）。

## 项目背后的故事

这个项目的灵感来自我实习期间遇到的一个真实数据清洗问题。我手头有一份 Excel，里面好几千行自然语言形式的教育和工作经历：有的看上去像半结构化 JSON，有的是中文自由文本，有的是英文，还有的把多条记录揉在一行里。当时为了赶进度，我写了一个一次性的 Python 脚本，读一个硬编码的列，调用公司内部封装好的 AI 大模型接口，提取六个结构化字段，再把清洗结果写回 CSV。

脚本解决了眼前的业务问题，但所有东西都是硬编码的：文件路径、列名、字段集、prompt、重试逻辑。下一个实习生拿到不同列的 Excel，又得整个重写一遍。

**V1 版的 AI Data Extraction Studio 就是把这个脚本进一步产品化** —— 加了前端 UI、真实 LLM 后端、字段校验、失败自动重试、人工审核回路、独立的归档桶、干净的 CSV/XLSX 导出。

```
真实实习问题
        |
        v
一次性 Python Excel 清洗脚本
        |
        v
V1 全栈 AI 抽取 MVP   <-- 当前仓库
        |
        v
完整的 AI 非结构化数据抽取平台   (Roadmap V2-V6)
```

更长的故事在 [`docs/background.md`](./docs/background.md)。

### 设计原则

- **不留半成品。** V1 故意只把一个用例（行级 Excel/CSV + 一个内置模板）做透。自定义 schema、文档级抽取、OCR、认证、队列 —— 全部明确放到编号的路线图里，绝不假装已完成。
- **Mock 是 fallback，不是 feature。** 启发式 Mock 存在的唯一原因是让你不带 key 也能跑 demo。要真实抽取效果就得用真模型 —— README 说得很坦白。
- **测，不要靠感觉。** `evaluation/` 里有一个带合成 ground truth 的 1000 行评测脚手架。README 里的准确率数字来自这个脚手架，不是 PPT。
- **架构胜过抛光。** `BaseLLMClient` 已经同时托管 Mock 和 Anthropic。新增 OpenAI 只需要写一个 subclass。前端用一个统一 HTTP 封装。DB schema 留好了 V2 自定义模板的空间，不需要 migration。

## V1 范围

V1 故意把**一个用例**端到端做透；其它能力都在路线图上。

| 能力 | V1 | 备注 |
|---|:---:|---|
| 上传 `.xlsx` / `.csv` | yes | 流式；上限 25 MB |
| 表头 + 首 20 行预览 | yes | |
| 行级抽取（一行 → 一条记录） | yes | 文档级 V4 |
| 真实 LLM：Anthropic Claude Sonnet 4.6 | yes | 可切换 Haiku / Opus |
| 启发式 `MockLLMClient` fallback | yes | 不需要 key 就能 demo |
| Pydantic schema 校验 + 失败重试 | yes | |
| `archived` 桶（LLM 判定不可处理） | yes | 独立计数、tab、导出 sheet |
| 后台 job runner + 实时进度 | yes | 线程；SQLite 持久化 |
| 行内编辑 + 失败重跑 | yes | 编辑会把 archived/failed → success |
| 导出 CSV / XLSX，带 `_status` 列 | yes | |
| 中英双语文档 | yes | |
| Docker / docker-compose | yes | 一行命令启动 |
| 后端测试（pytest） | yes | 26 个测试覆盖 parser、validator、mock、runner、archive、export |
| 自定义 schema 构建器 UI | no | V2 |
| 其它 LLM 提供方（OpenAI、DeepSeek…） | no | V3 |
| `.docx` / `.pdf` / `.txt` / `.md` 支持 | no | V4 |
| 扫描版 PDF OCR | no | V5 |
| 用户认证 / 团队 / 云端部署 | no | V6 |

## 技术栈

| 层 | 工具 |
|---|---|
| 后端 | Python 3.11+、FastAPI、SQLAlchemy 2、Pydantic 2、SQLite、pandas、openpyxl |
| LLM | Anthropic Claude（默认 Sonnet 4.6）、内置启发式 Mock |
| 前端 | Next.js 14 App Router、TypeScript strict、Tailwind CSS、TanStack Table、SWR、react-hook-form + zod |
| 工程 | pytest、ESLint、Docker + docker-compose |

## 项目结构

```
ai-data-extraction-studio/
├── apps/
│   ├── api/                              # FastAPI 后端
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── db.py
│   │   │   ├── models/                   # SQLAlchemy ORM
│   │   │   ├── schemas/                  # Pydantic DTO
│   │   │   ├── routers/                  # FastAPI 接口
│   │   │   ├── services/                 # 抽取核心
│   │   │   │   ├── excel_parser.py
│   │   │   │   ├── prompt_builder.py
│   │   │   │   ├── llm_client.py         # MockLLMClient + AnthropicClient + ABC
│   │   │   │   ├── validator.py
│   │   │   │   ├── extractor.py          # 重试循环 + 归档信号
│   │   │   │   ├── job_runner.py         # 后台线程 runner
│   │   │   │   ├── exporter.py
│   │   │   │   └── builtin_templates.py
│   │   │   └── utils/
│   │   ├── tests/                        # 26 个 pytest 测试
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web/                              # Next.js 14 前端
│       ├── app/                          # / /upload /run /jobs /results 页面
│       ├── components/
│       ├── lib/api.ts                    # 单一 HTTP 封装
│       ├── types/api.ts
│       └── Dockerfile
│
├── evaluation/                            # 评测脚手架 + 1000 行数据集
│   ├── generate_dataset.py
│   ├── run_eval.py
│   └── eval_dataset_1000.json
├── docs/                                  # background.md, architecture.md
├── examples/                              # 示例 CSV / XLSX
├── storage/{uploads,exports}              # 运行时文件存储
├── data/                                  # SQLite 数据库
├── docker-compose.yml
├── .env.example
└── README.md / README.zh-CN.md
```

## API 概览

所有接口前缀 `/api`。交互文档在 <http://localhost:8000/docs>。

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/api/health` | 健康检查 + 当前 provider/model |
| `POST` | `/api/files/upload` | 上传 `.xlsx` / `.csv`，返回 `{file_id, headers, preview_rows, total_rows}` |
| `GET` | `/api/templates` | 列出所有模板（built-in 标记） |
| `GET` | `/api/templates/{id}` | 模板详情 |
| `POST` | `/api/jobs` | 创建并启动任务 |
| `GET` | `/api/jobs/{id}` | 任务状态 + 计数（含 `archived_count`） |
| `POST` | `/api/jobs/{id}/retry-failed` | 重跑失败行 |
| `GET` | `/api/jobs/{id}/results?status=all\|success\|failed\|archived` | 分页结果 |
| `PATCH` | `/api/results/{id}` | 手动编辑；将 archived/failed 提升为 success |
| `GET` | `/api/jobs/{id}/export?format=csv\|xlsx` | 下载合并文件 |

## 测试

```bash
cd apps/api
pytest -v
```

覆盖范围：

- Excel / CSV 解析
- Prompt builder 输出形状
- Pydantic validator（必填、类型错误、枚举边界、code fence 去除）
- MockLLMClient 行为确定性 + provider 工厂拒绝逻辑
- Anthropic 客户端 API key 守卫
- 端到端 job runner
- CSV / XLSX 导出（含 archived sheet）
- 归档路由路径（LLM 信号、Mock 启发式、重跑排除、手动编辑提升）

共 26 个测试。前端：`npm run lint`、`npx tsc --noEmit`、`npm run build`。

## Roadmap

每一项都是 **规划中**，不会假装已实现。

| 版本 | 主题 | 计划内容 |
|---|---|---|
| **V2** | 自定义 schema | 用户自定义字段 / prompt / 示例；可复用模板；JSON 导入导出；模板市场 |
| **V3** | 更多 LLM 提供方 | OpenAI、DeepSeek、私有化部署等 `BaseLLMClient` subclass；按 job 的成本 & token 统计；多 provider 自动 fallback |
| **V4** | 更多文件类型 | `.docx`、`.txt`、`.md`、文本型 `.pdf`；文档级抽取（一份文档 → 多条记录） |
| **V5** | OCR 与长文档 | 扫描版 PDF OCR；更强分块；长文档多记录提取 |
| **V6** | 生产部署 | 用户认证、团队工作区、PostgreSQL、S3 / 云存储、Celery/Redis 队列、部署模板 |

## 已知局限

- V1 只接 `.xlsx` 和 `.csv`（DOCX/PDF/TXT/MD 暂不支持）。
- 只支持行级抽取。文档级（一个 PDF → 多条记录）见 V4。
- 只有一个内置模板，没有自定义 schema UI。
- 真实 LLM 模式 V1 只支持 Anthropic；OpenAI / DeepSeek / 私有化在 V3。
- `MockLLMClient` 基于启发式规则，不能替代真实模型。仅作离线 demo 和 CI 使用，正式抽取请配 Anthropic。
- 任务队列在进程内（线程），API 重启会丢失正在进行的任务。Celery / Redis 持久化队列在 V6。
- 没有用户认证，目前是单用户本地工具。
- 没有 OCR — 扫描版 PDF 不支持。

## 故障排查

**`Address already in use`（端口 8000 / 3000 被占）。** 别的进程占了端口。换一个：`uvicorn app.main:app --port 8001` / `npm run dev -- -p 3001`。如果改了后端端口，记得同步改 `.env` 里的 `NEXT_PUBLIC_API_BASE`。

**`ModuleNotFoundError: No module named 'app'`。** 在 `apps/api/` 目录里运行 `uvicorn app.main:app`，不要在仓库根目录运行。

**前端到处 "Failed to fetch"。** 前端连不上后端。检查 (1) 后端是否跑在 `NEXT_PUBLIC_API_BASE` 指定地址，(2) `BACKEND_CORS_ORIGINS` 包含前端 URL。

**`sqlite3.OperationalError: unable to open database file`。** `data/` 目录不存在或不可写。`mkdir -p data`。

**`npm install` 失败。** Next.js 14 最低 Node 18.17，推荐 Node 20+。`nvm install 20 && nvm use 20`。

**`ANTHROPIC_API_KEY is not set`。** 你设了 `MODEL_PROVIDER=anthropic` 但 `ANTHROPIC_API_KEY` 留空。要么填 key，要么改回 `MODEL_PROVIDER=mock`。

**`docker compose up` 卡在 "downloading"。** 首次构建要拉好几 GB 的基础镜像，耐心等。之后启动几秒就好。

**Anthropic 返回 `Your credit balance is too low`。** 账号没钱了。到 <https://console.anthropic.com/settings/billing> 充值。

## 参与贡献

欢迎 PR。详见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。推荐的入门贡献方向：

- 新增一个内置模板（纯工作经历、简历解析、论文元数据 …）。
- 实现一个新的 `BaseLLMClient` subclass（OpenAI、DeepSeek、vLLM …）作为 V3 路线图起点。
- 完善 `MockLLMClient` 对边界输入的处理。
- 给 `evaluation/generate_dataset.py` 加更多评测类别。

## 许可证

[MIT](./LICENSE)

## 致谢

实习中遇到的真实问题，是项目最初的来源。以及背后所有开源生态：[FastAPI][fastapi-url]、[Next.js][nextjs-url]、[SQLAlchemy][sqlalchemy-url]、[Pydantic][pydantic-url]、[Tailwind CSS][tailwind-url]、[TanStack Table][tanstack-url]。

---

[status-shield]: https://img.shields.io/badge/Status-V1%20MVP-orange
[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
[license-url]: ./LICENSE
[prs-shield]: https://img.shields.io/badge/PRs-welcome-brightgreen

[python-shield]: https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white
[python-url]: https://www.python.org/
[fastapi-shield]: https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white
[fastapi-url]: https://fastapi.tiangolo.com/
[pydantic-shield]: https://img.shields.io/badge/Pydantic-2-E92063?logo=pydantic&logoColor=white
[pydantic-url]: https://docs.pydantic.dev/
[sqlalchemy-shield]: https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white
[sqlalchemy-url]: https://www.sqlalchemy.org/
[sqlite-shield]: https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white
[sqlite-url]: https://sqlite.org/
[nextjs-shield]: https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs&logoColor=white
[nextjs-url]: https://nextjs.org/
[typescript-shield]: https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white
[typescript-url]: https://www.typescriptlang.org/
[tailwind-shield]: https://img.shields.io/badge/Tailwind%20CSS-3-06B6D4?logo=tailwindcss&logoColor=white
[tailwind-url]: https://tailwindcss.com/
[anthropic-shield]: https://img.shields.io/badge/Anthropic-Claude%20Sonnet%204.6-D77757?logo=anthropic&logoColor=white
[anthropic-url]: https://www.anthropic.com/
[docker-shield]: https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white
[docker-url]: https://www.docker.com/
[tanstack-url]: https://tanstack.com/table
