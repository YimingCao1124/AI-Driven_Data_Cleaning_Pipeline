<div align="center">

# AI Data Extraction Studio

**一个基于字段 Schema 的 AI 数据清洗与结构化抽取平台。**

*把表格里那些乱七八糟的自然语言文本，自动整理成干净、结构化的数据表。*

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-V1%20MVP-orange)
![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen)

[English](./README.md) · [简体中文](./README.zh-CN.md)

</div>

---

## 📸 截图

> 截图将在首次手动 Demo 之后补上。下面的 [使用说明](#-使用说明手把手) 中详细描述了每个页面应该是什么样子。

```
┌────────────────────────────────────────────────────────┐
│  [首页]   →  [上传]   →   [运行]   →   [结果]         │
│                                                        │
│   产品介绍    拖入 CSV    选列&运行    编辑/导出       │
└────────────────────────────────────────────────────────┘
```

---

## 📖 项目背景

> 这个项目的灵感来自我实习期间遇到的真实数据清洗问题。
>
> 最初我写了一个 Python 脚本，用来读取 Excel 表格中某一列复杂的自然语言教育经历/工作经历文本，并调用公司 DataOps Git 仓库中封装好的大模型接口，从文本中提取起始日期、结束日期、学校、专业、学历、是否为工作经历等字段，最后把结果追加到原始表格后导出 CSV。
>
> 这个脚本解决了当时的业务问题，但它本质上仍然是一个一次性的 pipeline：输入列、输出字段、prompt、校验规则和文件路径都是硬编码的。
>
> **V1 版本的 AI Data Extraction Studio** 就是把这个一次性的脚本产品化成一个可以本地运行的全栈 AI Excel 数据抽取 MVP，包含前端界面、后端 API、Mock AI 抽取、字段校验、结果预览、人工修改和导出功能。

整个项目的演进路径是有意分阶段的：

```
真实实习问题
        ↓
一次性 Python Excel 清洗脚本
        ↓
V1 全栈 AI Excel 抽取 MVP        ← 当前仓库
        ↓
完整的 AI 非结构化数据抽取平台 (Roadmap V2–V6)
```

更详细的故事见 [`docs/background.md`](./docs/background.md)。

---

## 🎯 V1 范围

V1 故意只把**一个用例**做透：原始的实习数据清洗工作流。其它功能都在 Roadmap 中，且明确标注未实现。

| 功能 | V1 | 备注 |
|---|:--:|---|
| 上传 `.xlsx` / `.csv` | ✅ | |
| 表头 + 20 行预览 | ✅ | |
| 行级抽取（一行 → 一条记录） | ✅ | |
| 内置模板：教育经历清洗 | ✅ | 字段：`from`、`to`、`school`、`major`、`scholar`、`is_work_experience` |
| MockLLMClient（无需 API key） | ✅ | |
| Pydantic 字段校验 + 失败自动重试 | ✅ | |
| 任务进度实时展示 | ✅ | 后台线程 + SQLite |
| 结果预览 + 行内编辑 | ✅ | |
| 失败行重跑 | ✅ | |
| 导出 CSV / XLSX，原始列 + 抽取列拼接 | ✅ | |
| 中英文双语文档 | ✅ | |
| Docker / docker-compose | ✅ | |
| 后端测试 | ✅ | |
| 自定义 schema 构建器 | ❌ | V2 |
| 真实 LLM 提供方（OpenAI、Anthropic…） | ❌ | V3 |
| `.docx` / `.pdf` / `.txt` / `.md` 支持 | ❌ | V4 |
| 文档级抽取（一份文档 → 多条记录） | ❌ | V4 |
| 扫描版 PDF OCR | ❌ | V5 |
| 用户认证 / 团队 / 云端 | ❌ | V6 |

---

## ✨ V1 特性

- **🪶 零配置 Demo** — clone、安装、运行。MockLLMClient 不依赖任何外部 API key，也能跑出真实的抽取结果。
- **🧩 Schema 驱动校验** — 每条抽取结果都会通过一个根据模板字段定义动态构建的 Pydantic 模型校验。
- **🔁 失败自动重试** — 当模型返回非法 JSON 或字段校验失败时，抽取器会把错误信息嵌进下一轮 prompt 中，让模型修正。
- **🖊️ 人工审核闭环** — 每一条结果都可以看到原始输入文本和 AI 抽取的字段，可以单行编辑，也可以批量重跑失败行。
- **📦 干净的导出** — 原始列保留不动，AI 抽取的列追加到表后，与原实习脚本的输出格式一致。
- **🧱 清晰的抽象** — `BaseLLMClient` 已经准备好接入真实模型提供方（V3），不需要改动其它任何代码。

---

## 🛠️ 技术栈

**后端**

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x + SQLite
- Pydantic 2
- pandas、openpyxl
- pytest

**前端**

- Next.js 14 (App Router)
- TypeScript (strict)
- Tailwind CSS
- shadcn/ui
- TanStack Table
- SWR（轮询）
- react-hook-form + zod

**工程**

- Docker + docker-compose
- MIT License

---

## 📂 项目结构

```
ai-data-extraction-studio/
├── apps/
│   ├── api/                              # FastAPI 后端
│   │   ├── app/
│   │   │   ├── main.py                   # 入口
│   │   │   ├── config.py                 # 基于环境变量的配置
│   │   │   ├── db.py                     # SQLAlchemy 会话
│   │   │   ├── models/                   # 数据库模型
│   │   │   ├── schemas/                  # Pydantic DTO
│   │   │   ├── routers/                  # API 路由
│   │   │   ├── services/                 # 抽取核心
│   │   │   │   ├── excel_parser.py
│   │   │   │   ├── prompt_builder.py
│   │   │   │   ├── llm_client.py         # MockLLMClient + ABC
│   │   │   │   ├── validator.py
│   │   │   │   ├── extractor.py
│   │   │   │   ├── job_runner.py
│   │   │   │   ├── exporter.py
│   │   │   │   └── builtin_templates.py
│   │   │   └── utils/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web/                              # Next.js 前端
│       ├── app/
│       │   ├── page.tsx                  # 首页
│       │   ├── upload/page.tsx
│       │   ├── run/page.tsx
│       │   ├── jobs/[jobId]/page.tsx
│       │   └── results/[jobId]/page.tsx
│       ├── components/
│       ├── lib/api.ts                    # 所有 HTTP 调用
│       ├── types/api.ts
│       └── Dockerfile
│
├── docs/                                  # 架构 + 项目背景
├── examples/                              # 示例 CSV / XLSX
├── scripts/                               # 辅助脚本
├── storage/{uploads,exports}              # 运行时文件存储
├── data/                                  # SQLite 数据库
├── .env.example
├── docker-compose.yml
├── README.md
└── README.zh-CN.md                        # ← 当前文件
```

---

## ⚡ 快速开始

可以选择**本地运行**（两个终端）或者 **Docker 一键启动**。两条路径产出的 Demo 是一样的。

> **前置条件：** Python 3.11+、Node.js 20+，以及 npm 或 pnpm。Docker 模式还需要 Docker Desktop 或 Docker Engine + Compose V2。

### 方案 A — 本地开发

#### 1. Clone 仓库并准备环境变量文件

```bash
git clone https://github.com/<your-username>/AI-Driven_Data_Cleaning_Pipeline.git
cd AI-Driven_Data_Cleaning_Pipeline
cp .env.example .env
```

`.env` 不需要修改，默认值就能配合 Mock LLM 跑通整个 Demo。

#### 2. 启动后端（终端 1）

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

你应该看到：

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

打开 <http://localhost:8000/docs> 就能看到交互式 API 文档。

#### 3. 启动前端（终端 2）

```bash
cd apps/web
npm install
npm run dev
```

你应该看到：

```
✓ Ready in 1.4s
- Local:    http://localhost:3000
```

#### 4. 打开应用

浏览器访问 <http://localhost:3000>。

### 方案 B — Docker

```bash
docker compose up --build
```

启动完成后访问：

- 前端：<http://localhost:3000>
- 后端 API：<http://localhost:8000>
- API 文档：<http://localhost:8000/docs>

---

## 🧑‍🏫 使用说明（手把手）

这一节带你从安装完成 → 导出干净 CSV，**用时大约 3 分钟**，使用仓库里自带的示例文件。

### 第 0 步 — 启动应用

任选上文方案 A 或方案 B，确认后端跑在 `:8000`、前端跑在 `:3000`。

### 第 1 步 — 打开首页

浏览器访问 <http://localhost:3000>。会看到 AI Data Extraction Studio 的产品页和一个 **"Start Extraction"** 按钮。

> ✅ **页面上应该看到：** 项目标题、副标题、V1 工作流条 (`上传 → 选列 → 运行 → 审核 → 导出`)，以及绿色的 "Start Extraction" 按钮。

点击 **Start Extraction**。

### 第 2 步 — 上传示例文件

进入 `/upload` 页面。

1. 点击 **"Choose file"**（或者拖拽文件），选择仓库中的 `examples/education_experience_sample.csv`。
2. 页面会自动上传文件，并在下方显示 **10 行 × 3 列** (`id`、`name`、`experience`) 的预览。

> ✅ **页面上应该看到：** 预览表格里 `experience` 列包含 `2018年9月-2022年6月 北京大学 计算机科学与技术 本科`、`{"from":"2019","to":"2023","school":"MIT","major":"EE","degree":"MS"}` 这类乱七八糟的文本。预览下方出现 "Continue →" 按钮。

点击 **Continue**。

### 第 3 步 — 配置抽取参数

进入 `/run` 页面。

1. **Input column** 下拉框 → 选 `experience`。
2. **Template** 下拉框 → 默认应该已经选好 *Education Experience Cleaner*（V1 唯一内置模板）。
3. **Max rows** 输入框 → 保留默认 `100`，或者改成 `10` 只跑示例的 10 行。
4. 点击 **Run Extraction**。

> 💡 **小提示：** 模板卡片里会展示具体抽取哪些字段：`from`、`to`、`school`、`major`、`scholar`、`is_work_experience`。

### 第 4 步 — 观察任务运行

页面跳转到 `/jobs/<jobId>`，前端每 2 秒轮询一次后端。

> ✅ **页面上应该看到：**
> - 进度条从 0% 走到 100%。
> - 四个状态计数卡片：**Total / Processed / Success / Failed**。
> - 对示例 CSV 来说，预期大约 **9 条成功 / 0–1 条失败**（Mock LLM 故意会让某一条歧义行失败，方便你看到失败重跑流程）。
> - 状态变为 `completed` 时，自动跳转到 `/results/<jobId>`。

### 第 5 步 — 审核抽取结果

进入 `/results/<jobId>` 页面。

- 表格按行展示，每行包含原始 `input_text` 与抽取出的 `from`、`to`、`school`、`major`、`scholar`、`is_work_experience` 等字段。
- 顶部 **All / Success / Failed** 标签可以筛选。
- 点击任意行的 **Edit** 图标，会弹出编辑对话框，可以修改任何字段，保存即同步到数据库。
- 点击 **Retry failed** 可以把所有失败行重新跑一遍。

> 💡 **小提示：** 失败行显示红色徽章，鼠标悬停可以看到具体的校验错误信息。

### 第 6 步 — 导出结果

页面右上角：

- 点击 **Export CSV**，下载 CSV 文件，其中包含原始列 (`id`、`name`、`experience`) + 六个 AI 抽取列。
- 点击 **Export XLSX**，下载 Excel 版本。

> ✅ **导出的 CSV 预览：**
>
> ```csv
> id,name,experience,from,to,school,major,scholar,is_work_experience
> 1,张伟,2018年9月-2022年6月 北京大学 计算机科学与技术 本科,2018-09,2022-06,北京大学,计算机科学与技术,Bachelor,false
> 2,Alice Johnson,"2015/09 - 2019/06, Stanford University, …",2015-09,2019-06,Stanford University,Computer Science,Bachelor,false
> ...
> ```

### 🎉 完成

这就是原始实习脚本的工作流，被完整产品化之后的样子 —— 在本地笔记本上就能跑，不需要任何外部依赖、不需要任何 API key。

---

## 🌱 环境变量

| 变量 | 默认值 | 用途 |
|---|---|---|
| `MODEL_PROVIDER` | `mock` | V1 只支持 `mock` |
| `MODEL_NAME` | `mock-extractor` | 仅展示用，会出现在 `/api/health` 返回中 |
| `MAX_RETRIES` | `2` | 单行校验失败后的最大重试次数 |
| `TEMPERATURE` | `0` | 为 V3 真实模型预留 |
| `MAX_CONCURRENCY` | `3` | 单任务并发线程数 |
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLAlchemy 数据库 URL |
| `UPLOAD_DIR` | `./storage/uploads` | 上传文件落盘位置 |
| `EXPORT_DIR` | `./storage/exports` | 导出文件位置 |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000` | 允许的 CORS 来源（逗号分隔） |
| `NEXT_PUBLIC_API_BASE` | `http://localhost:8000` | 前端访问后端的地址 |
| `OPENAI_API_KEY` | _(空)_ | V3 预留 |
| `ANTHROPIC_API_KEY` | _(空)_ | V3 预留 |

---

## 🔌 内置模板（V1）

**名称：** *Education Experience Cleaner*
**模式：** row-wise

| 字段 | 类型 | 必填 | 说明 |
|---|---|:--:|---|
| `from` | string | ❌ | 起始日期（如 `2018-09` 或 `2018`） |
| `to` | string | ❌ | 截止日期或 `present` |
| `school` | string | ❌ | 学校或公司名称 |
| `major` | string | ❌ | 专业（教育经历）或职位（工作经历） |
| `scholar` | string | ❌ | 学历（`Bachelor`、`Master`、`PhD`） |
| `is_work_experience` | boolean | ✅ | `true` 表示这是一段工作经历 |

模板的指令文本与示例会在首次启动时写入数据库，可通过 `GET /api/templates` 获取。

---

## 🌐 API 概览

所有接口都在 `/api` 前缀下。完整交互文档：<http://localhost:8000/docs>。

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/api/health` | 健康检查 + 当前 LLM 提供方 |
| `POST` | `/api/files/upload` | 上传 `.xlsx` / `.csv`，返回 `{file_id, headers, preview_rows, total_rows}` |
| `GET` | `/api/templates` | 列出所有模板 |
| `GET` | `/api/templates/{id}` | 模板详情 |
| `POST` | `/api/jobs` | 创建并启动抽取任务 |
| `GET` | `/api/jobs/{id}` | 任务状态 + 进度计数 |
| `POST` | `/api/jobs/{id}/retry-failed` | 重新跑失败行 |
| `GET` | `/api/jobs/{id}/results` | 分页结果（可按状态过滤） |
| `PATCH` | `/api/results/{id}` | 手动修改单行结果 |
| `GET` | `/api/jobs/{id}/export?format=csv\|xlsx` | 下载合并后的文件 |

---

## 🧪 测试

```bash
cd apps/api
pytest -v
```

覆盖：

- Excel / CSV 解析
- Prompt builder 产出形状
- Pydantic validator（必填、类型错误、枚举边界）
- MockLLMClient 行为确定性
- 端到端 job runner
- CSV / XLSX 导出

---

## 🗺️ Roadmap

每一项都是 **规划中**，不假装已完成。

| 版本 | 主题 | 计划功能 |
|---|---|---|
| **V2** | 自定义 schema | 用户自定义字段、prompt、示例；可复用模板；模板导入导出 |
| **V3** | 真实 LLM 提供方 | OpenAI、Anthropic、DeepSeek 等基于 `BaseLLMClient` 的实现；成本估算；更智能的失败重试 |
| **V4** | 更多文件类型 | `.docx`、`.txt`、`.md`、文本型 `.pdf`；文档级抽取（一份文档 → 多条记录） |
| **V5** | OCR 与长文档 | 扫描版 PDF OCR；更强的分块策略；长文档中多记录提取 |
| **V6** | 生产部署 | 用户认证、团队工作空间、PostgreSQL、S3 / 云存储、Celery/Redis 队列、部署模板 |

---

## ⚠️ 已知局限

- V1 只接受 `.xlsx` 和 `.csv`（DOCX/PDF/TXT/MD 暂不支持）。
- V1 只支持行级抽取，不支持文档级抽取。
- 只有一个内置模板（*Education Experience Cleaner*），暂无自定义 schema 构建器。
- 唯一可用的 LLM 客户端是 `MockLLMClient`，基于启发式规则，**不是真实模型**。真实模型见 V3。
- 任务队列在进程内（API 容器内的线程）。API 重启会导致任务丢失，队列持久化见 V6。
- 没有用户认证，目前仅作为单用户本地工具。
- 暂无 OCR 能力，扫描版 PDF 不支持。
- README 中的截图为占位，需要手动截图补上。

---

## 🩹 故障排查

**`Address already in use`（端口 8000 或 3000 被占用）**
其它进程占了端口。要么关掉那个进程，要么换端口：`uvicorn app.main:app --port 8001` / `npm run dev -- -p 3001`。如果改了后端端口，记得同时改 `.env` 里的 `NEXT_PUBLIC_API_BASE`。

**`ModuleNotFoundError: No module named 'app'`**
确认你是在 `apps/api/` 目录下运行 `uvicorn app.main:app`，而不是仓库根目录。

**前端每个页面都出现 "Failed to fetch"**
前端访问不到后端。检查：
1. 后端是否跑在 `NEXT_PUBLIC_API_BASE` 指定的地址。
2. 后端的 `BACKEND_CORS_ORIGINS` 是否包含前端的地址。

**`sqlite3.OperationalError: unable to open database file`**
`data/` 目录不存在或不可写。手动创建：`mkdir -p data`。

**`npm install` 在 Node 18 下报错**
Next.js 14 最低支持 Node 18.17，推荐 Node 20+。建议升级：`nvm install 20 && nvm use 20`。

---

## 🤝 参与贡献

欢迎 PR。请参考 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

特别推荐的入门贡献方向：

- 新增一个内置模板（工作经历清洗、简历解析等）。
- 实现 V3 路线图中的真实 LLM 客户端。
- 完善 MockLLMClient 对边界输入的处理。
- 写更多测试。

---

## 📜 许可证

[MIT](./LICENSE) © 2026 AI Data Extraction Studio contributors.

---

## 🙏 致谢

- 实习中遇到的真实问题，是这个项目最初的来源。
- FastAPI、Next.js、SQLAlchemy、Pydantic、Tailwind CSS、shadcn/ui、TanStack 等开源项目，没有它们就没有这个仓库。
