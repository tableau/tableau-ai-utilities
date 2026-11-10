# Blitz Scenario Example

A full worked Blitz example sequence, used only as a structural template and never shown to the player.

---

**[Intake complete. Player selected: Analyst audience, Intermediate experience, Performance focus, Straightforward Reality, Blitz depth.]**

---

**Opening (TableauQuest response):**

Greetings adventurer.

You're 45 minutes from your Monday standup when Slack lights up. Marcus, your Analytics Manager, has forwarded an email chain:

*"The Sales Pipeline dashboard is loading in 22 seconds. VP of Sales (Dana) tried to pull it up during a client call on Friday. She closed it after 12 seconds and used a screenshot from last week instead. She's asked why we can't 'just make it fast.' We need a plan by end of day."*

You pull up the workbook. It's running against a live connection to Snowflake -- 4.7M rows across 3 tables joined in Tableau. The dashboard has 14 sheets, 6 quick filters, and 4 LOD calculations. Last month it loaded in 6 seconds. Three weeks ago, the data engineering team added a new transaction history table to the schema, and someone joined it in.

Marcus is waiting for your response.

1. Tell Marcus you'll extract the data source now: faster loads today, but stale data until the refresh job is built and scheduled
2. Tell Marcus you need to profile the workbook first, which costs the morning but shows what changed before you touch anything
3. Tell Marcus you'll remove the new table join and republish: the quickest fix, at the risk of breaking sheets that depend on it
4. Ask Marcus if Dana would accept a filtered version (last 90 days only) while you investigate: quick relief, but she gets less data

---

**[Player selects 2]**

---

**Decision 2 response:**

Marcus nods. "Fine, but I need something I can tell Dana by 3pm. Not 'we're looking into it' -- she's heard that before."

You open Tableau Desktop and connect to the published workbook. Performance Recording confirms it: the new join to `transaction_history` is generating 11.2M rows after the join fans out. Four of the 14 sheets don't even reference fields from that table. Two LOD calculations -- `{ FIXED [Account ID] : SUM([Pipeline Value]) }` and `{ FIXED [Rep ID], [Quarter] : COUNT([Opportunity ID]) }` -- are now computing across the inflated row set.

It's 10:15am. Your standup is in 30 minutes.

1. Remove the transaction_history join and republish now: fixed by lunch, but the data engineering team's new reports lose their source and you haven't asked them
2. Split the sheets that need transaction_history into a second workbook and republish both: fixes everything, but takes the afternoon and doubles the publishing risk
3. Document your findings and bring the tradeoffs to standup: Marcus stays informed, but Dana's dashboard stays slow for hours more

---

**[Player selects 3]**

---

**Decision 3 response:**

At standup, Marcus listens through your explanation and pauses. "I like the root cause. But I have to give Dana something today, and data engineering says the new table feeds two of their own reports."

Dana's Slack message lands while he's still talking: "Is this fixed yet? I have the regional review Wednesday."

1. Commit to the separate-workbook fix with a 2-day timeline, and promise Dana a root-cause summary today: honest, but you are now publicly on the hook for Wednesday
2. Publish a 90-day filtered version of the main dashboard today as interim relief: Dana gets speed now, but she sees less history and you maintain two versions
3. Ask data engineering to roll back the schema change: fixes it at the source, but you depend on another team's calendar and Dana waits on them

---

**[Player selects 1]**

---

**Resolution:**

Marcus forwards your one-paragraph summary to Dana within the hour. Her reply comes at 2:47pm: "Thanks for the transparency. Two days works if it actually stays fast after that. I don't want to have this conversation again in a month."

You spend the afternoon building the separated workbook and documenting the change for the data engineering team, so the next schema addition goes through a review. On Tuesday the main dashboard loads in 5.8 seconds. By Wednesday both workbooks are published, and the regional review runs on time. The two data engineering reports lag a day while their owner, Priya, rebuilds a connection, and she lets Marcus know it was noticed.

---

**Ending Screen:**

**The Measured Response**

You identified root cause before acting, communicated tradeoffs transparently, and delivered a sustainable fix within a reasonable timeline. Dana's trust was preserved through honesty rather than a rushed patch. The documentation you created establishes a precedent that prevents this class of issue from recurring silently.

[A pixel-art analyst's desk bathed in steady golden light. Two monitor screens show clean dashboard layouts with green status indicators. A Slack notification glows with a thumbs-up. The scene is still and stable -- three bright sparkles orbit gently above the monitors like a constellation coming into focus.]

**Sparkle Level:** ✨✨✨

---

*End of example. This demonstrates: specific numbers, named stakeholders, time pressure, realistic Tableau constraints, three decisions (Blitz minimum), tradeoffs on every option, consequence summary tied to choices, and sparkle justified by evidence discipline and stakeholder care.*
