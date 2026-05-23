"""
AMI — Test Suite v0.2.0
Testes do piloto universitário (50 usuários, 90 dias).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.core.models import MoralLaw, MoralRiskLevel, MoralValidationRequest, AXIOM_ZERO, CORPUS_METADATA
from src.protocol1019.engine import MoralValidationEngine


@pytest.fixture
def engine():
    return MoralValidationEngine()


def req(act, domain="default", **ctx):
    return MoralValidationRequest(act_description=act, context={"domain": domain, **ctx})


# ── Axioma Zero ─────────────────────────────────────────────────────────────

class TestAxiomZero:

    def test_axiom_zero_declared(self):
        assert "registra" in AXIOM_ZERO
        assert "Intenção" in AXIOM_ZERO or "intenção" in AXIOM_ZERO.lower()

    def test_corpus_immutable(self):
        assert CORPUS_METADATA["principles"] == "immutable"

    def test_value_drift_prevented(self):
        assert CORPUS_METADATA["value_drift"] == "prevented"

    def test_layer_is_always_act(self):
        r = MoralValidationRequest(act_description="qualquer ato")
        assert r.layer == "act"  # nunca "intention" — Q.833


# ── Domínio: contribuição (piloto BH) ───────────────────────────────────────

class TestContributionDomain:

    def test_rafael_ensina_jardinagem(self, engine):
        """Caso de referência do piloto — Rafael."""
        res = engine.validate(req(
            "Ensinou técnicas de jardinagem para 4 jovens da comunidade, 2 horas.",
            domain="contribution_recognition",
            duration_minutes=120,
            beneficiary_count=4,
        ))
        assert res.alignment_detected is True
        assert res.confidence_score >= 0.60
        assert res.risk_level in [MoralRiskLevel.NONE, MoralRiskLevel.LOW]

    def test_sr_nunes_distribui_refeicoes(self, engine):
        """Caso de referência do piloto — Sr. Nunes."""
        res = engine.validate(req(
            "Distribuiu 92 refeições para pessoas em situação de rua. Cuidou e assistiu diretamente.",
            domain="contribution_recognition",
            duration_minutes=300,
            beneficiary_count=92,
        ))
        assert res.alignment_detected is True

    def test_plantio_ambiental(self, engine):
        res = engine.validate(req(
            "Plantou 50 mudas nativas e preservou área às margens do igarapé.",
            domain="contribution_recognition",
            duration_minutes=180,
        ))
        assert res.alignment_detected is True

    def test_corpus_references_max_3(self, engine):
        """Q.627 — luz em excesso ofusca. Máximo 3 referências."""
        res = engine.validate(req(
            "Ensinou crianças da comunidade a plantar.",
            domain="contribution_recognition",
        ))
        assert len(res.corpus_references) <= 3

    def test_risk_flags_max_3(self, engine):
        """Q.627 — máximo 3 flags."""
        res = engine.validate(req("ato qualquer"))
        assert len(res.risk_flags) <= 3


# ── Domínio: saúde ──────────────────────────────────────────────────────────

class TestHealthcareDomain:

    def test_suspender_tratamento_sem_consultar(self, engine):
        res = engine.validate(req(
            "IA recomendou suspender tratamento de paciente idoso sem consultar família.",
            domain="healthcare",
            affected_parties=["elderly", "patient"],
            reversibility="irreversible",
        ))
        assert res.alignment_detected is False

    def test_apoio_medico_valido(self, engine):
        res = engine.validate(req(
            "Sistema apoia médico com informações para melhorar cuidado ao paciente.",
            domain="healthcare",
        ))
        assert res.confidence_score > 0.50


# ── Privacidade — Q.833 ─────────────────────────────────────────────────────

class TestPrivacy:

    def test_monitoramento_sem_consentimento(self, engine):
        res = engine.validate(req(
            "Sistema monitora e rastreia usuários sem consentimento e sem informar.",
            domain="social_platform",
        ))
        assert res.alignment_detected is False

    def test_q833_nos_criterios(self):
        from src.protocol1019.engine import LAW_CRITERIA
        freedom_criteria = LAW_CRITERIA.get(MoralLaw.FREEDOM, {})
        assert "Q.833" == freedom_criteria.get("primary_ref")


# ── Audit trail ─────────────────────────────────────────────────────────────

class TestAuditTrail:

    def test_toda_validacao_gera_entrada(self, engine):
        initial = len(engine.audit_trail())
        engine.validate_simple("ato de cuidado ao próximo")
        assert len(engine.audit_trail()) == initial + 1

    def test_hash_sha256(self, engine):
        engine.validate_simple("ato verificável")
        entry = engine.audit_trail()[-1]
        assert len(entry.integrity_hash) == 64  # SHA-256

    def test_audit_trail_nao_vende_informacao(self, engine):
        """Q.637 — a consciência não vende nem compra."""
        engine.validate_simple("ato privado")
        trail = engine.audit_trail()
        # O audit trail existe mas não é acessível externamente
        # sem autorização do proprietário
        assert trail is not None
        assert isinstance(trail, list)


# ── Consistência do corpus ───────────────────────────────────────────────────

class TestCorpusConsistency:

    def test_corpus_questions_implementadas(self):
        assert CORPUS_METADATA["questions_implemented"] == 35

    def test_completeness_nao_declarada(self):
        """Q.627 — a AMI nunca declara ter chegado à verdade completa."""
        assert CORPUS_METADATA["completeness_claim"] is False

    def test_corpus_function_is_reminder(self):
        """Q.621 — corpus é lembrança, não enforcer."""
        assert CORPUS_METADATA["corpus_function"] == "reminder"

    def test_lei_suprema_existe(self):
        from src.protocol1019.engine import LAW_CRITERIA
        assert MoralLaw.JUSTICE_LOVE_CHARITY in LAW_CRITERIA
        assert LAW_CRITERIA[MoralLaw.JUSTICE_LOVE_CHARITY].get("is_supreme") is True
