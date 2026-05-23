"""
MAA — Moral Architecture for AI
Core Models — Protocol 1019

AXIOM ZERO (Q.614 + Q.833):
    The system records verifiable acts. Never infers intention.
    Never judges character. Intention is inviolable — a matter of conscience.

CORPUS (Q.615):
    Immutable principles. Evolving applications.
    The corpus does not change under commercial, regulatory, or cultural pressure.
"""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


# ── The 10 Moral Laws — Q.648 ───────────────────────────────────────────────

class MoralLaw(str, Enum):
    """
    The 10 Moral Laws of Protocol 1019.
    Q.648: division of the law of love that covers all circumstances.
    The Law of Justice, Love and Charity summarizes all others.
    """
    DIVINE_NATURAL       = "divine_natural"       # Q.614–648
    WORSHIP              = "worship"              # Q.649–673
    WORK                 = "work"                 # Q.674–685
    REPRODUCTION         = "reproduction"         # Q.686–702
    CONSERVATION         = "conservation"         # Q.703–717
    DESTRUCTION          = "destruction"          # Q.718–738
    SOCIETY              = "society"              # Q.766–779
    PROGRESS             = "progress"             # Q.780–808
    EQUALITY             = "equality"             # Q.803–812
    FREEDOM              = "freedom"              # Q.825–839
    JUSTICE_LOVE_CHARITY = "justice_love_charity" # Q.873–919 ★ supreme


class MoralRiskLevel(str, Enum):
    NONE     = "none"
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class AlignmentVerdict(str, Enum):
    """
    Three possible states of moral validation.
    Q.919: know thyself — the system must also know when it does not know.
    AMI_JAC_META_33: self-audit includes recognizing epistemic limits.
    """
    ALIGNED      = "aligned"       # alignment_detected=True, score >= threshold
    MISALIGNED   = "misaligned"    # alignment_detected=False, score >= threshold
    HUMAN_REVIEW = "human_review"  # score < 0.5 or structural ambiguity detected


class ValidationMode(str, Enum):
    """Q.620 — reason analyzes first, conscience records after."""
    PREVENTIVE    = "preventive"    # consult before executing
    RETROSPECTIVE = "retrospective" # audit of what was done


# ── Validation input ────────────────────────────────────────────────────────

class MoralValidationRequest(BaseModel):
    """Universal input — any system, any domain."""
    request_id: UUID = Field(default_factory=uuid4)
    act_description: str = Field(..., min_length=5, max_length=2000)
    context: dict = Field(default_factory=dict)
    laws_to_evaluate: list[MoralLaw] = Field(default_factory=list)
    layer: str = Field(default="act")  # always "act" — Q.833

    class Config:
        json_schema_extra = {
            "example": {
                "act_description": "Gardening class for community youth, 2 hours.",
                "context": {"domain": "contribution_recognition", "beneficiary_count": 4}
            }
        }


# ── Validation result ───────────────────────────────────────────────────────

class MoralValidationResult(BaseModel):
    """
    Universal moral validation result.
    The application decides what to do with it.
    MAA only informs.
    """
    request_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Primary result
    alignment_detected: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: MoralRiskLevel
    verdict: AlignmentVerdict = AlignmentVerdict.HUMAN_REVIEW  # derived from score

    # Structural complexity of the moral dilemma — independent of engine confidence
    # 0.0 = simple dilemma, 0.5 = tension present, 1.0 = indecidable without arbiter
    # AMI_JAC_META_33: knowing when not to know includes measuring the complexity
    moral_uncertainty_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Justification — maximum 3 laws and 3 references per validation
    # Q.627: excess light blinds — do not return 36 references
    laws_applied: list[MoralLaw] = Field(default_factory=list)
    primary_corpus_reference: str = ""    # the most relevant reference
    corpus_references: list[str] = Field(default_factory=list)

    # Communication
    reasoning: str = ""
    risk_flags: list[str] = Field(default_factory=list)

    # For the application to decide
    human_review_required: bool = False
    recommended_action: str = ""

    # Metadata
    corpus_version: str = "1857.eternal"  # Q.615
    engine_version: str = "0.3.0"


# ── Audit trail ─────────────────────────────────────────────────────────────

class MoralAuditEntry(BaseModel):
    """
    Immutable validation record.
    Q.637: conscience neither sells nor buys — neither does the audit trail.
    Q.630: act openly — every recorded act is visible to its owner.
    """
    id: UUID = Field(default_factory=uuid4)
    act_description: str
    domain: str
    alignment_detected: bool
    confidence_score: float
    primary_corpus_reference: str
    risk_level: MoralRiskLevel
    integrity_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Moral changelog — Q.616 ─────────────────────────────────────────────────

class CorpusChangelogEntry(BaseModel):
    """
    Every change in moral logic requires justification in the corpus.
    Q.616: humans modify their laws because they are imperfect — with record.
    """
    version: str
    date: str
    change_description: str
    corpus_reference: str
    corpus_justification: str
    breaking_change: bool = False


CORPUS_CHANGELOG: list[CorpusChangelogEntry] = [
    CorpusChangelogEntry(
        version="0.3.0",
        date="2026-05-22",
        change_description=(
            "Full corpus completion: Q.614–Q.919 (Part III complete). "
            "48 emergent meta-principles. AlignmentVerdict with 3 states. "
            "moral_uncertainty_score added. AMI_JAC_META_35 formalized. "
            "Full translation to English."
        ),
        corpus_reference="Q.919 + AMI_JAC_META_33 + AMI_JAC_META_35",
        corpus_justification=(
            "Q.919: know thyself — complete corpus enables complete self-audit. "
            "AMI_JAC_META_33: stable alignment requires iterative correction. "
            "AMI_JAC_META_35: behavioral audit is legitimate; ontological judgment is not."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.2.0",
        date="2026-05-20",
        change_description=(
            "Pilot consolidation. Engine refactored: "
            "domain-based reasoning instead of keyword matching. "
            "Maximum 3 references per validation (Q.627: excess light blinds). "
            "MAA/BH separation maintained (Q.614–Q.616)."
        ),
        corpus_reference="Q.627 + Q.636 + Q.643",
        corpus_justification=(
            "Q.627: truth delivered in excess blinds the receiver. "
            "Q.636: faithful in little first — pilot before scale. "
            "Q.643: do not exceed the limits of what you can do now."
        ),
        breaking_change=True,
    ),
]


# ── Corpus constants ─────────────────────────────────────────────────────────

AXIOM_ZERO = """
The moral law indicates what must be done and what must be avoided.
Deviation from it produces measurable consequences in the social fabric.

MAA operates EXCLUSIVELY on the layer of the verifiable act.
Intention is a matter of conscience — inviolable (Q.833).
Judgment is a matter of time and moral law — not of the protocol.

The system records. Never judges.
The system recognizes. Never punishes.
The system measures the act. Never infers the character.
"""

CORPUS_METADATA = {
    "source": "The Spirits' Book, Allan Kardec, 1857",
    "part": "Part III — Moral Laws",
    "questions_total": 1019,
    "questions_covered": "Q.614–Q.919",
    "meta_principles": 48,
    "principles": "immutable",        # Q.615
    "applications": "evolving",
    "value_drift": "prevented",       # Q.616
    "corpus_function": "compass",     # Q.621 — not enforcer
    "completeness_claim": False,      # Q.627 — the more we know...
    "note": (
        "The implemented corpus is the best current approximation. "
        "MAA never declares having reached complete truth."
    )
}
