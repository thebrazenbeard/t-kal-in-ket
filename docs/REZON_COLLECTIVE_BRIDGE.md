# Rezon Collective V1: bounded snapshot bridge

Source binding examined: `thebrazenbeard/rezon@72e9ec97e39eb0f0cfed0e62c5252f027b25ecb9` — `src/rezon/collective.py` (`CollectiveSnapshot.to_dict` and `CollectiveStore._snapshot`).

`tkik.rezon_bridge.assess_snapshot(snapshot)` consumes **an already exported JSON object**, not a live connection. It independently recomputes the upstream canonical `input_digest` from the episode, prompt, agent roster and ordered contributions; validates participant identities, distinct answers/reviews, target references, missing-answer barrier and stale synthesis flags; and reports a typed readiness assessment.

Example:

```python
from tkik.rezon_bridge import assess_snapshot

# payload = json.load(open("exported_rezon_snapshot.json", encoding="utf-8"))
# status = assess_snapshot(payload)
# print(status.phase, status.missing_reviews, status.origin_verified)
```

This import is **READ-ONLY**. Validating a digest proves structural consistency of a transmitted object against its embedded digest; it does **not** establish cryptographic origin, independent executions, consensus truth, trusted timestamps, model ownership or the user's consent to close a case. `origin_verified` is always `False` until a separately implemented and verified attestation boundary exists. `REVIEWED_UNVERIFIED` is not a TKIK disposition and cannot call `Case.determine` itself.

The bridge requires external mapping from Rezon agent IDs to TKIK lenses; reviewers' actual model IDs, runtime/process receipts and source/input digests must be independently qualified. Do not equate three role labels or relayed submissions with independent reasoning. The original case retains a single unanswered challenge at a time, and only the proposer may explicitly withdraw.

## Existing parallel Rezon work

Rezon [research PR #109](https://github.com/thebrazenbeard/rezon/pull/109), observed on 2026-10-23 at `f1b6307b065f9aa7a1a1df369be16e08dfa31554`, documents **three local model hosts plus a separate GPT-6 cloud source**, four initial answers and four targeted reviews in one native CollectiveStore episode. Those authors explicitly qualify the transport as primary-relayed, not an authenticated permanent four-machine ingress. That PR remains a separate **draft/HOLD** with a security warning about current Rezon source; this TKIK branch neither merges nor executes it.

Transport integration, authenticated host identity, verified provenance and safely gated multi-host deployment remain separate future work. Never open an untrusted Rezon repository in an editor with automated workspace tasks; inspect only approved source paths.

## Command-line inspection (source-only)

Run from the repository root using Python 3.10 or newer:

```sh
python -m tkik.inspect_rezon path/to/collective-snapshot.json
python -m tkik.inspect_rezon path/to/collective-snapshot.json --require-reviewed
python -m tkik.inspect_rezon - < path/to/collective-snapshot.json
```

The input must be a **Rezon CollectiveSnapshot.to_dict() JSON export**, not a SQLite database path, a prompt transcript or a fabricated review. The inspector makes **no network request**, never invokes a model and does not write any user state. Input size is capped at 1 MiB; invalid Unicode, nonstandard JSON numbers, duplicate JSON keys, malformed envelopes and inconsistent internal hashes produce a bounded `structural_check: FAIL` response and exit **2**. A valid envelope produces `structural_check: PASS` (exit **0**), or exit **3** under `--require-reviewed` if the peer review phase is incomplete.

A PASS reports only the derived episode ID, digest, review/answer counts and missing participants. It **does not echo prompt, model answers, challenges, source text or evidence**. All reports explicitly include `origin_verified: false`, `independence_verified: false`, `authority: NONE`, and `sustain_authorized: false`. Even a reviewed, internally consistent export remains caller-supplied evidence and cannot itself close a TKIK case.

The reference schema is Rezon Collective V1 at `thebrazenbeard/rezon@72e9ec97e39eb0f0cfed0e62c5252f027b25ecb9`. Future schema changes require an explicitly reviewed adapter revision, not guesses about runtime provenance.
