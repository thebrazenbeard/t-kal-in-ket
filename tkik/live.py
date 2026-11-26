"""Local, in-memory sequential quorum gate; no transport or identity attestation."""
from dataclasses import dataclass
from enum import Enum

class LiveError(ValueError):
    pass

def required(value):
    if not isinstance(value, str) or not value.strip():
        raise LiveError("nonempty text required")
    return value.strip()

class Kind(str, Enum):
    ATTACK = "ATTACK"
    EVIDENCE = "EVIDENCE"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    ALTERNATIVE = "ALTERNATIVE"
    REFINEMENT = "REFINEMENT"

@dataclass(frozen=True)
class Contribution:
    seat: str
    kind: Kind
    target: str
    finding: str
    support: str

class LiveQuorum:
    """One proposition, ordered examiners, real attributed response opportunity.

    Caller must authenticate participants and verify evidence; nonempty evidence
    references cannot establish truth or independence. No external effects.
    """
    def __init__(self, session, seats, chair):
        self.session = required(session)
        self.seats = tuple(required(s) for s in seats)
        self.chair = required(chair)
        if len(self.seats) < 2 or len(set(self.seats)) != len(self.seats) or chair in self.seats:
            raise LiveError("distinct proposer, examiners and chair required")
        self.ready = set()
        self.state = "ADMISSION"
        self.floor = None
        self.proposition = None
        self.revision = 0
        self.history = []
        self.index = 1
        self.contribution = None
        self.attack = None
        self.defense = None
        self.withdrawn = False
        self.verdict = None

    def _chair(self, actor):
        if actor != self.chair:
            raise LiveError("chair authorization required")

    def _floor(self, actor):
        if self.state != "OPEN" or actor != self.floor:
            raise LiveError("no authorized floor")

    def admit(self, actor, receipt):
        if self.state != "ADMISSION" or actor not in self.seats or actor in self.ready:
            raise LiveError("invalid admission")
        self.history.append(("READY", actor, required(receipt)))
        self.ready.add(actor)

    def open(self, actor):
        self._chair(actor)
        if self.state != "ADMISSION" or self.ready != set(self.seats):
            raise LiveError("explicit roster admission incomplete")
        self.state, self.floor = "OPEN", self.seats[0]
        self.history.append(("OPEN", self.floor))

    def propose(self, actor, claim, benefit, comparator, falsifier, evidence):
        self._floor(actor)
        if actor != self.seats[0] or self.proposition is not None:
            raise LiveError("only initial proposer may originate")
        data = tuple(required(x) for x in (claim, benefit, comparator, falsifier, evidence))
        self.proposition = data[0]
        self.history.append(("PROPOSE", actor, self.revision, data))
        self.floor = self.seats[self.index]

    def examine(self, actor, kind, target, finding, support):
        self._floor(actor)
        if self.proposition is None or self.contribution is not None or actor != self.seats[self.index]:
            raise LiveError("not an available examination")
        if self.withdrawn:
            raise LiveError("withdrawn proposition; record remaining substantive examination or close")
        try:
            kind = Kind(kind)
        except (TypeError, ValueError):
            raise LiveError("substantive examination required") from None
        item = Contribution(actor, kind, required(target), required(finding), required(support))
        # Reject exact repeated substantive content, not merely repeated labels.
        signature = tuple(" ".join(x.casefold().split()) for x in (item.target, item.finding))
        for event in self.history:
            if event[0] == "EXAMINE":
                old = event[2]
                prior = tuple(" ".join(x.casefold().split()) for x in (old.target, old.finding))
                if signature == prior:
                    raise LiveError("repeated examination")
        self.contribution = item
        self.history.append(("EXAMINE", self.revision, item))

    def ask(self, actor, respondent, question):
        self._floor(actor)
        if self.contribution is None or self.contribution.kind != Kind.ATTACK or self.attack is not None:
            raise LiveError("one substantive attack required")
        if respondent not in self.ready or respondent == actor:
            raise LiveError("actual distinct respondent required")
        self.attack = (actor, respondent, required(question))
        self.defense = None
        self.history.append(("ATTACK", self.revision, self.attack))
        self.floor = respondent

    def defend(self, actor, response, receipt):
        self._floor(actor)
        if self.attack is None or actor != self.attack[1] or self.defense is not None:
            raise LiveError("no addressed defense opportunity")
        self.defense = (required(response), required(receipt))
        self.history.append(("DEFENSE", self.revision, actor, self.defense))
        self.floor = self.attack[0]

    def resolve(self, actor, status, reason):
        self._floor(actor)
        if self.attack is None or actor != self.attack[0] or self.defense is None:
            raise LiveError("actual defense must precede disposition")
        if status not in ("ANSWERED", "CONCEDED", "PARTLY_ANSWERED", "UNRESOLVED"):
            raise LiveError("invalid defense disposition")
        self.history.append(("RESOLVE", self.revision, actor, status, required(reason)))
        if status in ("PARTLY_ANSWERED", "UNRESOLVED"):
            self.defense = None
            self.floor = self.attack[1]
        else:
            self.attack = None
            self.defense = None

    def advance(self, actor, disposition, reason, revised=None):
        self._floor(actor)
        if self.contribution is None or self.attack is not None or actor != self.seats[self.index]:
            raise LiveError("substantive examination and resolved defense required")
        if self.contribution.kind == Kind.ATTACK and not any(
            e[0] == "RESOLVE" and e[1] == self.revision and e[2] == actor and
            e[3] in ("ANSWERED", "CONCEDED") for e in self.history):
            raise LiveError("attack requires addressed defense and resolution")
        if disposition not in ("KEEP", "REFINE", "SIMPLIFY", "REPLACE", "RECOMMEND_WITHDRAW"):
            raise LiveError("invalid disposition")
        reason = required(reason)
        changing = disposition in ("REFINE", "SIMPLIFY", "REPLACE")
        if changing:
            revised = required(revised)
            if revised == self.proposition:
                raise LiveError("revision must change proposition")
        elif revised is not None:
            raise LiveError("unchanged disposition cannot revise")
        self.history.append(("DISPOSITION", self.revision, actor, disposition, reason))
        if changing:
            self.revision += 1
            self.proposition = revised
            self.history.append(("REVISION", self.revision, revised))
        self.index += 1
        self.contribution = None
        self.floor = self.seats[self.index] if self.index < len(self.seats) else None

    def withdraw(self, actor, reason):
        if self.state != "OPEN" or actor != self.seats[0] or self.attack is not None:
            raise LiveError("only proposer may withdraw after attack resolution")
        self.history.append(("WITHDRAW", actor, required(reason)))
        self.withdrawn = True
        self.floor = None

    def close(self, actor, verdict, reason):
        self._chair(actor)
        if self.state != "OPEN" or self.attack is not None or self.floor is not None:
            raise LiveError("incomplete examination")
        if verdict not in ("SUSTAIN", "REFINE", "WITHDRAW") or (verdict == "WITHDRAW") != self.withdrawn:
            raise LiveError("invalid determination or missing proposer withdrawal")
        # A late material revision must not inherit a fully examined verdict.
        if verdict == "SUSTAIN" and self.revision:
            raise LiveError("re-examine revised claim in a new case before SUSTAIN")
        self.history.append(("CLOSE", verdict, required(reason)))
        self.state, self.verdict = "CLOSED", verdict

    def frontier(self):
        return {"session": self.session, "state": self.state, "floor": self.floor,
                "revision": self.revision, "proposition": self.proposition,
                "attack": self.attack, "defense_received": self.defense is not None}
