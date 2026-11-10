# Data Source Connector

Recommends the right Tableau Studio connector and auth pattern for a new data source. Advisory-only. Every step is a Desktop UI instruction because no connect-datasource tool exists.

**Example:** You say "I need to connect to a Snowflake warehouse; we use SSO." The skill picks the Snowflake connector, recommends OAuth auth, lists the network prerequisites (allow-list Snowflake OAuth endpoints), and hands you numbered Desktop UI steps.

## What it does

Compresses the "which connector, which auth" decision from a 20-minute internal debate to a single named recommendation with rationale. Reads a natural-language source description, matches against a locked connector catalog, applies a locked auth-pattern rubric, and produces Desktop UI steps.

## When to use it

- "Connect to Snowflake / Postgres / Salesforce / Excel."
- "How do I set up this connection?"
- "Which connector for X?"
- "OAuth or PAT or password?"

## When NOT to use it

- First-run "where do I start" (use the built-in Studio onboarding skill, `onboarding-concierge`).
- Modeling questions once connected (use `join-and-relationship-advisor`).
- Data-quality questions (use `data-quality-review`).
- Publishing to Server or Cloud (out of scope, Desktop-only).

## What you get back

- Primary connector recommendation plus one alternate if applicable.
- Auth pattern with a one-line "why this."
- Prerequisites (drivers, service accounts, network) called out upfront.
- Numbered Desktop UI walkthrough.

## Limitations

- Advisory-only. No connect-datasource tool exists. Every action is a Desktop UI instruction.
- Cannot verify environment claims (SSO vs. PAT vs. password) beyond what the user tells the skill.
- Connector catalog reflects Desktop 2026.2 (Beta). Older-version connector deprecations not tracked.
