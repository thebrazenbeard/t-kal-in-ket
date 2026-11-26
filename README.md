# T’Kal-in-ket — auditable adversarial inquiry

A practical, unofficial peer-examination protocol inspired by T’Kal-in-ket in *Star Trek: Discovery* (“Unification III”). The purpose is to **discover the weaknesses in a claim, not win an argument**.

The fictional process places a challenger before three peers with an advocate and permits withdrawal. The software's evidence records, executable gates, and remote model receipts are **engineering additions**, not purported canon.

## Four roles, one falsifiable claim

Three peer lenses—**Purist Logic**, **Pragmatism**, and **Bridge**—challenge a frozen hypothesis. **Chair** protects the record, tracks dissent and blocks unsupported determination. The challenger and advocate have opportunity to clarify, defend, concede and withdraw. A role label alone is not proof that a separate model or host ran.

## Live collective mode

The protocol also supports a facilitated sequential quorum with a variable number of participants. Each examiner must make a substantive, evidence-bearing challenge or improvement rather than passively agree. One proposer, one current proposition, one speaking floor and a genuine defense opportunity are preserved; simplify, retain or withdraw when justified. Existing portfolio components may be examined for declining usefulness, consolidation or localization against actual consumer evidence. See [live sequential collective examination](docs/PROTOCOL.md#live-sequential-collective-examination-facilitated-mode). This is a documented human/agent facilitation method, not an installed transport or a new executable gate.

## Quick start

Python 3.10+ with no third-party dependencies:

```sh
python -m unittest discover -s tests -v
python -m tkik.cli
python -m tkik.inspect_rezon /path/to/rezon-export.json --require-reviewed
# Or inspect an exported JSON snapshot on standard input:
# python -m tkik.inspect_rezon - < snapshot.json
```

The inspector **only reads exported Rezon Collective V1 JSON**. It checks the structural digest, answer/review coverage and synthesis freshness. It emits a bounded JSON report without printing model answers and exits 2 for malformed/inconsistent input or 3 when `--require-reviewed` is unmet. An exit 0 is **not** independent host authentication, authority to `SUSTAIN`, or proof of scientific truth.

The original `tkik.cli` is a **scripted demonstration only**. No actual Rezon inference, Lappy/VN1/VN2 execution, scientific learning or autonomous effect is claimed.

## Contents

- [Scientific and adversarial protocol](docs/PROTOCOL.md): evidence classes, three peers, advocate, one-question defense flow, dissent and closure gates.
- [Research and source distinctions](docs/RESEARCH.md): fictional procedure versus original engineering extensions.
- [Rezon Collective read-only bridge](docs/REZON_COLLECTIVE_BRIDGE.md): inspect exported JSON with canonical digest, peer-target, completeness and synthesis-staleness checks, either programmatically or using `python -m tkik.inspect_rezon`. No live host authentication. [Four-source transport proposal](docs/REZON_INTEGRATION.md) remains uninstalled.
- [Core case state machine](tkik/core.py): fail-closed determination and withdrawal.
- [Protocol regression tests](tests/test_core.py) and [CI](.github/workflows/tests.yml).

## Determination

The currently implemented `SUSTAIN` gate requires three distinct reviewer identities and a directed, answered/conceded peer-exchange cycle touching every peer as questioner and respondent. `REFINE` and human withdrawal remain available without fabricating an exchange. A different reviewer ID is **not** independent model/host attestation, and written defenses alone are not proof of actual inference. Once the first review is accepted, the proposition and definitions are bound by a digest; material changes require a new case version.

Partial and unresolved defenses can be continued; a new question cannot replace them until resolution. **Only the proposer may withdraw.**

A case may be **SUSTAINED**, **REFINED** or **WITHDRAWN** on documented reasons. SUSTAIN does not mean universal proof. Unresolved or partially answered challenges block normal closure; silent absence never means concession. External reviews need real attributable invocation records before they count as independent sources.

## Boundaries

Never put private deliberations, identifying case material, credentials or secrets in this public repo. Verdicts do not authorize merges, deployments, model-training or other protected effects. The independent four-host adapter must be built against current Rezon source and verified with live receipts before anyone describes that adapter as an authenticated running quorum. Externally facilitated live proceedings are distinct from the adapter.

**Status:** tested in-memory peer-examination gate plus a read-only Rezon Collective V1 snapshot verifier (tested against a persisted native four-source episode). No authenticated live remote transport, cryptographic reviewer custody, model self-learning or production qualification. No software license selected.
