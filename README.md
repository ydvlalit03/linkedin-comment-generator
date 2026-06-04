# LinkedIn Comment Generator

A full-stack **Next.js** app that generates personalized, human-sounding LinkedIn comments in *your* voice. Paste a post URL (or upload a CSV of posts) and it analyzes the post, retrieves your relevant past comments via a **RAG** pipeline, generates comment options across different angles, and runs them through a humanizer to strip out tell-tale "AI clichés."

---

## How It Works

```
Post URL / CSV → Post Analyzer → RAG Service → Dynamic Prompt Engine → Groq LLM → Humanizer → Comments
                 (scrape+classify) (your past    (style-aware prompt)            (de-cliché)
                                    comments)
```

---

## Features

- **RAG over your own comments** — embeds your comment history and retrieves the closest matches as style anchors for every new comment
- **Post analysis** — scrapes and classifies the target post's topic, tone and type before generating
- **Multiple comment angles** — agreement, question, insight, story, and more
- **Humanizer** — post-processes output against a curated AI-cliché list so comments read naturally
- **Groq-powered inference** — very low-latency LLM responses
- **CSV bulk upload** — process many post URLs at once
- **Dashboard & analytics** — manage posts, review comments, track usage

---

## Tech Stack

- **Framework**: Next.js 16 (App Router) + React 19, TypeScript
- **Styling**: Tailwind CSS v4, lucide-react, sonner
- **LLM**: Groq SDK (fast inference)
- **Database**: Drizzle ORM + better-sqlite3 (local SQLite)
- **Retrieval**: custom RAG service over embedded comment history
- **Backend (optional)**: supplementary FastAPI scraping service in `backend/`

---

## Quick Start

### Prerequisites

- Node.js 18+
- A **Groq API key** ([console.groq.com](https://console.groq.com))

### Setup

```bash
npm install
cp .env.example .env.local      # add GROQ_API_KEY
npx drizzle-kit push            # set up local SQLite via Drizzle
npm run dev                     # http://localhost:3000
```

Run with Docker: `docker-compose up --build`

---

## Project Structure

```
src/
├── app/            # App Router pages (dashboard, analytics, settings, post/[postId])
├── components/     # UI: upload, post, comments, shared
└── lib/
    ├── services/   # scraper, analyzer, RAG, prompt engine, Groq client, humanizer
    ├── db/         # Drizzle schema & client
    ├── data/       # comment angles, post types, AI-cliché list
    └── utils/      # logger, json parser, url helpers
backend/            # optional FastAPI scraping service
```

---

## Disclaimer

For educational and personal-productivity use. Respect LinkedIn's Terms of Service and applicable data-privacy laws.
