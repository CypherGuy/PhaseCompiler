Generate a phased project plan for the following:

**Project Name:** StudyBattles
**Description:** A revision tool where students upload study materials (PPTX, DOCX, YouTube videos), the system generates a topic hierarchy via OpenAI, and they grind through boss encounters to prove understanding. Students answer predetermined question types, get marked against LLM-generated key points, and unlock parent nodes only after defeating all children.
**Goal:** Build the full StudyBattles from scratch — document upload, topic tree generation, question answering, mark scheme evaluation, and node unlock mechanics.
**Stack:** Python 3.11 (FastAPI backend), React 18 frontend, MongoDB, AWS S3 (document storage), OpenAI API (tree generation + question generation + answer evaluation)
**Architecture:** Monorepo, single-developer project, REST API
**Starting point:** Nothing — greenfield project
**Phase count:** 11
**Primary user:** Students that want to learn a new topic efficiently
**MVP (phases 1–7):** Student can upload a document, generate a boss tree, click into bottom-level nodes, answer questions in predetermined formats (Define, Solve, Compare, ELI5, Finish the Answer), receive marks based on LLM-generated mark schemes, and unlock parent nodes after defeating all children.
**Full product (phases 8–11):** Session persistence across page reloads, result display with key-point feedback, frontend polish (loading states, error handling, responsive layout), and end-to-end testing.
**Completion criteria:** Full 11-phase flow works end-to-end: upload document → generate tree → answer questions → receive marks → unlock parent nodes → session persists across page reloads → UI is polished and tested.
**Constraints:** No auth system required (session-based via localStorage), AWS S3 for file storage, OpenAI GPT-4 for all LLM tasks, max tree depth of 3 levels.
