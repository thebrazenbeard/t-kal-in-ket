# T’Kal-in-ket — auditable adversarial inquiry

A practical, unofficial peer-examination protocol inspired by T’Kal-in-ket in *Star Trek: Discovery* (“Unification III”). The purpose is to **discover the weaknesses in a claim, not win an argument**.

The fictional process places a challenger before three peers with an advocate and permits withdrawal. The software's evidence records, executable gates, and remote model receipts are **engineering additions**, not purported canon.

## Four roles, one falsifiable claim

Three peer lenses—**Purist Logic**, **Pragmatism**, and **Bridge**—challenge a frozen hypothesis. **Chair** protects the record, tracks dissent and blocks unsupported determination. The challenger and advocate have opportunity to clarify, defend, concede and withdraw. A role label alone is not proof that a separate model or host ran.

## Quick start

Python 3.10+ with no third-party dependencies:

```sh
python -m unittest discover -s tests -v
python -m tkik.cli
```

The CLI is a **scripted demonstration only**. No actual Rezon inference, Lappy/VN1/VN2 execution, scientific learning or autonomous effect is claimed.

## Contents

- [Scientific and adversarial protocol](docs/PROTOCOL.md): evidence classes, three peers, advocate, one-question defense flow, dissent and closure gates.
- [Research and source distinctions](docs/RESEARCH.md): fictional procedure versus original engineering extensions.
- [Rezon four-source integration contract](docs/REZON_INTEGRATION.md): proposed transport, durable receipts and independence requirements; not yet connected.
- [Core case state machine](tkik/core.py): fail-closed determination and withdrawal.
- [Protocol regression tests](tests/test_core.py) and [CI](.github/workflows/tests.yml).

## Determination

The currently implemented `SUSTAIN` gate requires three distinct reviewer identities and a directed, answered/conceded peer-exchange cycle touching every peer as questioner and respondent. `REFINE` and human withdrawal remain available without fabricating an exchange. A different reviewer ID is **not** independent model/host attestation, and written defenses alone are not proof of actual inference. Once the first review is accepted, the proposition and definitions are bound by a digest; material changes require a new case version.

A case may be **SUSTAINED**, **REFINED** or **WITHDRAWN** on documented reasons. SUSTAIN does not mean universal proof. Unresolved or partially answered challenges block normal closure; silent absence never means concession. External reviews need real attributable invocation records before they count as independent sources.

## Boundaries

Never put private deliberations, identifying case material, credentials or secrets in this public repo. Verdicts do not authorize merges, deployments, model-training or other protected effects. The independent four-host adapter must be built against current Rezon source and verified with live receipts before anyone describes this as a running quorum.

**Status:** source-level peer-examination gate with tests; no verified live Rezon adapter, durable remote invocation custody, or production qualification. No software license has yet been selected.
