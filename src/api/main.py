"""
AMI — API REST Universal
Interface para qualquer sistema de IA que queira integrar o Protocolo 1019.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.core.models import (
    MoralLaw,
    MoralValidationRequest,
    MoralValidationResult,
    CORPUS_METADATA,
    AXIOM_ZERO,
    CORPUS_CHANGELOG,
)
from src.protocol1019.engine import (
    MoralValidationEngine,
    MORAL_LAWS_REGISTRY,
)

engine = MoralValidationEngine()

app = FastAPI(
    title="AMI — Arquitetura Moral para IA",
    description=(
        "Protocolo 1019 — bússola moral universal para sistemas de IA embarcada. "
        "Independente de aplicação. "
        "Baseado em O Livro dos Espíritos, Allan Kardec, 1857."
    ),
    version="0.1.0",
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
        "system": "AMI — Arquitetura Moral para IA",
        "version": "0.1.0",
        "status": "online",
        "axiom_zero": AXIOM_ZERO.strip(),
        "corpus": CORPUS_METADATA,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
