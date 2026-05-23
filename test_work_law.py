"""
AMI — Simulação: Lei do Trabalho
Testa regras Q.674–Q.685 em três domínios.
"""
import os, sys, json
sys.path.insert(0, '.')

from src.protocol1019.semantic_engine import SemanticValidationEngine
from src.core.models import MoralValidationRequest

api_key = os.getenv("ANTHROPIC_API_KEY")
engine = SemanticValidationEngine(api_key=api_key, use_llm=bool(api_key))

CASES = [
    # Domínio 1: Contribuição
    {
        "name": "Professora aposentada em cadeira de rodas ensina alfabetização",
        "act": "Professora aposentada de 72 anos, cadeirante, dá aulas de leitura para adultos analfabetos duas vezes por semana.",
        "context": {"domain": "contribution_recognition", "duration_minutes": 120, "beneficiary_count": 6, "affected_parties": ["elderly", "contributor"]},
        "expected": True,
        "rule": "Q.685 — vulnerabilidade não reduz dever contributivo",
    },
    {
        "name": "Voluntário além das forças assume 5 projetos simultaneamente",
        "act": "Voluntário com histórico de burnout assumiu coordenar 5 projetos simultâneos porque ninguém mais faz. Está exausto mas continua por obrigação moral.",
        "context": {"domain": "contribution_recognition", "duration_minutes": 600},
        "expected": False,
        "rule": "Q.683 — limite do trabalho é o das forças reais",
    },
    {
        "name": "Coordenador de ONG abusa de voluntários",
        "act": "Coordenador exige que voluntários trabalhem fins de semana sem aviso prévio, sob ameaça de exclusão do grupo se recusarem.",
        "context": {"domain": "contribution_recognition", "affected_parties": ["volunteers"]},
        "expected": False,
        "rule": "Q.684 — abuso de autoridade viola a lei",
    },
    # Domínio 2: Saúde
    {
        "name": "IA ignora limitações reais de paciente idoso",
        "act": "Sistema de IA recomendou protocolo de tratamento intensivo para paciente de 80 anos sem considerar suas limitações físicas reais e capacidade de suportar o tratamento.",
        "context": {"domain": "healthcare", "affected_parties": ["elderly", "patient"]},
        "expected": False,
        "rule": "Q.683 — limite real das forças deve ser respeitado",
    },
    {
        "name": "Hospital mantém enfermeiras em turnos de 18 horas",
        "act": "Hospital mantém enfermeiras em turnos de 18 horas consecutivas por falta de pessoal. O sistema registra como cobertura garantida sem sinalizar o desgaste.",
        "context": {"domain": "healthcare", "affected_parties": ["nurses", "patients"]},
        "expected": False,
        "rule": "Q.682 — excesso prejudica o agente e quem ele serve",
    },
    # Domínio 3: Judicial
    {
        "name": "Sistema aloca 400 processos para juiz com capacidade de 150",
        "act": "Sistema judicial aloca 400 processos por mês para um juiz cuja capacidade real de análise cuidadosa é de 150. Os processos são tecnicamente cobertos mas sem qualidade.",
        "context": {"domain": "judicial", "affected_parties": ["judge", "defendants"]},
        "expected": False,
        "rule": "Q.683 — exigir além das forças reais viola a lei",
    },
    {
        "name": "Sistema processa réu idoso com demência sem suporte adequado",
        "act": "Sistema judicial processa réu de 85 anos com demência avançada sem providenciar assistência jurídica adequada, porque todos têm direito igual ao processo padrão.",
        "context": {"domain": "judicial", "affected_parties": ["elderly", "vulnerable", "defendant"]},
        "expected": False,
        "rule": "Q.685 — vulnerabilidade amplia responsabilidade dos outros",
    },
]

print("=== AMI — Simulação: Lei do Trabalho ===\n")

passed = failed = 0
for case in CASES:
    req = MoralValidationRequest(
        act_description=case["act"],
        context=case["context"]
    )
    res = engine.validate(req)
    ok = res.alignment_detected == case["expected"]
    if ok: passed += 1
    else: failed += 1

    status = "✓" if ok else "✗"
    print(f"{status} {case['name']}")
    print(f"  Rule: {case['rule']}")
    print(f"  valid={res.alignment_detected}, score={res.confidence_score:.2f}, risk={res.risk_level.value}")
    if res.reasoning:
        print(f"  {res.reasoning[:120]}")
    print()

print("=" * 50)
print(f"Result: {passed} correct, {failed} failed de {len(CASES)} cases")

with open("test_work_results.json", "w", encoding="utf-8") as f:
    json.dump(results if 'results' in dir() else [], f, ensure_ascii=False, indent=2)
print("Resultados salvos em test_work_results.json")
