"""Dependency-free, deliberately strict T'Kal-in-ket case state.

An evidence record is not a verified fact. A review is not independent merely
because its role differs. External execution receipts belong to integrations.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

LENSES = ("purist_logic", "pragmatism", "bridge")
STATES = ("OPEN", "CROSS_EXAMINATION", "CLOSED", "WITHDRAWN")
VERDICTS = ("SUSTAIN", "REFINE", "WITHDRAW")


class ProtocolError(ValueError):
    pass


@dataclass(frozen=True)
class Evidence:
    identifier: str
    claim: str
    source: str
    method: str
    reliability: str
    uncertainty: str


@dataclass(frozen=True)
class Review:
    lens: str
    reviewer_id: str
    finding: str
    objection: str
    execution_ref: Optional[str] = None


@dataclass
class Challenge:
    identifier: str
    lens: str
    target: str
    question: str
    status: str = "OPEN"
    defense: Optional[str] = None


@dataclass
class Case:
    case_id: str
    hypothesis: str
    falsifier: str
    proposer: str
    definitions: Dict[str, str] = field(default_factory=dict)
    evidence: List[Evidence] = field(default_factory=list)
    reviews: Dict[str, Review] = field(default_factory=dict)
    challenges: List[Challenge] = field(default_factory=list)
    state: str = "OPEN"
    verdict: Optional[str] = None
    rationale: Optional[str] = None

    def __post_init__(self):
        if not all((self.case_id.strip(), self.hypothesis.strip(),
                    self.falsifier.strip(), self.proposer.strip())):
            raise ProtocolError("case_id, hypothesis, falsifier and proposer are mandatory")

    def _mutable(self):
        if self.state in ("CLOSED", "WITHDRAWN"):
            raise ProtocolError("case is terminal")

    def add_evidence(self, item: Evidence):
        self._mutable()
        if not all((item.identifier, item.claim, item.source, item.method,
                    item.reliability, item.uncertainty)):
            raise ProtocolError("evidence provenance and uncertainty required")
        if any(e.identifier == item.identifier for e in self.evidence):
            raise ProtocolError("duplicate evidence ID")
        self.evidence.append(item)

    def add_review(self, review: Review):
        self._mutable()
        if review.lens not in LENSES:
            raise ProtocolError("unknown peer lens")
        if not all((review.reviewer_id.strip(), review.finding.strip(),
                    review.objection.strip())):
            raise ProtocolError("reviewer identity, finding and objection required")
        if review.lens in self.reviews:
            raise ProtocolError("lens already reviewed; revisions require a new case version")
        self.reviews[review.lens] = review

    def ask(self, challenge: Challenge):
        self._mutable()
        if challenge.lens not in LENSES:
            raise ProtocolError("unknown challenge lens")
        if not all((challenge.identifier.strip(), challenge.target.strip(),
                    challenge.question.strip())):
            raise ProtocolError("challenge needs ID, target and question")
        if challenge.status != "OPEN" or challenge.defense is not None:
            raise ProtocolError("challenges must start unanswered")
        if any(c.status in ("OPEN", "PARTLY_ANSWERED", "UNRESOLVED")
               for c in self.challenges):
            raise ProtocolError("only one unanswered challenge permitted")
        if any(c.identifier == challenge.identifier for c in self.challenges):
            raise ProtocolError("duplicate challenge ID")
        self.challenges.append(challenge)
        self.state = "CROSS_EXAMINATION"

    def resolve(self, identifier: str, status: str, defense: Optional[str] = None):
        self._mutable()
        if status not in ("ANSWERED", "PARTLY_ANSWERED", "CONCEDED",
                          "SKIPPED", "WAIVED", "UNRESOLVED"):
            raise ProtocolError("invalid resolution")
        match = next((c for c in self.challenges if c.identifier == identifier), None)
        if match is None or match.status not in ("OPEN", "PARTLY_ANSWERED", "UNRESOLVED"):
            raise ProtocolError("challenge absent or already finally resolved")
        if status in ("ANSWERED", "PARTLY_ANSWERED", "CONCEDED") and not defense:
            raise ProtocolError("record defense/concession")
        match.status, match.defense = status, defense

    def determine(self, verdict: str, rationale: str):
        self._mutable()
        if verdict not in ("SUSTAIN", "REFINE") or not rationale.strip():
            raise ProtocolError("chair may only SUSTAIN or REFINE; proposer withdraws explicitly")
        if set(self.reviews) != set(LENSES):
            raise ProtocolError("three peer lenses required")
        if any(c.status in ("OPEN", "UNRESOLVED", "PARTLY_ANSWERED")
               for c in self.challenges):
            raise ProtocolError("unresolved cross-examination")
        self.verdict, self.rationale, self.state = verdict, rationale, "CLOSED"

    def withdraw(self, reason: str):
        self._mutable()
        if not reason.strip():
            raise ProtocolError("withdrawal reason required")
        self.verdict, self.rationale, self.state = "WITHDRAW", reason, "WITHDRAWN"
