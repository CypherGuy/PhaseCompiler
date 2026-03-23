Generate a phased project plan for the following:

**Project Name:** DevLogSummarizer
**Description:** A CLI tool that reads a project's git log, groups commits by day or week, and uses OpenAI to generate human-readable summaries of what was worked on. Output is written to a Markdown file or printed to stdout. Designed for developers who want a frictionless way to populate standup notes or changelogs.
**Goal:** Build the full DevLogSummarizer CLI from scratch — git log parsing, OpenAI summarisation, configurable output formats, and local SQLite caching so repeated runs don't re-summarise identical commits.
**Stack:** Python 3.11, Click (CLI framework), SQLite (local cache via sqlite3 stdlib), OpenAI API (GPT-4o for summarisation)
**Architecture:** Single-file CLI distributed as a pip package, no server, no frontend
**Starting point:** Nothing — greenfield project
**Phase count:** 6
**Primary user:** Solo developers who want automated standup notes and changelogs
**MVP (phases 1–4):** Developer can run `devlog summarize --since 7d` in any git repo and get a Markdown summary of the week's commits, grouped by day, written to `devlog.md`.
**Full product (phases 5–6):** SQLite caching to skip already-summarised commits, configurable output (stdout, file, format), and a `devlog config` command for setting OpenAI key and default options.
**Completion criteria:** `devlog summarize --since 7d` runs in any git repo, calls OpenAI, writes `devlog.md` with grouped daily summaries, and skips already-cached commits on re-runs.
**Constraints:** No network calls except to OpenAI API, must work offline for cached commits, pip-installable with a single `pip install devlogsummarizer`, Python 3.11+ only.
