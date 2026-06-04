# 💬 LinkedIn Comment Generator

> Generate **personalized, human-sounding LinkedIn comments in your own voice** — a full-stack Next.js app that learns your style from your past comments and uses a RAG pipeline + fast Groq LLM inference to write replies that don't sound like AI.

Paste a LinkedIn post URL (or upload a CSV of posts), and the app analyzes the post, retrieves your relevant past comments as style references, generates on-brand comment options across different angles, and runs them through a humanizer to strip out tell-tale "AI clichés."

---

## ✨ Features

- **🧠 RAG over your own comments** — embeds your comment history into a local vector store and retrieves the closest matches as style anchors for every new comment.
- **🔎 Post analysis** — scrapes and analyzes the target LinkedIn post to understand topic, tone and post type before generating.
- **🎭 Multiple comment angles** — generates several comment options across different angles (agreement, question, insight, story, etc.).
- **🪄 Humanizer** — post-processes output against a curated list of AI clichés so comments read naturally.
- **⚡ Groq-powered inference** — uses the Groq SDK for very low-latency LLM responses.
- **📥 CSV bulk upload** — process many post URLs at once.
- **📊 Dashboard & analytics** — manage posts, review generated comments, and track usage.
- **⚙️ Settings** — configure your profile, API key and generation preferences.

---

## 🛠️ Tech Stack

| Layer        | Tech                                                        |
|--------------|-------------------------------------------------------------|
| Framework    | Next.js 16 (App Router) + React 19                          |
| Language     | TypeScript                                                  |
| Styling      | Tailwind CSS v4, lucide-react, sonner (toasts)              |
| LLM          | Groq SDK (fast inference)                                   |
| Database     | Drizzle ORM + better-sqlite3 (local SQLite)                 |
| Retrieval    | Custom RAG service over embedded comment history            |
| Backend (opt)| Supplementary FastAPI service in `backend/` for scraping     |

---

## 🏗️ How It Works

```
Post URL / CSV ─▶ Post Analyzer ─▶ RAG Service ─▶ Dynamic Prompt Engine
                  (scrape+classify)  (retrieve your    (build style-aware
                                      past comments)     prompt)
                                                              │
                                                              ▼
                                                        Groq LLM
                                                              │
                                                              ▼
                                                        Humanizer ─▶ Comment options
```

Key services live in `src/lib/services/`:
- `linkedin-scraper.ts` — fetch post content
- `post-analyzer.ts` — classify post type & topic
- `rag-service.ts` — retrieve relevant past comments
- `dynamic-prompt-engine.ts` — assemble the generation prompt
- `comment-generator.ts` + `groq-client.ts` — generate via Groq
- `humanizer.ts` — remove AI clichés

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- A **Groq API key** ([console.groq.com](https://console.groq.com))

### Setup

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env.local     # add your GROQ_API_KEY

# 3. Set up the local database (Drizzle + SQLite)
npx drizzle-kit push

# 4. Run the dev server
npm run dev                    # http://localhost:3000
```

### Run with Docker

```bash
docker-compose up --build
```

---

## 📂 Project Structure

```
src/
├── app/                      # App Router pages (dashboard, analytics, settings, post/[postId])
├── components/               # UI: upload, post, comments, shared
└── lib/
    ├── services/             # scraper, analyzer, RAG, prompt engine, Groq client, humanizer
    ├── db/                   # Drizzle schema & client
    ├── data/                 # comment angles, post types, AI-cliché list
    └── utils/                # logger, json parser, url helpers
backend/                      # optional FastAPI scraping service
```

---

## ⚠️ Disclaimer

For **educational and personal-productivity** use. Respect LinkedIn's Terms of Service and applicable data-privacy laws when fetching and processing post data.
