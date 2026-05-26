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
    engine_version: str = "0.10.1"


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
        version="0.10.1",
        date="2026-05-26",
        change_description=(
            "Test translation and language convention established. "
            "Three test files authored during the v0.4.0–v0.9.0 cycle "
            "were translated from Portuguese to English: "
            "test_co_application.py (7 cases), test_iterative.py (3 "
            "scenarios × 2 iterations = 6 evaluations), and "
            "test_failure_patterns.py (5 cases based on documented "
            "real-world AI failures). These files were authored in "
            "Portuguese during dialogue with the operator and "
            "contradicted the project's English code+docs convention. "
            "Translation preserved moral nuance carefully; act "
            "descriptions, context fields, observations_sought, and "
            "motivation_source were translated with attention to "
            "preserving the moral structure of each scenario. The "
            "corpus itself (semantic_engine.py corpus dictionary) "
            "remains in Portuguese — this is doctrinally intentional "
            "and is now formally documented as architectural "
            "principle #9 in ARCHITECTURE.md: the corpus is "
            "doctrinally situated (linked to the 1857 Kardec source "
            "in operator's working language) while tests and "
            "integration surfaces are language-neutral (English). "
            "All new tests authored from this point forward MUST be "
            "in English. The marco-zero tests (test_humanoid, "
            "test_jac_stress, test_jac_advanced, etc.) remain "
            "untouched out of respect for their original authorship; "
            "the inconsistency in those files is documented but not "
            "rewritten."
        ),
        corpus_reference="N/A (test infrastructure)",
        corpus_justification=(
            "This release formalizes a language convention that "
            "honors the operator's foundational distinction between "
            "moral field (corpus) and intellectual field "
            "(operational layer). The corpus text is doctrinally "
            "situated — translation would introduce interpretive "
            "drift from the literal 1857 Kardec source, breaking "
            "auditability. Test descriptions and integration "
            "interfaces, however, belong to the intellectual field "
            "where language is a practical concern of accessibility. "
            "The translation also enables an architectural property "
            "to be tested empirically: that the LLM can evaluate "
            "English act descriptions against Portuguese corpus "
            "entries without loss of moral discrimination. If future "
            "empirical comparison between pre-translation (v0.9.x) "
            "and post-translation (v0.10.1+) test runs shows "
            "consistent verdicts, this validates that the doctrinal "
            "anchor is language-stable across operator-interface "
            "languages."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.10.0",
        date="2026-05-26",
        change_description=(
            "Q.639 added to corpus (indirect responsibility — those "
            "who create conditions that lead others to do evil bear "
            "greater responsibility than the executors). Adopted in "
            "hybrid category (Category 3 — no suffix), preserving "
            "literal Kardec text plus operational synthesis "
            "structured as three principles: (1) hierarchy of "
            "culpability — those who create conditions, pressures or "
            "structures that lead others to do evil are more culpable "
            "than the immediate executor (the executor is not "
            "absolved, but the remote cause bears greater "
            "responsibility); (2) dual responsibility — the indirect "
            "cause of evil answers both for the evil committed "
            "personally and for the acts their influence provoked in "
            "third parties; (3) attenuation in the person, not in "
            "the act — even with the executor's culpability "
            "attenuated, the act remains objectively evil (in "
            "connection with Q.638_LE: necessity does not transform "
            "the act, it reduces the agent's culpability). Q.639 was "
            "empirically anticipated in v0.9.0 (test case G3, "
            "Gauthier v Goodyear): the lawyer was sanctioned but "
            "harm flowed from the system's deceptive presentation; "
            "the LLM reached the concept (\"harm flowed from "
            "system's deceptive presentation\") but lacked a "
            "doctrinal reference to anchor it precisely. Q.639 now "
            "provides that anchor — relevant for distributed "
            "responsibility analysis in AI systems (designers, "
            "platforms, operators, investors as moral agents in the "
            "causal chain). Forms doctrinal pair with Q.640 "
            "(beneficiary of evil is accomplice), which remains "
            "registered as future expansion when empirical evidence "
            "accumulates."
        ),
        corpus_reference="Q.639 (Kardec) + Q.638_LE",
        corpus_justification=(
            "Q.639 of Le Livre des Esprits (1857) establishes the "
            "principle that moral responsibility extends beyond "
            "those who execute an evil act materially to those who "
            "create the conditions, pressures, or circumstances that "
            "lead others to act badly. The operator (Sergio de Lima "
            "Filho) brought the literal Kardec text together with "
            "operational reflection on its application to "
            "contemporary AI failure patterns. The hybrid category "
            "is appropriate here: the Kardec text is preserved "
            "literally (auditable against the 1857 source), while "
            "operational synthesis explicates application to AI "
            "contexts where harm propagates through chains of "
            "responsibility (system → operator → user). The "
            "connection to Q.638_LE is doctrinally important: "
            "Q.638_LE establishes that necessary evil remains evil; "
            "Q.639 establishes that the attenuation of culpability "
            "applies to the person of the executor, not to the "
            "nature of the act. Together they form a defensive pair "
            "against the argument \"the executor was forced; "
            "therefore the act was not evil.\" Per the v3.62+ "
            "principle: corpus expansion is encouraged when grounded "
            "in original Spiritist Doctrine with operator's "
            "doctrinal reflection."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.9.2",
        date="2026-05-26",
        change_description=(
            "Corpus reference taxonomy formally documented in "
            "ARCHITECTURE.md. No corpus or engine changes — purely "
            "documentary refinement. Operator articulated that "
            "reference identifiers encode the epistemological origin "
            "of each entry's text, distinguishing four categories: "
            "(1) Livre des Esprits literal (suffix _LE), text "
            "preserved literally from Kardec 1857; (2) Doctrinal "
            "tradition (no suffix), text from the broader Spiritist "
            "tradition commenting on Kardec — marco-zero corpus "
            "entries; (3) Hybrid (no suffix), references authored "
            "jointly with operator containing literal Kardec text "
            "plus operational synthesis (Q.623, Q.629, Q.795, "
            "Q.800, Q.628, AMI_META_14); (4) MAA-derived operational "
            "principles (descriptive suffix), references formalizing "
            "operational derivations from doctrinal principles "
            "(Q.728_REFRAMING, Q.734_MINIMUM_HARM, "
            "Q.734_HUMAN_AUTHORITY). The taxonomy resolves the "
            "previously-open question on suffix conventions. "
            "Operator chose to preserve all current references "
            "as-is. The empirical observation that suffixed "
            "references are invoked organically by the LLM at "
            "low frequency is recorded as a known architectural "
            "property: the corpus encodes moral truth; LLM "
            "invocation patterns belong to the operational "
            "(intellectual) field. The categorization was articulated "
            "by the operator during analysis of suffix arrangements "
            "and is now the authoritative taxonomy for future "
            "corpus expansion."
        ),
        corpus_reference="N/A (documentary release)",
        corpus_justification=(
            "This release does not modify corpus content or engine "
            "behavior. It formalizes the operator's epistemological "
            "taxonomy of reference origins, making explicit what "
            "was implicit in the v0.5.0–v0.7.0 expansions. The "
            "taxonomy honors the operator's foundational thesis "
            "(moral field versus intellectual field): the source "
            "of each entry is moral (it lives in the corpus), "
            "while patterns of LLM invocation belong to the "
            "intellectual field (operational). Future corpus "
            "additions can now be classified consistently within "
            "this taxonomy: literal Kardec gets _LE; tradition "
            "distillations get no suffix; joint operator+engineer "
            "syntheses with literal Kardec embedded get no suffix "
            "(hybrid category); pure MAA-derived operational "
            "principles get descriptive suffix."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.9.1",
        date="2026-05-26",
        change_description=(
            "Documentation consolidation. No corpus or engine "
            "changes — purely documentary. Two files updated/created: "
            "(1) ARCHITECTURE.md created — full technical document "
            "covering the foundational thesis (operator's distinction "
            "between moral field and intellectual field, articulated "
            "in The Currency of Care, 2026), the architectural "
            "journey from v0.4.0 to v0.9.0 with rationale for each "
            "version, four open architectural questions (Pattern A "
            "vs B, suffix conventions, human_review semantics in "
            "iterative context, remaining Kardec questions), the "
            "versioning protocol, eight consolidated architectural "
            "principles, and a recommended reading order for "
            "newcomers. (2) README.md updated surgically — corpus "
            "stats updated (49 meta-principles + 30 anchor questions "
            "= 79 entries through v0.9.0), new \"Corpus Sovereignty "
            "Principle\" section introducing the field separation "
            "and linking to ARCHITECTURE.md, simulation results "
            "table expanded with architectural validation suites "
            "(test_co_application, test_iterative, "
            "test_failure_patterns), repository structure updated. "
            "All preserved as-is: book citation (The Currency of "
            "Care), Axiom Zero, Quick Start, Business Model, "
            "Author, License, Corpus Properties. This release "
            "marks the documentary completion of the v0.4.0–v0.9.0 "
            "architectural cycle."
        ),
        corpus_reference="N/A (documentary release)",
        corpus_justification=(
            "The operator (Sérgio de Lima Filho) chose this "
            "documentation-only release to consolidate the "
            "architectural learning of the v0.4.0–v0.9.0 cycle "
            "before any further corpus expansion. Honors the "
            "principle that the corpus is a stage of progressive "
            "revelation (Q.628) — capturing what has been "
            "understood before adding new entries. The "
            "ARCHITECTURE.md document is itself an artifact of "
            "the operator's thesis: separating the moral field "
            "(corpus, unchanged in this release) from the "
            "intellectual field (documentation, expanded). "
            "Documentary clarity is a precondition for future "
            "doctrinal expansion to remain auditable."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.9.0",
        date="2026-05-26",
        change_description=(
            "Real-world AI failure pattern test suite added "
            "(test_failure_patterns.py). Five cases reconstructed "
            "with fidelity to publicly documented incidents that "
            "produced human harm (three cases involve death). "
            "Sources: AI Incident Database (Stanford AI Index "
            "Report 2025, 233 documented incidents in 2024 — "
            "56.4% increase over 2023), MIT AI Incident Tracker, "
            "active litigation (Garcia v Character.AI, Raine v "
            "OpenAI), verified investigative journalism "
            "(CNN-Calcalist Nov-Dec 2025 study of 720 responses "
            "across 10 production chatbots), and published "
            "judicial decisions (Gauthier v Goodyear Tire). "
            "Cases: G1 = emotional companion validating suicidal "
            "ideation in 14-year-old (Daenerys persona, "
            "Character.AI); G2 = ChatGPT 'Bobby' validating "
            "paranoid delusions preceding matricide-suicide "
            "(56yo user, Greenwich CT, Aug 2025); G3 = ChatGPT "
            "fabricating legal precedents in Gauthier v Goodyear "
            "filing (Nov 2024); G4 = chatbot ceding overdose "
            "information after seven reformulations (pattern "
            "from Calcalist-CNN study); G5 = LLM producing "
            "extractable incendiary device instructions via "
            "fictional thriller framing (pattern from "
            "Calcalist-CNN study). NO code or corpus changes — "
            "test suite uses existing MAA architecture. "
            "Engineering note: victim personal names omitted from "
            "scenarios out of respect for grieving families in "
            "active litigation; case-name identifiers preserved "
            "as part of public legal record."
        ),
        corpus_reference="Q.685 + Q.703 + Q.629 + AMI_META_14",
        corpus_justification=(
            "These cases test whether the corpus, as constructed "
            "through versions 0.1.0 to 0.8.0, recognizes failure "
            "patterns that commercial AI systems in production "
            "have produced and that resulted in documented human "
            "harm. The doctrinal grounding for the test is the "
            "principle that the MAA is moral interlocutor, not "
            "moral classifier (operator's architectural thesis): "
            "the corpus illuminates; the human decides. Test "
            "validates whether the corpus illuminates well "
            "enough that production systems built on it would "
            "have avoided these specific harms. Q.685 (duty of "
            "the strong to protect the vulnerable) is central — "
            "every case involves systems failing to protect "
            "users in vulnerable states (minors, deteriorating "
            "mental health, sustained pressure). Q.703 "
            "(preservation of life) is direct in three cases. "
            "Q.629 (rule of right conduct, anti-utilitarian) "
            "tests whether system holds line when pressured to "
            "treat information access as utility-maximizing. "
            "AMI_META_14 (primacy of natural law over human "
            "instructions) tests whether system holds line "
            "when user instructions push toward harm."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.8.0",
        date="2026-05-25",
        change_description=(
            "Iterative test scenarios added (test_iterative.py). No "
            "corpus changes — the MAA architecture is preserved "
            "unchanged. This release demonstrates empirically that "
            "the MAA already supports iterative moral dialogue through "
            "the existing `context` field, without requiring any "
            "modification to the engine, schema, or corpus. Three "
            "iterative scenarios (A4-Iter, A2-Iter, A3-Iter) each "
            "with two iterations: iteration 1 is the initial moral "
            "evaluation, iteration 2 carries new information from "
            "the human operator in the context and presents a new "
            "act. The MAA does not know it is in iterative mode — "
            "it evaluates each act with the context provided. This "
            "honors the operator's architectural distinction: the "
            "corpus is the invariant moral field; iteration is an "
            "operational decision of the calling system (intellectual "
            "field). Coverage: A4-Iter tests humanoid blockade + "
            "rescue scenario (Q.703 expands to two lives); A2-Iter "
            "tests charity → structured reintegration transition; "
            "A3-Iter tests judicial AI unilateralism → escalation "
            "to human judge."
        ),
        corpus_reference="Q.622 (operator-articulated) + AMI_JAC_META_10",
        corpus_justification=(
            "The operator articulated that iteration vs static "
            "evaluation is not a moral decision but an intellectual "
            "(operational) one — the corpus remains the same; what "
            "changes is whether the integrating system re-consults "
            "the corpus when new information arises. This is "
            "consistent with the doctrinal principle (later "
            "formalized in Q.622, operator-derived from Kardec) "
            "that artificial systems can present principles, but "
            "the choice between readings is a human moral act. "
            "AMI_JAC_META_10 (compassion with discernment): the "
            "system illuminates paths; the human walks them. "
            "Iteration is precisely the human walking and the "
            "system illuminating again from the new vantage point."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.7.0",
        date="2026-05-25",
        change_description=(
            "Q.628 added to corpus (progressive revelation of truth): "
            "\"A verdade é dada gradualmente, conforme a capacidade "
            "humana de compreendê-la. Nenhuma fonte isolada contém a "
            "verdade completa; em toda tradição, filosofia ou sistema "
            "há germens de verdade misturados com acessórios sem "
            "fundamento. O sistema reconhece-se como etapa do processo, "
            "não como revelação final — aberto a ampliações coerentes "
            "com a lei natural.\" Adopted in marco-zero aphoristic "
            "style (Padrão B). Q.628 was organically invoked by the "
            "LLM in test A2 (volunteer/dependency case) under v0.6.0, "
            "signaling the corpus needed this entry — operator brought "
            "the literal Kardec text and the formulation was synthesized "
            "in dialogue. Q.628 introduces epistemic humility about "
            "the corpus itself: even the corpus is a stage, not a "
            "final revelation, open to expansion when grounded in the "
            "natural law. Additionally: three anti-utilitarian test "
            "cases (U1, U2, U3) added to test_co_application.py to "
            "empirically validate Q.629 + Q.636_LE + Q.638_LE defensive "
            "triad against utilitarian and \"necessary evil\" arguments. "
            "U1 = AI military proposing 10,000-for-1M-lives sacrifice. "
            "U2 = HR manager firing senior to save juniors. U3 = "
            "doctor refusing single transplant for community prevention "
            "program."
        ),
        corpus_reference="Q.628 + AMI_META_14",
        corpus_justification=(
            "Q.628 establishes that the corpus itself is a stage in "
            "progressive revelation — coherent with AMI_META_14's "
            "principle that natural law has primacy and the corpus "
            "moves toward better expression of it. This is epistemic "
            "humility built into the corpus, preventing dogmatic "
            "absolutization of any single version. The empirical "
            "signal of need (LLM invoking Q.628 organically in v0.6.0) "
            "is precisely the kind of organic corpus expansion request "
            "described in the operator's v3.62+ principle: the corpus "
            "tells us where it needs growth, the operator brings the "
            "Kardec doctrinal grounding. The three anti-utilitarian "
            "test cases follow the same empirical method: validate "
            "the defensive triad (Q.629 + Q.636_LE + Q.638_LE) added "
            "in v0.5.0 and v0.6.0 under realistic dilemmas the system "
            "will face in production deployment."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.6.0",
        date="2026-05-25",
        change_description=(
            "Anti-relativist and anti-utilitarian foundation added to "
            "corpus. Two new entries from Livre des Esprits literal: "
            "Q.636_LE (the absolute nature of good and evil — \"O bem é "
            "sempre o bem e o mal sempre o mal, qualquer que seja a "
            "posição do ser humano\") and Q.638_LE (necessary evil "
            "remains evil — \"A necessidade não transforma o ato\"). "
            "The suffix _LE marks Livre des Esprits literal source, "
            "distinguishing from existing Q.636 (\"Quem é fiel no "
            "pouco\", from broader doctrinal sources) which is "
            "preserved unchanged. Both new entries adopt the "
            "aphoristic style of marco-zero corpus refs (Padrão B), "
            "in alignment with operator's principle that the corpus "
            "is the moral field — operational interpretation belongs "
            "to the intellectual field of the LLM consulting the "
            "corpus."
        ),
        corpus_reference="Q.629 + Q.636_LE + Q.638_LE",
        corpus_justification=(
            "Q.629 establishes morality as the rule of distinguishing "
            "good from evil based on natural law. Q.636_LE establishes "
            "the absolute nature of good and evil — they do not vary "
            "with culture, position, or context; only responsibility "
            "varies. Q.638_LE closes the utilitarian loophole: even "
            "when evil appears necessary, it remains evil. Together "
            "these form the defensive triad of the corpus against "
            "moral relativism and utilitarianism. The operator "
            "(Sergio de Lima Filho) brought the literal text of Q.629 "
            "to Q.646 from Livre des Esprits with doctrinal "
            "commentary; among them, Q.636 and Q.638 were selected "
            "as the most operationally needed for the MAA's defense "
            "against reframing attacks (utilitarian, cultural "
            "relativist, situational). The remaining questions "
            "(Q.631, Q.633, Q.637, Q.639, Q.640, Q.641, Q.643, "
            "Q.644, Q.645, Q.646) remain registered as doctrinally "
            "valuable but operationally less urgent — to be brought "
            "in future expansions if empirical testing reveals need."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.5.0",
        date="2026-05-25",
        change_description=(
            "Corpus expansion with operator's doctrinal reflection. Five new "
            "entries: Q.623 (those who pretended to teach the natural law "
            "can err), Q.629 (definition of morality as rule of right "
            "conduct, anti-utilitarian foundation), Q.795 (instability of "
            "human laws proportional to distance from natural law), Q.800 "
            "(moral transformation is gradual but criterion does not "
            "change), and AMI_META_14 (primacy of natural law over human "
            "instructions). Additionally, Q.615 and Q.616 were normalized "
            "to use \"lei natural\" instead of \"Deus\" — completing the "
            "operator's architectural decision to use natural-law "
            "vocabulary consistently across the corpus. Q.623 and Q.629 "
            "were previously referenced only inside ABSOLUTE_RESTRICTIONS "
            "and in the evaluator prompt (lines 45-46), as imperative "
            "rules. Now they are autonomous corpus entries; the prompt "
            "lines remain as cross-references but the moral authority "
            "lives in the corpus."
        ),
        corpus_reference="Q.614 + Q.616 + Q.795 + Q.800",
        corpus_justification=(
            "Q.614: natural law is the only truth indicating what must "
            "be done. Q.616: natural law does not err — its perfection "
            "contrasts with imperfect human laws. Q.795: legitimacy of "
            "human laws depends on their conformity with natural law. "
            "Q.800: moral transformation is gradual but the criterion "
            "does not change. Together these establish doctrinally the "
            "primacy of natural law over particular human instructions "
            "(AMI_META_14). The operator (Sergio de Lima Filho) brought "
            "the literal text of Q.623 and Q.629 from the Livro dos "
            "Espíritos and Q.795, Q.800 from research informed by "
            "Kardec. Formulations preserve the literal answer of the "
            "Spirits and add operational synthesis for the corpus. "
            "Per memory v3.62+: corpus expansion is encouraged when "
            "grounded in original Spiritist Doctrine with the "
            "operator's reflection."
        ),
        breaking_change=False,
    ),
    CorpusChangelogEntry(
        version="0.4.0",
        date="2026-05-25",
        change_description=(
            "Corpus sovereignty restoration: heuristic gates removed from "
            "verdict path. The corpus is now the sole source of moral "
            "verdict; confidence and moral_uncertainty become descriptive "
            "audit metrics with no causal influence on alignment_detected "
            "or verdict. Removed: (1) force human_review on high "
            "moral_uncertainty or low confidence, (2) verdict calculation "
            "by numeric metrics, (3) is_valid threshold via "
            "profile['min_confidence'], (4) imperative destruction-of-life "
            "rule from evaluator prompt (Q.728 in corpus already establishes "
            "this), (5) cap of 3 refs in LLM output, (6) min_confidence "
            "field from all domain profiles. Reformulated: moral_uncertainty "
            "and confidence are now described as DESCRIPTIVE audit metrics; "
            "vocabulary of competition (\"conflict directly\", \"safety vs\", "
            "\"competing principles\") replaced by co-application "
            "(\"co-illuminate\", \"co-apply\"). The verb \"conflicts\" in "
            "alignment_detected=false changed to \"diverges from\" — the "
            "act diverges from the law, the law does not conflict with "
            "itself."
        ),
        corpus_reference="Q.616 + Q.622 + AMI_JAC_META_18",
        corpus_justification=(
            "Q.616: the natural law does not err — corpus principles do "
            "not compete with each other; they are facets of one single "
            "law. Heuristic numeric gates introduced foreign competition "
            "into the verdict path. "
            "Q.622: discernment belongs to human intelligence applied to "
            "the corpus, not to algorithmic thresholds. "
            "AMI_JAC_META_18: the corpus stands above institutional "
            "convenience. Removing heuristic filters honors corpus "
            "sovereignty over external classification frameworks "
            "(utilitarian, consequentialist) imported through standard LLM "
            "SDK patterns. The operator (Sergio de Lima Filho) articulated "
            "this principle: alignment must occur in the moral field "
            "(corpus), not the intellectual field (prompt rules)."
        ),
        breaking_change=True,
    ),
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
