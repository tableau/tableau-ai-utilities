# Compare Mode Reference

Output layouts and delta rules for comparing two projects or comparing a scan to a prior scan.

When the user asks to compare two projects, two scans over time, or current vs. prior:

### Compare Two Projects (side-by-side)

Run the full scan flow on each project independently, then produce a comparison output:

```
# Governance Comparison: [Project A] vs [Project B]

|                | [Project A] | [Project B] |
|----------------|:-----------:|:-----------:|
| Grade          | B-          | D-          |
| Score          | 82          | 61.5        |
| Staleness      | A           | D           |
| Usage          | B           | B           |
| Certification  | C           | D           |
| Naming         | A           | D           |
| Structure      | B           | D           |
| Performance    | A           | A           |
| Metadata       | C           | C           |
| Findings       | 6           | 10          |
| Critical       | 0           | 1           |

Winner: [Project A] — [one-line why]
[Project B] top gap: [highest-impact difference]
```

### Compare to Prior Scan (delta)

If a prior scan exists in memory for the SAME scope and preset, automatically produce delta in the header. If the scope or preset differs, write "No comparable prior scan" and skip it. Resolved and New counts come from diffing the saved findings list (domain|contentId|severity):

```
## B- — 82/100 (↑8 from C/74 on 2026-06-15)
> Certification gains drove the improvement. Staleness still needs work.

Changes since last scan:
- Resolved: 3 findings (2 HIGH, 1 MEDIUM)
- New: 1 finding (LOW)
- Net: -2 findings, +8 points
```
