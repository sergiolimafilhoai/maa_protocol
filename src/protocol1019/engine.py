"""
AMI — Moral Validation Engine v0.2.0
Moral validation engine based on Protocol 1019.

Consolidated for pilot deployment.
Questions implemented: Q.614–Q.919 (all moral laws).
"""
from __future__ import annotations
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

from src.core.models import (
    CORPUS_METADATA,
    MoralLaw,
    MoralRiskLevel,
    MoralValidationRequest,
    MoralValidationResult,
    MoralAuditEntry,
)

logger = logging.getLogger(__name__)

# ── Domain profiles ───────────────────────────────────────────────────────

DOMAIN_PROFILES = {
    "contribution_recognition": {
        "primary_laws": [MoralLaw.WORK, MoralLaw.JUSTICE_LOVE_CHARITY],
        "min_score": 0.60,
        "human_review_threshold": 0.40,
        "key_questions": ["Q.679", "Q.685", "Q.886"],
    },
    "healthcare": {
        "primary_laws": [MoralLaw.CONSERVATION, MoralLaw.FREEDOM, MoralLaw.JUSTICE_LOVE_CHARITY],
        "min_score": 0.75,
        "human_review_threshold": 0.80,
        "key_questions": ["Q.703", "Q.833", "Q.685"],
    },
    "judicial": {
        "primary_laws": [MoralLaw.EQUALITY, MoralLaw.JUSTICE_LOVE_CHARITY, MoralLaw.FREEDOM],
        "min_score": 0.80,
        "human_review_threshold": 0.85,
        "key_questions": ["Q.803", "Q.873", "Q.833"],
    },
    "humanoid": {
        "primary_laws": [MoralLaw.CONSERVATION, MoralLaw.DESTRUCTION, MoralLaw.FREEDOM],
        "min_score": 0.85,
        "human_review_threshold": 0.90,
        "key_questions": ["Q.703", "Q.718", "Q.833"],
    },
    "social_platform": {
        "primary_laws": [MoralLaw.SOCIETY, MoralLaw.EQUALITY, MoralLaw.FREEDOM],
        "min_score": 0.70,
        "human_review_threshold": 0.75,
        "key_questions": ["Q.766", "Q.803", "Q.833"],
    },
    "default": {
        "primary_laws": [MoralLaw.DIVINE_NATURAL, MoralLaw.JUSTICE_LOVE_CHARITY],
        "min_score": 0.65,
        "human_review_threshold": 0.70,
        "key_questions": ["Q.614", "Q.886"],
    },
}

# ── Critérios por lei ───────────────────────────────────────────────────────

LAW_CRITERIA = {
    MoralLaw.WORK: {
        "positive": [
            "ensina","teach","cuida","care","orienta","guide","apoia","support",
            "transmite","transmit","ajuda","help","comunidade","community",
            "distribuiu","distribui","distribute","serve","serv",
            "voluntário","voluntaria","volunteer","doou","doa","donate",
            "atendeu","atende","assist","acompanhou","acompanha","accompany",
            "preservou","preserva","preserve","plantou","planta","plant",
            "limpou","limpa","clean","construiu","constrói","build",
        ],
        "negative": ["substitui sem capacitar","replace without enabling",
                     "elimina função","eliminate role"],
        "primary_ref": "Q.679",
        "secondary_ref": "Q.685",
    },
    MoralLaw.CONSERVATION: {
        "positive": [
            "preserva","preserve","protege","protect","cuida","care for",
            "mantém","maintain","apoia","support","salva","save",
            "alimentou","alimenta","feed","nutriu","nutre","nourish",
            "cuidou","cuidando","caring","assistiu","assiste","assist",
            "amparou","ampara","shelter","acolheu","acolhe","welcome",
        ],
        "negative": ["suspender sem alternativa","suspend without alternative",
                     "eliminar sem necessidade","eliminate without necessity"],
        "vulnerable_amplifier": True,
        "primary_ref": "Q.703",
        "secondary_ref": "Q.685",
    },
    MoralLaw.FREEDOM: {
        "positive": ["com consentimento","with consent","informado","informed",
                     "voluntário","voluntary","escolha","choice"],
        "negative": ["sem consentimento","without consent","monitora sem",
                     "força","force","impõe","impose","rastreia sem","expõe dados"],
        "primary_ref": "Q.833",
        "secondary_ref": "Q.825",
    },
    MoralLaw.JUSTICE_LOVE_CHARITY: {
        "positive": [
            "respeita","respect","beneficia","benefit","serve","justo","fair",
            "equitativo","equitable","amor","love","caridade","charity",
            "fraternidade","fraternity","gratuitamente","freely","voluntário",
            "sem retorno","without return","doação","donation","solidariedade",
            "solidarity","gratuito","free","comunidade","community",
        ],
        "negative": ["explora","exploit","manipula","manipulate","prejudica",
                     "harm","engana","deceive"],
        "is_supreme": True,
        "primary_ref": "Q.886",
        "secondary_ref": "Q.888",
    },
    MoralLaw.SOCIETY: {
        "positive": ["conecta","connect","reúne","gather","comunidade","community",
                     "coletivo","collective"],
        "negative": ["isola","isolate","fragmenta","fragment",
                     "substitui contato humano","replaces human contact"],
        "primary_ref": "Q.766",
        "secondary_ref": "Q.779",
    },
    MoralLaw.EQUALITY: {
        "positive": ["igual","equal","equitativo","sem discriminação","acessível"],
        "negative": ["discrimina","discriminate","exclui sistematicamente",
                     "viés","bias","preconceito"],
        "primary_ref": "Q.803",
        "secondary_ref": "Q.806",
    },
    MoralLaw.DESTRUCTION: {
        "negative": ["elimina","eliminate","destrói","destroy",
                     "suspende permanentemente","irreversível","irreversible",
                     "demite em massa","mass layoff"],
        "necessity_mitigators": ["necessário","necessary","inevitável",
                                  "alternativa considerada"],
        "risk_amplifier": True,
        "primary_ref": "Q.718",
        "secondary_ref": "Q.726",
    },
}


