# T’Kal-in-ket protocol v0.1

## Source fidelity versus extensions

In *Star Trek: Discovery* “Unification III,” a challenger faces three peers and has an advocate; proceedings may end in withdrawal. The production does **not** define our Python schema, thresholds, peer role names, or multi-model API. Those are operational inventions and may be revised.

## Quorum roles

- **Challenger**: owns the claim; has opportunity to clarify, defend, concede and withdraw.
- **Advocate (sha-set)**: flags procedural unfairness, omitted context, changed terms, inaccessible evidence and coercive tactics; does not manufacture defenses.
- **Purist Logic**: tests consistency, definitions, deductive validity and counterexamples.
- **Pragmatism**: tests implementation, data quality, experimental controls, opportunity costs and feasibility.
- **Bridge**: tests frame mismatch, human implications, alternative explanations and system-level effects.
- **Chair**: verifies case identities, access boundaries, independent receipt status, outstanding attacks and final decision gates. Does not silently rewrite reviewers' findings.

## Evidence classes

Record propositions individually as USER_DIRECT, REPOSITORY_SOURCE, RUNTIME_OBSERVATION, EXTERNAL_EVIDENCE, INFERENCE, HYPOTHESIS, AUTHORITY, ACTION, EFFECT, VERIFICATION or UNKNOWN. A citation indicates an evidence source; it does not prove the claim is correct. Preserve source timestamp, immutable source identifier when available, verification method, scope, uncertainty, exclusions and contradictions.

## Interactive cross-examination

At most one unanswered attack per case; show lens, precise target, question, significance and invitation for defense. Mark responses ANSWERED, PARTLY_ANSWERED, CONCEDED, SKIPPED, WAIVED or UNRESOLVED. Silence is not a concession. A human may pause or withdraw at any time. The quorum may continue after an explicitly recorded waiver; do not invent one.

## Determination

Source implementation additionally requires for `SUSTAIN`: three distinct `reviewer_id` values, a frozen claim-and-definitions digest from the first review, and at least one attributed `ANSWERED` or `CONCEDED` directed peer challenge from and to each of the three lenses. A waiver, silence, partially answered question, or three copied reviewer identities cannot satisfy this gate. An explicit `defender_id` must match the registered respondent reviewer ID. `REFINE` remains a legitimate preliminary disposition without this complete exchange, and withdrawal does not require permission from the peers. If the participants cannot complete the cycle, the claim cannot be `SUSTAIN`ed on this source-level contract.

SUSTAIN: presently supported inside the specified scope; not proven universal. REFINE: material premises, scope, implementation or tests must change. WITHDRAW: claim withdrawn or no longer defensible in its stated form. Each disposition requires recorded reasons and salient dissent. Administrative gate: three distinct *lens* reviews and no outstanding cross-examination. The gate **does not** demonstrate three independent model executions; that stronger claim requires checked external receipts. It also does not make mutable Python objects a tamper-proof ledger: a malicious in-process caller can alter public containers or private fields. The claim digest detects ordinary changes during admissible case methods; authenticated append-only custody belongs to a separate transport/persistence layer.

## Review integrity

Do not equate four persona prompts sent to one model with four independent reasoning sources. Bind provider, host, actual model identifier, input digest, frozen subject and challenge IDs, outbound invocation ID, attempt/outcome state, and full returned response hash. If connection times out after dispatch, report OUTCOME_UNKNOWN rather than inferring failed execution. Do not adjudicate over missing reviews as if they happened. Expose correlated models and shared context as independence limitations.

## Safeguards

Never put private payloads, API tokens or identifying evidence in public cases. Do not publish model prompts containing third-party secrets. No irreversible or protected effects are authorized by an inquiry verdict alone. High-stakes advice demands qualified human review and domain-appropriate safety boundaries.
\n## Explicit zero-attack waiver\n\nA new case cannot be adjudicated with zero challenge records unless the calling application records an explicitly authorized reason through `Case.waive_cross_examination(reason)` before any attack. That waiver is not inferred from silence. After any attack begins, its disposition must be recorded under `Case.resolve`; a previous no-attack waiver cannot subsequently be paired with late attacks in the same case. Authentication of the participant who grants a waiver is an **application responsibility**, not proven by this in-memory state machine.\n
## Active challenges and disposition boundaries

Partly answered and unresolved challenges remain the single active question until explicitly revisited and finally resolved. A chair cannot silently use determine(WITHDRAW): the proposer must call withdraw(reason). A SUSTAIN verdict still needs three distinct reviewer IDs, a frozen claim and directed, attributed cross-examination across all three lenses under the implemented invariant; a no-attack waiver does not bypass that gate. REFINE remains available with three reviews and no outstanding question even when no full cross-examination took place.
