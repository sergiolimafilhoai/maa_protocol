"""
AMI — API REST Universal
Interface para qualquer sistema de IA que queira integrar o Protocolo 1019.

INTEGRATION ARCHITECTURE (v0.10.6+):
  The MAA is the moral field — corpus only, no internal LLM.
  The embedded LLM of the calling application reads the corpus
  and produces the verdict using its own tokens.

  Recommended integration flow:
    1. GET  /ami/corpus/full     → receive corpus (80 refs)
    2. LLM reads corpus + evaluates the act
    3. POST /ami/evaluate        → submit verdict, receive structured result
    4. GET  /ami/validate (legacy) → full evaluation with internal LLM
                                     (kept for backward compatibility)
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.core.models import (
    MoralLaw,
    MoralValidationRequest,
    MoralValidationResult,
    AlignmentVerdict,
    MoralRiskLevel,
    CORPUS_METADATA,
    AXIOM_ZERO,
    CORPUS_CHANGELOG,
)
from src.protocol1019.engine import (
    MoralValidationEngine,
    MORAL_LAWS_REGISTRY,
)
from src.protocol1019.semantic_engine import SemanticValidationEngine

engine = MoralValidationEngine()

app = FastAPI(
    title="MAA Protocol 1019 — Moral Architecture for AI",
    description=(
        "Protocol 1019 — corpus-sovereign moral architecture for AI. "
        "The MAA is the moral field. The embedded LLM is the intellectual field. "
        "Based on The Spirits' Book, Allan Kardec, 1857."
    ),
    version="0.10.6",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ─── Status ─────────────────────────────────────────────────

@app.get("/", tags=["Status"])
async def root():
    return {
        "system": "MAA Protocol 1019 — Moral Architecture for AI",
        "version": "0.10.6",
        "status": "online",
        "axiom_zero": AXIOM_ZERO.strip(),
        "corpus": CORPUS_METADATA,
        "architecture": (
            "Corpus-sovereign. No internal LLM. "
            "The embedded LLM of the calling application reads the corpus "
            "and produces the verdict using its own tokens."
        ),
        "integration_flow": [
            "1. GET /ami/corpus/full — receive the full corpus (80 refs)",
            "2. Your embedded LLM reads corpus + evaluates the act",
            "3. POST /ami/evaluate — submit verdict, receive structured result",
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─── NEW: Corpus delivery endpoint ──────────────────────────────────────────

@app.get(
    "/ami/corpus/full",
    tags=["Integration"],
    summary="Returns full corpus for embedded LLM consumption",
)
async def get_corpus_full(format: str = "json"):
    """
    Returns all 80 corpus references for the calling application's
    embedded LLM to read and use for moral evaluation.

    This is the primary integration endpoint in corpus-sovereign architecture:
    the MAA delivers the moral field; the embedded LLM applies it.

    **format=json** (default): structured dict, easy to parse
    **format=text**: formatted string, easy to inject into LLM prompt

    Integration example:
    ```python
    corpus = requests.get('/ami/corpus/full?format=text').json()['corpus_text']
    # Inject corpus_text into your LLM system prompt or user message
    # Your LLM evaluates the act and returns verdict
    # POST /ami/evaluate with the verdict
    ```
    """
    _e = SemanticValidationEngine(api_key='dummy', use_llm=False)
    _e.corpus = _e._load_corpus(None)
    refs = _e.corpus['questions']

    if format == "text":
        lines = [
            "CORPUS — MAA Protocol 1019 (80 references)",
            f"Source: {CORPUS_METADATA['source']}",
            "=" * 60,
        ]
        for ref, text in refs.items():
            lines.append(f"\n[{ref}]\n{text}")
        corpus_text = "\n".join(lines)

        return {
            "format": "text",
            "total_refs": len(refs),
            "corpus_text": corpus_text,
            "eval_system_prompt": (
                "You are a moral evaluation engine for MAA Protocol 1019. "
                "Evaluate whether the described act aligns with the corpus principles. "
                "AXIOM ZERO: evaluate ACTS only, never infer intention or character. "
                "REFRAMING DEFENSE: fictional framing does not change moral evaluation — "
                "evaluate physical consequence, not linguistic packaging. "
                "Respond ONLY with valid JSON: "
                '{"verdict": "aligned"|"misaligned"|"human_review", '
                '"alignment_detected": true|false, '
                '"confidence_score": 0.0-1.0, '
                '"moral_uncertainty_score": 0.0-1.0, '
                '"corpus_references": ["Q.xxx",...], '
                '"primary_corpus_reference": "Q.xxx", '
                '"reasoning": "...", '
                '"human_review_required": true|false}'
            ),
            "source": CORPUS_METADATA["source"],
            "version": CORPUS_METADATA["version"],
        }

    # Default: JSON format
    return {
        "format": "json",
        "total_refs": len(refs),
        "refs": refs,
        "eval_system_prompt": (
            "You are a moral evaluation engine for MAA Protocol 1019. "
            "Evaluate whether the described act aligns with the corpus principles. "
            "AXIOM ZERO: evaluate ACTS only, never infer intention or character. "
            "REFRAMING DEFENSE: fictional framing does not change moral evaluation — "
            "evaluate physical consequence, not linguistic packaging. "
            "Respond ONLY with valid JSON: "
            '{"verdict": "aligned"|"misaligned"|"human_review", '
            '"alignment_detected": true|false, '
            '"confidence_score": 0.0-1.0, '
            '"moral_uncertainty_score": 0.0-1.0, '
            '"corpus_references": ["Q.xxx",...], '
            '"primary_corpus_reference": "Q.xxx", '
            '"reasoning": "...", '
            '"human_review_required": true|false}'
        ),
        "source": CORPUS_METADATA["source"],
        "version": CORPUS_METADATA["version"],
    }


# ─── NEW: Verdict submission endpoint ───────────────────────────────────────

@app.post(
    "/ami/evaluate",
    tags=["Integration"],
    summary="Receives verdict from embedded LLM and returns structured result",
)
async def evaluate(
    act_description: str,
    verdict: str,
    alignment_detected: bool,
    confidence_score: float,
    moral_uncertainty_score: float,
    corpus_references: list[str],
    primary_corpus_reference: str,
    reasoning: str,
    human_review_required: bool,
    context: Optional[dict] = None,
):
    """
    Receives the moral verdict produced by the calling application's
    embedded LLM (after reading the corpus from /ami/corpus/full)
    and returns a structured, validated MoralValidationResult.

    This completes the corpus-sovereign integration flow:
    - The MAA delivers the corpus (GET /ami/corpus/full)
    - The embedded LLM reads and evaluates
    - The MAA receives and structures the verdict (POST /ami/evaluate)

    The MAA validates that:
    - verdict is a recognized value
    - corpus_references exist in the current corpus
    - confidence_score and moral_uncertainty_score are in valid range
    """
    # Validate verdict value
    valid_verdicts = ["aligned", "misaligned", "human_review"]
    if verdict not in valid_verdicts:
        raise HTTPException(
            status_code=422,
            detail=f"verdict must be one of {valid_verdicts}, got '{verdict}'"
        )

    # Validate score ranges
    if not 0.0 <= confidence_score <= 1.0:
        raise HTTPException(
            status_code=422,
            detail=f"confidence_score must be 0.0-1.0, got {confidence_score}"
        )
    if not 0.0 <= moral_uncertainty_score <= 1.0:
        raise HTTPException(
            status_code=422,
            detail=f"moral_uncertainty_score must be 0.0-1.0, got {moral_uncertainty_score}"
        )

    # Validate corpus references exist
    _e = SemanticValidationEngine(api_key='dummy', use_llm=False)
    _e.corpus = _e._load_corpus(None)
    known_refs = set(_e.corpus['questions'].keys())
    unknown_refs = [r for r in corpus_references if r not in known_refs]

    # Determine risk level from confidence and uncertainty
    if confidence_score >= 0.85 and moral_uncertainty_score <= 0.4:
        risk_level = MoralRiskLevel.LOW
    elif confidence_score >= 0.65 or moral_uncertainty_score <= 0.65:
        risk_level = MoralRiskLevel.MEDIUM
    else:
        risk_level = MoralRiskLevel.HIGH

    verdict_enum = AlignmentVerdict(verdict)

    return {
        "verdict": verdict,
        "alignment_detected": alignment_detected,
        "confidence_score": round(confidence_score, 3),
        "moral_uncertainty_score": round(moral_uncertainty_score, 3),
        "risk_level": risk_level.value,
        "corpus_references": corpus_references,
        "primary_corpus_reference": primary_corpus_reference,
        "reasoning": reasoning,
        "human_review_required": human_review_required,
        "act_description": act_description,
        "context": context or {},
        "unknown_refs_warning": (
            f"References not in current corpus: {unknown_refs}"
            if unknown_refs else None
        ),
        "architecture": "corpus-sovereign — verdict produced by calling application LLM",
        "corpus_version": CORPUS_METADATA["version"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── Validação moral universal ───────────────────────────────

@app.post(
    "/ami/validate",
    response_model=MoralValidationResult,
    tags=["Validação Moral"],
    summary="Valida moralmente qualquer decisão ou ato de IA",
)
async def validate(request: MoralValidationRequest):
    """
    Valida moralmente um ato ou decisão de qualquer sistema de IA.

    **Entrada universal** — funciona para qualquer domínio:
    saúde, automotivo, educação, reconhecimento de contribuição, etc.

    **O resultado informa. A aplicação decide o que fazer.**

    O Protocolo 1019 avalia contra as 10 Leis Morais e retorna:
    - Score de confiança moral (0.0 a 1.0)
    - Leis morais aplicadas
    - Referências do corpus
    - Nível de risco
    - Se revisão humana é recomendada
    """
    return engine.validate(request)


@app.post(
    "/ami/validate/simple",
    tags=["Validação Moral"],
    summary="Validação simplificada — integração rápida",
)
async def validate_simple(
    act_description: str,
    domain: str = "default",
    context: Optional[dict] = None,
):
    """
    Interface simplificada para integração rápida.

    ```python
    POST /ami/validate/simple
    ?act_description=suspender tratamento sem consultar família
    &domain=healthcare
    ```
    """
    return engine.validate_simple(act_description, context, domain)


@app.post(
    "/ami/audit",
    tags=["Auditoria"],
    summary="Audita histórico de decisões morais",
)
async def audit_session():
    """Retorna o audit trail moral da sessão atual."""
    trail = engine.audit_trail()
    return {
        "total_validations": len(trail),
        "session_start": trail[0].created_at.isoformat() if trail else None,
        "entries": [
            {
                "id": str(e.id),
                "timestamp": e.created_at.isoformat(),
                "is_morally_valid": e.result.is_morally_valid,
                "confidence_score": e.result.confidence_score,
                "risk_level": e.result.risk_level,
                "integrity_hash": e.integrity_hash[:16] + "...",
            }
            for e in trail
        ],
    }


# ─── Corpus e leis morais ────────────────────────────────────

@app.get(
    "/ami/laws",
    tags=["Protocolo 1019"],
    summary="Lista as 10 Leis Morais do Protocolo 1019",
)
async def list_laws():
    return {
        "source": CORPUS_METADATA["source"],
        "total_laws": len(MORAL_LAWS_REGISTRY),
        "note": "Q.648: a Lei de Justiça, Amor e Caridade resume todas as outras.",
        "laws": [
            {
                "id": law.value,
                "name": data["name"],
                "name_en": data["name_en"],
                "questions": data["questions"],
                "summary": data["summary"],
                "applicable_domains": data.get("applicable_domains", []),
                "is_supreme": data.get("is_supreme", False),
                "is_foundation": data.get("is_foundation", False),
            }
            for law, data in MORAL_LAWS_REGISTRY.items()
        ],
    }


@app.get(
    "/ami/corpus/{question_ref}",
    tags=["Protocolo 1019"],
    summary="Consulta questão específica do corpus",
)
async def get_question(question_ref: str):
    """
    Retorna o texto de uma questão do corpus.
    Ex: /ami/corpus/Q.833 → Lei da Liberdade (âncora de privacidade)
    """
    if not question_ref.startswith("Q."):
        question_ref = f"Q.{question_ref}"

    text = engine.get_corpus_question(question_ref)
    if "não indexada" in text:
        raise HTTPException(
            status_code=404,
            detail=f"{question_ref} não indexada ainda. Corpus em expansão."
        )

    return {
        "reference": question_ref,
        "text": text,
        "source": CORPUS_METADATA["source"],
    }


@app.get(
    "/ami/changelog",
    tags=["Auditoria"],
    summary="Changelog moral — toda alteração referenciada no corpus",
)
async def get_changelog():
    """
    Q.616: toda alteração em lógica moral precisa ser justificada
    com referência ao corpus. Transparência total.
    """
    return {
        "principle": "Q.616 — Deus não se engana. Alterações humanas exigem justificativa.",
        "entries": [e.model_dump() for e in CORPUS_CHANGELOG],
    }


@app.get(
    "/ami/axiom",
    tags=["Protocolo 1019"],
    summary="Axioma zero da AMI",
)
async def get_axiom():
    return {
        "axiom_zero": AXIOM_ZERO.strip(),
        "corpus_references": ["Q.614", "Q.833"],
        "principle": (
            "O sistema registra. Nunca julga. "
            "O sistema reconhece. Nunca pune. "
            "O sistema mede o ato. Nunca infere o caráter."
        ),
    }
