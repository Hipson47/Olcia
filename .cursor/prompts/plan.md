---
id: cmd-plan
title: Structured Plan (ToT+GoT)
---

Instructions:
- Build a Tree-of-Thought (branch=3, depth=4). Score nodes 0..1.
- Promote winners into a Graph-of-Thought. Aggregate, refine, create synergies.
- Emit a micro-plan of ≤10 steps scoped with @file/@folder. Each step includes a test idea.

Outputs: plan, risks, tests_contract, diff_impact.
