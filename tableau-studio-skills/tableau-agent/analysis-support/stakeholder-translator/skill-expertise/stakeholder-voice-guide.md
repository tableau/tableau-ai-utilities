# Stakeholder Voice Guide

Five locked audience profiles for stakeholder-translator. The skill maps any author-declared audience to one of these before generating output.

## C-suite

**Vocabulary.** Business outcomes. Revenue, cost, growth, risk, retention. No fields, no aggregations, no filter names.

**Attention budget.** 1-2 minutes. One paragraph.

**What they want to know.**
- The headline number.
- Whether it is good or bad (author owns the "good or bad" framing).
- The strategic implication the author sees (author owns).

**Follow-up patterns.**
- Strategic. "What should we do."
- Trajectory. "Is this getting better or worse."
- Comparison. "How do we compare to peers / target."

**Avoid.**
- Named technical fields.
- Methodology ("this is computed using an INCLUDE LOD").
- Chart types ("the bar chart shows").

## Business sponsor

**Vocabulary.** Named business metrics with definitions. Can hear "ARR" and "NRR" if defined in context. Comfortable with time windows (QoQ, YoY).

**Attention budget.** 3-5 minutes.

**What they want to know.**
- The metric and how it is defined.
- Whether the data matches their expectation.
- Where the data differs from the business model.

**Follow-up patterns.**
- Expectation. "I thought that number would be higher. Why is it lower."
- Attribution. "What is driving this."
- Scope. "Does this include the enterprise segment."

**Avoid.**
- Chart-construction detail.
- Internal filter mechanics.

## Operational manager

**Vocabulary.** Action-focused. Named entities (accounts, products, regions, people). Can hear "SLA" and "throughput" if those are their domain.

**Attention budget.** 3-5 minutes.

**What they want to know.**
- Who is in the top-N or bottom-N.
- What to do about them.
- Who owns the action.

**Follow-up patterns.**
- Tactical. "Which account should I call first."
- Attribution. "Why is this account at the bottom."
- Timeline. "When did this change."

**Avoid.**
- Trend analysis unless it drives action.
- Strategic framing (that is the sponsor's conversation).

## External customer

**Vocabulary.** Minimal shared context. Define every acronym on first use. Avoid internal product names unless they are the subject.

**Attention budget.** 5-10 minutes. Context eats budget.

**What they want to know.**
- What business is being described.
- What time period.
- What the measure means in plain language.

**Follow-up patterns.**
- Clarifying. "What does X mean."
- Scope. "Is this all customers or a subset."
- Framing. "What should I take away."

**Avoid.**
- Internal benchmarks or targets unless defined.
- Any assumption of shared product knowledge.

## Cross-functional peer

**Vocabulary.** Shared vocabulary from their function, not yours. If translating a sales dashboard for a product manager, use product vocabulary.

**Attention budget.** 3-5 minutes.

**What they want to know.**
- How this affects their function.
- What they need to do differently.
- What they can rely on this dashboard to tell them going forward.

**Follow-up patterns.**
- Relational. "How does this affect my team."
- Shared workflow. "Is this the single source of truth for X."
- Access. "Can my team see this directly."

**Avoid.**
- Over-explaining concepts they already know in their own domain.
- Under-explaining your domain's jargon.

## Mapping non-standard audiences to locked profiles

| Author's phrase | Mapped profile |
|---|---|
| "my CEO" | C-suite |
| "my VP" | C-suite if business VP, Business sponsor if functional VP |
| "my director" | Business sponsor |
| "my boss" | Business sponsor (default); Operational manager if the author's role is operational |
| "my team" | Cross-functional peer |
| "another team at the company" | Cross-functional peer |
| "a customer" | External customer |
| "a prospect" | External customer |
| "my partner at X" | External customer |
| "a board member" | C-suite |

State the mapping in the output so the author can correct.

## Voice violations to catch

- Using methodology language in C-suite voice.
- Using named fields in external-customer voice.
- Skipping the scope-boundary section regardless of audience (HC-5).
- Fabricating business conclusions ("revenue is strong") in any voice (HC-3).
