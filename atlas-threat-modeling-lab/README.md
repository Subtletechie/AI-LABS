# AI Threat Modeling with MITRE ATLAS

## What this lab is

A hands-on, no-code exercise. You take a realistic AI system and work it through the MITRE ATLAS framework to produce a threat model. No setup, no tools  just the worksheet and your thinking. Time: 45–60 minutes, best done in pairs.

## The scenario

NorthBank deploys a customer-facing LLM chatbot on its website. Customers ask it questions about their accounts in natural language. The chatbot was fin tuned on NorthBank's internal documentation, retrieves answers from a knowledge base of policy documents, and can call an internal API to look up a logged-in customer's real account balance. It is reachable by anyone on the public internet.

## Your task

Work through each ATLAS tactic in the worksheet. For each, decide whether and how an attacker could use it against the NorthBank chatbot, and write one concrete technique. Then pick your top 3 threats (rank by likelihood × impact) and propose one control for each, bridging to controls you already know (input validation, access control, monitoring, rate limiting).

## Files in this lab

- `WORKSHEET.md` — the table you fill in (or download `worksheet.csv` to fill in a spreadsheet)
- `ATLAS_PRIMER.md` — plain-English description of each ATLAS tactic
- `worksheet.csv` — same worksheet as a downloadable spreadsheet
- `SUBMISSION.md` — what to hand in

> Note: the full ATLAS framework has 16 tactics; this lab focuses on the core lifecycle tactics. The complete matrix is at https://atlas.mitre.org.