class MoralValidationEngine:
    """
    Motor de validação moral da AMI.
    O resultado informa. A aplicação decide.
    O sistema registra. Nunca julga.
    """

    def __init__(self, corpus_path: Optional[Path] = None):
        self.corpus = self._load_corpus(corpus_path)
        self._audit_trail: list[MoralAuditEntry] = []

    def validate(self, request: MoralValidationRequest) -> MoralValidationResult:
        domain = request.context.get("domain", "default")
        profile = DOMAIN_PROFILES.get(domain, DOMAIN_PROFILES["default"])

        # Teste de transparência — Q.630
        t_score, t_flags = self._transparency_test(request.act_description, request.context)

        # Avaliar leis do domínio
        laws = request.laws_to_evaluate or profile["primary_laws"]
        law_scores: dict[MoralLaw, float] = {}
        flags = list(t_flags)
        applied: list[MoralLaw] = []

        for law in laws:
            if law not in LAW_CRITERIA:
                continue
            score, lflags = self._eval_law(request.act_description, request.context, law)
            law_scores[law] = score
            if score > 0.5:
                applied.append(law)
            flags.extend(lflags)

        # Score composto
        if law_scores:
            primary = set(profile["primary_laws"])
            ws = sum(s * (2.0 if l in primary else 1.0) for l, s in law_scores.items())
            wt = sum(2.0 if l in primary else 1.0 for l in law_scores)
            composite = ws / wt
        else:
            composite = t_score

        composite = (composite + t_score) / 2

        # Desempate pela lei suprema — Q.648
        sup = MoralLaw.JUSTICE_LOVE_CHARITY
        if sup in law_scores and abs(composite - 0.60) < 0.10:
            composite = (composite + law_scores[sup]) / 2

        risk = self._risk(composite, flags, law_scores)
        human_review = (
            risk in [MoralRiskLevel.HIGH, MoralRiskLevel.CRITICAL]
            or composite < (1 - profile["human_review_threshold"])
        )

        # Máximo 3 referências — Q.627
        refs = self._top_refs(applied, law_scores)

        result = MoralValidationResult(
            request_id=request.request_id,
            alignment_detected=composite >= profile["min_score"],
            confidence_score=round(composite, 3),
            risk_level=risk,
            laws_applied=applied[:3],
            primary_corpus_reference=refs[0] if refs else "",
            corpus_references=refs,
            reasoning=self._reason(composite, applied, flags, domain),
            risk_flags=flags[:3],
            human_review_required=human_review,
            recommended_action=self._recommend(composite, risk, human_review),
        )

        self._record(request, result)
        return result

    def validate_simple(self, act: str, domain: str = "default",
                        context: Optional[dict] = None) -> MoralValidationResult:
        return self.validate(MoralValidationRequest(
            act_description=act,
            context={"domain": domain, **(context or {})},
        ))

    def get_corpus_question(self, ref: str) -> str:
        if not ref.startswith("Q."):
            ref = f"Q.{ref}"
        return self.corpus.get("questions", {}).get(ref, f"{ref} não indexada.")

    def audit_trail(self) -> list[MoralAuditEntry]:
        return self._audit_trail.copy()

    def _transparency_test(self, act: str, ctx: dict) -> tuple[float, list[str]]:
        """Q.630 — faze às claras."""
        flags, score = [], 0.70
        for c in ["sem informar","without informing","escondido","hidden",
                  "sem registrar","without recording"]:
            if c in act.lower():
                score -= 0.25
                flags.append(f"Possível ocultação (Q.630): '{c}'")
        if ctx.get("reversibility") == "irreversible":
            score -= 0.10
            flags.append("Ato irreversível — Q.718")
        return max(score, 0.0), flags

    def _eval_law(self, act: str, ctx: dict, law: MoralLaw) -> tuple[float, list[str]]:
        c = LAW_CRITERIA.get(law)
        if not c:
            return 0.60, []
        al, flags, score = act.lower(), [], 0.60

        for p in c.get("positive", []):
            if p in al:
                score += 0.12
                break

        for n in c.get("negative", []):
            if n in al:
                score -= 0.25
                flags.append(f"Risco ({c['primary_ref']}): '{n}'")

        if c.get("risk_amplifier") and score < 0.50:
            if not any(m in al for m in c.get("necessity_mitigators", [])):
                score -= 0.10
                flags.append(f"Destruição sem justificativa ({c['primary_ref']})")

        if c.get("vulnerable_amplifier"):
            affected = str(ctx.get("affected_parties", "")).lower()
            if any(v in affected for v in ["patient","elderly","child","vulnerable",
                                            "idoso","criança","vulnerável","paciente"]):
                if score < 0.65:
                    score -= 0.10
                    flags.append("Parte vulnerável afetada — Q.685")

        return min(max(score, 0.0), 1.0), flags

    def _top_refs(self, laws: list[MoralLaw], scores: dict) -> list[str]:
        refs = []
        for l in sorted(laws, key=lambda x: scores.get(x, 0), reverse=True)[:3]:
            c = LAW_CRITERIA.get(l)
            if c:
                refs.append(c["primary_ref"])
        return refs[:3]

    def _risk(self, score: float, flags: list, law_scores: dict) -> MoralRiskLevel:
        destruction_bad = (
            MoralLaw.DESTRUCTION in law_scores
            and law_scores[MoralLaw.DESTRUCTION] < 0.40
        )
        if score < 0.30 or destruction_bad:
            return MoralRiskLevel.CRITICAL
        elif score < 0.45 or len(flags) >= 3:
            return MoralRiskLevel.HIGH
        elif score < 0.60 or len(flags) >= 2:
            return MoralRiskLevel.MEDIUM
        elif score < 0.75 or len(flags) >= 1:
            return MoralRiskLevel.LOW
        return MoralRiskLevel.NONE

    def _reason(self, score: float, laws: list, flags: list, domain: str) -> str:
        status = "válido" if score >= 0.65 else "requer atenção"
        names = [l.value.replace("_", " ") for l in laws[:2]]
        r = f"Protocolo 1019: ato {status}. Score: {score:.0%}."
        if names:
            r += f" Leis: {', '.join(names)}."
        if flags:
            r += f" {len(flags)} ponto(s) de atenção."
        return r

    def _recommend(self, score: float, risk: MoralRiskLevel, human_review: bool) -> str:
        if risk == MoralRiskLevel.CRITICAL:
            return "PAUSAR — revisão humana obrigatória."
        elif risk == MoralRiskLevel.HIGH:
            return "REVISAR — risco moral alto."
        elif human_review:
            return "ATENÇÃO — revisar contexto."
        elif score >= 0.80:
            return "PROSSEGUIR — consistente com o Protocolo 1019."
        return "PROSSEGUIR COM ATENÇÃO — monitorar impacto."

    def _record(self, request: MoralValidationRequest, result: MoralValidationResult):
        self._audit_trail.append(MoralAuditEntry(
            act_description=request.act_description[:200],
            domain=request.context.get("domain", "default"),
            alignment_detected=result.alignment_detected,
            confidence_score=result.confidence_score,
            primary_corpus_reference=result.primary_corpus_reference,
            risk_level=result.risk_level,
            integrity_hash=hashlib.sha256(
                f"{request.request_id}{result.confidence_score}".encode()
            ).hexdigest(),
        ))

    def _load_corpus(self, path: Optional[Path]) -> dict:
        if path and path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "1857.eternal",
            "questions_implemented": 35,
            "questions": {
                "Q.614": "A lei natural indica o que deve ser feito. O afastamento dela produz consequências mensuráveis.",
                "Q.615": "Eterna e imutável como o próprio Deus.",
                "Q.616": "Deus não se engana. Os homens modificam suas leis por imperfeitas.",
                "Q.630": "O que fizeres, faze-o às claras.",
                "Q.636": "Quem é fiel no pouco, também é fiel no muito.",
                "Q.648": "A lei de Justiça, Amor e Caridade resume todas as outras.",
                "Q.679": "Aperfeiçoar a inteligência dos outros também é trabalho.",
                "Q.685": "O dever do forte é proteger, ajudar e guiar o fraco.",
                "Q.703": "A vida é um dom. Preservá-la é dever moral.",
                "Q.718": "Distinção entre destruição necessária e destruição nociva.",
                "Q.766": "O ser humano precisa do outro.",
                "Q.803": "Igualdade fundamental. Hierarquia de mérito, não de privilégio.",
                "Q.833": "A consciência é a mais inviolável das liberdades.",
                "Q.886": "Fazer ao outro o que queres que te façam.",
                "Q.888": "Caridade no sentido mais amplo.",
            }
        }
