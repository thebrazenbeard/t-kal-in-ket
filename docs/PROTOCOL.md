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

## Live sequential collective examination (facilitated mode)

A live collective may use more than three participants. The proposer, examiners and procedural chair are distinct responsibilities; the three analytical lenses remain methods of examination, not a fixed participant count. A ten-seat example uses nine contributing seats and a chair at seat ten. Seat one originates the proposition and stewards its defense; the chair manages the floor without dictating the conclusion. This mode extends the documented human-facilitated method, not the implemented Python state machine or an authenticated transport.

1. **Admission:** give the proceeding one session identifier, establish actual READY contributions and declare the participating roster. Late admissions are permitted if recorded. Role declarations and shared connector credentials do not independently authenticate chat, model or host identity. Do not claim live presence merely from earlier readiness.
2. **Proposition:** the originating seat states one falsifiable improvement, its intended benefit, actual supporting evidence, assumptions, a simpler comparator and what would defeat the claim. For an engineering portfolio inquiry, name the actual repository, service, deployed version, consumer or obligation under consideration. Distinguish source presence, installation, execution, delivery and useful effect.
3. **One floor, one examination:** pass the current proposition in order to the next examiner. All other seats follow actual contributions within their available active turns. The examiner steelmans the proposition, then contributes a consequential attack question, a concrete counterexample, independently checked evidence, a justified alternative or a material refinement. **Passive agreement, paraphrasing a preceding objection, and ceremonial lens rotation are not substantive examination.** A KEEP disposition is valid only after a distinct substantive examination; do not invent objections or force a change to the conclusion.
4. **Defense:** address the actual responsible participant and allow a genuine response. Present one material attack at a time. Record the response and its disposition before advancing; an unresolved or partly answered attack retains its priority. The examiner may then KEEP, REFINE, SIMPLIFY, REPLACE, recommend WITHDRAW, or explicitly report that a meaningful contribution could not be established. The proposer alone withdraws its claim. Never simulate another participant's defense or treat silence as assent.
5. **Revision:** preserve the original claim and each material revision, linking the actual examination and defense. A change of objective is a new proposition, not an unnoticed revision. A material revision requires renewed examination of affected claims; it cannot inherit a source-level frozen-claim verdict automatically. Removal, consolidation or no change may outperform an addition.
6. **Depreciation:** examine declining marginal usefulness of existing mechanisms as well as new proposals. Test actual current consumers, dependencies, alternative capabilities, operational and recovery requirements, cost and preserved function. Inactivity, overlapping names, historical source, aggregate traffic or absent records alone do not prove disuse or substitutability. Preserve artifacts for investigation without implying they are safe to execute. A recommendation to retire is not permission to delete, disable, archive or migrate.
7. **Communication:** use an existing authorized shared record, exact event references and bounded active-turn reads. If a turn ends or a transport fails, record the current proposition, outstanding attack, last received response and authorized next speaker. Resume from that frontier. No claim of automatic wakeup, continuous waiting after the turn ends, or background operation without actual capability. Keep private case contents out of public records.
8. **Convergence:** complete the initial circuit with real contributions; continue only for unresolved material attacks or a new evidence-bearing improvement. Ask for explicit dispositions, retain dissent and distinguish incomplete examination from convergence. Stop when further work is not justified. Do not add more infrastructure or mandatory rounds just to keep the proceeding busy.

A facilitated determination is SUSTAIN, REFINE or WITHDRAW, with reasons, unresolved limits and the smallest useful next action (which may be none). An authorized reopening starts a new scoped phase while preserving prior decisions. The existing executable SUSTAIN gate and its exact three-lens peer-exchange requirements remain unchanged; a facilitated multi-seat determination is not a claim that those code-level gates ran. Separate actual peer receipts from independently authenticated model or host execution. Recommendations grant no operational authority.

