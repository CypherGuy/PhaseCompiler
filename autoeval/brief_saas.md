Generate a phased project plan for the following:

**Project Name:** InvoiceFlow
**Description:** A SaaS API for freelancers to create, send, and track invoices with integrated Stripe payments. Clients receive a payment link via email (SendGrid), can pay online, and the freelancer sees real-time payment status in a simple React dashboard.
**Goal:** Build the full InvoiceFlow product from scratch — invoice CRUD, Stripe payment links, SendGrid email delivery, webhook-driven status updates, and a React dashboard showing outstanding and paid invoices.
**Stack:** Node.js 20 (Express backend), React 18 (frontend), PostgreSQL 16, Stripe API (payment links + webhooks), SendGrid API (transactional email), Docker Compose (local dev)
**Architecture:** Separate backend and frontend services, REST API, JWT authentication
**Starting point:** Nothing — greenfield project
**Phase count:** 8
**Primary user:** Freelancers who invoice 5–20 clients per month and want faster payment collection
**MVP (phases 1–5):** Freelancer can register, create an invoice, send it to a client via email with a Stripe payment link, and see the invoice marked as paid when the client completes payment.
**Full product (phases 6–8):** Invoice history dashboard with filtering, PDF invoice download, automated payment reminders via SendGrid for overdue invoices, and production deployment to Railway.
**Completion criteria:** Full 8-phase flow: register → create invoice → send payment link via email → client pays via Stripe → webhook updates status → dashboard reflects paid status → PDF downloadable → reminders sent for overdue invoices.
**Constraints:** JWT auth (no OAuth for MVP), Stripe payment links only (no embedded checkout), PostgreSQL for all persistent state, SendGrid for all outbound email, deployed to Railway in phase 8.
