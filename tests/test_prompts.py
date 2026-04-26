"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture
    def prompt_data(self):
        data = load_prompts(str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"))
        return data.get("bug_to_user_story_v2", {})

    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "system_prompt missing"
        assert bool(prompt_data["system_prompt"].strip()), "system_prompt is empty"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system = prompt_data.get("system_prompt", "").lower()
        role_keywords = ["você é", "atue como", "aja como", "você será", "you are"]
        assert any(k in system for k in role_keywords), "Persona/Role not defined"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system = prompt_data.get("system_prompt", "").lower()
        assert "markdown" in system or "formato" in system or "user story" in system, "Format not mentioned"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system = prompt_data.get("system_prompt", "").lower()
        assert "exemplo" in system or "exemplos" in system or "entrada" in system, "Few-shot examples missing"

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system = prompt_data.get("system_prompt", "").upper()
        assert "[TODO]" not in system, "Found [TODO] in prompt"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, "Less than 2 techniques applied"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])