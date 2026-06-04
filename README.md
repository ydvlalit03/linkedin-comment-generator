<div align="center">

# 💬 LinkedIn Comment Generator

### Write human-sounding LinkedIn comments in *your* voice — a full-stack RAG app

![Next.js](https://img.shields.io/badge/Next.js_16-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-fast_LLM-F55036?style=flat-square&logo=groq&logoColor=white)
![Drizzle](https://img.shields.io/badge/Drizzle_ORM-C5F74F?style=flat-square&logo=drizzle&logoColor=black)
![Tailwind](https://img.shields.io/badge/Tailwind_v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)

</div>

---

## 📖 Overview

Generic AI comment tools all sound the same — robotic, over-eager, instantly recognizable as machine-written. **LinkedIn Comment Generator** solves that by learning *your* style. It embeds your past comments into a retrieval store and uses them as live style references, so every generated comment sounds like *you* — not like ChatGPT.

Paste a LinkedIn post URL (or upload a CSV of posts). The app scrapes and analyzes the post, retrieves your most relevant past comments via a **RAG pipeline**, generates several comment options across different *angles*, and runs each through a **humanizer** that strips out tell-tale "AI clichés." It's a full-stack Next.js app with fast **Groq** inference and a local **Drizzle/SQLite** database.

---

## 📑 Table of Contents

- [How it works](#-how-it-works)
- [Features](#-features)
- [Tech stack](#-tech-stack)
- [The service layer](#-the-service-layer)
- [Installation](#-installation)
- [Environment variables](#-environment-variables)
- [Project structure](#-project-structure)
- [Disclaimer](#-disclaimer)

---

## 🔄 How it works

```
Post URL / CSV
      │
      ▼
 Post Analyzer ──▶ RAG Service ──▶ Dynamic Prompt Engine ──▶ Groq LLM ──▶ Humanizer ──▶ Comment options
 (scrape +        (retrieve your   (assemble a style-aware                 (remove AI
  classify)        past comments)   prompt)                                 clichés)
```

The RAG step is what makes the output sound like you: instead of a generic system prompt, the model is grounded in real examples of how *you* actually comment, retrieved by semantic similarity to the current post.

---

## ✨ Features

- **🧠 RAG over your own comments** — embeds your comment history and retrieves the closest matches as style anchors for every new comment
- **🔎 Post analysis** — scrapes and classifies the target post's topic, tone and post-type before generating
- **🎭 Multiple comment angles** — generates several distinct options (agreement, question, insight, story, …) so you can pick the best
- **🪄 Humanizer** — post-processes output against a curated AI-cliché list so comments read naturally
- **⚡ Groq-powered inference** — very low-latency LLM responses
- **📥 CSV bulk upload** — process many post URLs at once
- **📊 Dashboard & analytics** — manage posts, review generated comments, and track usage over time
- **⚙️ Settings** — configure your profile, API key and generation preferences

---

## 🛠️ Tech stack

| Layer | Technology |
|-------|------------|
| **Framework** | Next.js 16 (App Router) + React 19 |
| **Language** | TypeScript |
| **Styling** | Tailwind CSS v4, lucide-react, sonner (toasts) |
| **LLM** | Groq SDK (fast inference) |
| **Database** | Drizzle ORM + better-sqlite3 (local SQLite) |
| **Retrieval** | custom RAG service over embedded comment history |
| **Backend (optional)** | a supplementary FastAPI scraping service in `backend/` |

---

## 🧱 The service layer

The core logic lives in `src/lib/services/`:

| Service | Responsibility |
|---------|----------------|
| `linkedin-scraper.ts` | fetch the post content from a URL |
| `post-analyzer.ts` | classify post type, topic and tone |
| `rag-service.ts` | retrieve relevant past comments from the store |
| `dynamic-prompt-engine.ts` | assemble a style-aware generation prompt |
| `comment-generator.ts` + `groq-client.ts` | generate options via Groq |
| `humanizer.ts` | remove AI clichés and de-robotify output |
| `csv-parser.ts` | parse bulk-upload CSVs |
| `web-search.ts` | optional enrichment |

Reference data lives in `src/lib/data/`: `comment-angles.ts`, `post-types.ts`, and the `ai-cliches.ts` list the humanizer screens against.

---

## 📦 Installation

### Prerequisites
- Node.js 18+
- A **Groq API key** ([console.groq.com](https://console.groq.com))

```bash
npm install
cp .env.example .env.local       # add GROQ_API_KEY
npx drizzle-kit push             # create the local SQLite schema via Drizzle
npm run dev                      # http://localhost:3000
```

### Run with Docker

```bash
docker-compose up --build
```

---

## 🔐 Environment variables

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Groq LLM access for generation |
| (see `.env.example`) | any additional scraping / config keys |

---

## 🗂️ Project structure

```
src/
├── app/                 # App Router pages: dashboard, analytics, settings, post/[postId]
├── components/          # UI: upload (csv-uploader, url-list-preview),
│                        #   post (post-card, post-media), comments (comment-card), shared
└── lib/
    ├── services/        # scraper, analyzer, RAG, prompt engine, Groq client, humanizer, csv
    ├── db/              # Drizzle schema & client
    ├── data/            # comment angles, post types, AI-cliché list
    ├── types/           # shared TypeScript types
    └── utils/           # logger, json parser, linkedin-url helpers
backend/                 # optional FastAPI scraping service
docs/                    # technical document + user guide (LaTeX)
```

---

## ⚠️ Disclaimer

For **educational and personal-productivity** use. Always respect LinkedIn's Terms of Service and applicable data-privacy laws when fetching and processing post data.
