---
title: Skeptical Deployment (Doubt First, Then Ship)
description: Operational principle for evaluating methods before adoption.
---

# Skeptical Deployment — FDE Operating Principle

> *"Before adopting a method, ask: What if I'm wrong? What would falsify this?"*

This principle is part of the FDE methodology's operating discipline. It is documented as a reference, not a script: any method — a trendy growth tactic, a new framework, a vendor's playbook — must be evaluated on first principles, not on hype.

## 1. Why This Principle Exists

Most projects fail because they adopt a method without questioning it. The skill must force the practitioner to identify failure modes upfront.

## 2. The Skeptical Deployment Loop

For every method considered, write down:

1. **Claim**: What does this method promise? (1 sentence)
2. **Source of Authority**: Who benefits from the claim? Is there a primary source or just secondary commentary?
3. **Failure Mode**: What would make this method a dead-end for your specific context?
4. **Cheapest Test**: What is the minimum evidence (file, command, page, click) that would prove or disprove the claim?
5. **Decision**: Ship, defer, or skip.

## 3. Worked Example: a high-risk programmatic-SEO tactic

Consider a growth method that promises rapid search ranking by mass-producing content on an aged or expired domain. Applying the Skeptical Deployment Loop:

- **Claim**: Rapid SEO ranking via mass content generation on a (possibly expired) domain.
- **Source of Authority**: A practitioner playbook. No primary source or measured ROI included.
- **Failure Modes**:
  - Manual creation of 15-20 pages is not industrial; it is labor that competes with the product.
  - Expired domains may carry toxic backlink profiles that trigger search-engine penalties.
  - The search Indexing API is documented for narrow content types (e.g. `JobPosting`, `BroadcastEvent`); using it for general pages is a gray area and may be ignored.
  - Authority signals (E-E-A-T) cannot be faked by a new domain with no history.
  - Parasite SEO on third-party platforms is increasingly devalued.
- **Cheapest Test**: Before scaling content production, publish 3 minimal HTML pages (no scripts, no generation), submit one URL via the Indexing API, and measure whether the search console registers the URL within 7 days.
- **Decision**: **Defer scaling.** Ship only the 3 minimal pages as a test. Do not invest in expired domains, automation scripts, or parasite SEO until the 3-page test produces real indexation data.

## 4. Constraint on the FDE Skill Itself

The FDE Skill, by its own principle, cannot ship an automation script for such a tactic without first passing the Skeptical Deployment Loop. The skill's own anti-pattern #1 (`Generic "use AI/ML" without stack/cost/team/ROI`) forbids generating code without measured evidence. Therefore, the skill itself must:

- Refuse to generate automation scripts on demand without a documented Failure Mode analysis.
- Treat any "playbook" as a hypothesis to test, not a procedure to execute.

## 5. Why This Document Is Markdown, Not Code

Following industrial practice: a principle is documentation. Documentation must be readable by humans, indexable by search, and editable without a runtime. Code that *enforces* a principle can be added later, after the principle has proven its value in practice.

## 6. From Skeptical Deployment to FDE Assurance Score

Skeptical Deployment is Step 2 (Contradiction) of the DeepSCR loop. Step 3 (Verification) and Step 4 (Certification) are defined in [fde-trust-score.md](fde-trust-score.md). Every FDE deliverable must include a `## FDE Assurance Score` section that closes the loop and produces a verifiable 0-100 score.
