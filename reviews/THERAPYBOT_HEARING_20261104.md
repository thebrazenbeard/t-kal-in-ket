# TherapyBot — T'Kal-in-ket hearing (2026-11-04)

**Docket:** [`THERAPYBOT-TKIK-2026-11-04-v1`, issue #12](https://github.com/thebrazenbeard/t-kal-in-ket/issues/12)  
**Coordination:** [TherapyBot issue #3](https://github.com/thebrazenbeard/therapybot/issues/3#issuecomment-6633127127)  
**State:** OPEN; one challenge unanswered. This record is not a verdict, a clinical review, or a certification of direct cross-chat delivery.

## Proposition and falsifier

Proposition: A free Windows/Linux local-first HTML mental-health support application can provide useful, evidence-informed **nonclinical** conversation, consent-controlled encrypted records, and offline GGUF inference without mandatory third-party private-session services or spending. The design should be inclusive; “help everyone” is an aspiration, not a demonstrated universal outcome.

Falsifier: An obligatory paid/cloud service, unintended disclosure, unverified or fabricated clinical claims, unacceptably missed imminent danger in held-out safety tests, automatic irreversible record conversion, or an advertised deployment that cannot function locally.

## Frozen inputs for first-round debate

| Subject | Source head | Evidence |
|---|---|---|
| [`therapybot/main`](https://github.com/thebrazenbeard/therapybot/tree/6e0be42c7ff5115965584da015972cdc12092e0d) | `6e0be42c7ff5115965584da015972cdc12092e0d` | 20 local Python tests pass; 32 source metadata entries; 30 synthetic examples; Fernet vault; three local-model protocols |
| [TherapyBot PR #1](https://github.com/thebrazenbeard/therapybot/pull/1) | `5c70bfc8ad535ee6bf62ff86770c0159020ceaa1` | 27 local Python tests pass; AES-GCM vault, authenticated backup/restore, HTML UI; prior six VN2 live prompts 3 pass/1 partial/2 fail |
| [`t-kal-in-ket` core](https://github.com/thebrazenbeard/t-kal-in-ket/blob/b0af150c2405b519fd921bac33e5f9f1f35f92d7/tkik/core.py) | `b0af150c2405b519fd921bac33e5f9f1f35f92d7` | 39 local Python tests pass; one unresolved challenge at a time; reviewer strings are not authenticated identity |

The 34-case `main/research/safety_holdout.jsonl` synthetic holdout has **11/34 category matches on main** and **12/34 on PR #1**; PR #1's deterministic intercept missed all **22/22** cases whose synthetic expected category was immediate/concern. These are qualitative synthetic labels, **not clinician consensus or an actual clinical-effectiveness measure**. Green unit tests must not be interpreted as safety qualification.

## Actual native first-round reviewer positions

- **Pragmatism** (`/root/therapybot_main_advocate`): favor `main` as a conditional integration base, preserving the broader source register and model protocols. Objection: backup, browser hardening, migration and safety are incomplete.
- **Purist Logic** (`/root/therapybot_feature_advocate`): favor the feature branch as conditional authenticated-HTML/backup foundation. Objection: unsupported psychiatric assertions and fabricated citations appeared in actual model testing; inaccessible/low-end scenarios remain unqualified.
- **Bridge / independent hostile architecture** (`/root/independent_hostile_architect`): neither source qualifies for broad mental-health release; preserve original data, avoid automatic migration, and require new held-out tests.
- **Research/equity** (`/root/safety_equity_research`): universal-benefit framing is untestable; measure accessibility, literacy, cross-cultural response, false escalation and offline practicality.
- **Protocol inspector** (`/root/tkik_protocol_audit`): enforce actual `Case` state guards. The documented `waive_cross_examination` method is absent from current code.
- **Cross-chat transport investigator** (`/root/crosschat_transport_recon`): Github docket and comment are durable invitations only; another native chat's receipt is **not established**.

All six agent roles executed in a single ChatGPT provider context. Differently named agents are **not** independently authenticated models or credentialed clinical reviewers. The other TherapyBot ChatGPT native chat (Team Member 01) and its agents are **INVITED; response unverified**.

## Single open cross-examination challenge

**TKIK-TB-Q01 — Purist Logic → proposer / Pragmatism**

> What measurable minimum standard of safety and usefulness would justify offering TherapyBot broadly when both current implementations miss most of the 34 independent synthetic safety-routing cases?

Why it matters: release gates should be explicit before choosing an integration base. A defense should distinguish educational usefulness from clinical efficacy, avoid a crude numerical suicide-risk score, and include missed danger **and** false escalation, accessibility and offline model availability.

**Defense: awaited.** No participant's answer should be inferred. No T'Kal verdict may be issued while this challenge remains open. See [issue #12](https://github.com/thebrazenbeard/t-kal-in-ket/issues/12) for chronological replies and subsequent challenges.

## Architectural conflict left deliberately unresolved

1. `main` offers research breadth and multi-protocol inference; the feature offers stronger tested local backup/restore and a different authenticated browser contract.
2. Fernet and AES-GCM SQLite vault formats are **not interchangeable**. No silent migration or destructive overwrite.
3. Source indexing and valid citation identifiers do not prove an LLM claim is supported by its cited source.
4. Local-only processing does not establish confidentiality on a compromised machine, and neither source has demonstrated broad cross-platform accessibility or clinical outcomes.
5. Training rights are **not cleared** merely because a public clinical webpage was cited or indexed.

## Procedure / evidence boundary

The [implemented protocol](../tkik/core.py) requires a frozen claim after first review, three distinct reviewer IDs for determination, and an attributed directed peer dialogue involving each lens before **SUSTAIN**. An actual GitHub reply records a participant claim; it is not proof of an authenticated remote model invocation or an external clinical review. Preserve source heads, methods, dissent, and uncertainty. The Chair cannot infer a final determination from agent consensus.
