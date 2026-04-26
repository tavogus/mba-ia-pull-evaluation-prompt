"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

# Mapeando LANGSMITH para LANGCHAIN
if "LANGSMITH_API_KEY" in os.environ and "LANGCHAIN_API_KEY" not in os.environ:
    os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        messages = [
            ("system", prompt_data.get("system_prompt", "")),
            ("human", prompt_data.get("user_prompt", "{bug_report}"))
        ]
        prompt_template = ChatPromptTemplate.from_messages(messages)
        
        tags = prompt_data.get("tags", [])
        techniques = prompt_data.get("techniques_applied", [])
        all_tags = tags + techniques
        description = prompt_data.get("description", "")
        
        url = hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=all_tags
        )
        print(f"✅ Prompt publicado com sucesso no Hub!")
        print(f"URL: {url}")
        return True
    except Exception as e:
        error_str = str(e)
        if "409" in error_str and "Nothing to commit" in error_str:
            print("✅ Prompt já está atualizado no Hub (sem mudanças desde o último commit).")
            return True
        print(f"❌ Erro ao publicar prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    if not prompt_data.get("system_prompt"):
        errors.append("Campo obrigatório faltando: system_prompt")
    if not prompt_data.get("description"):
        errors.append("Campo obrigatório faltando: description")
        
    return len(errors) == 0, errors


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS")
    
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()

    if " " in username:
        print(f"❌ USERNAME_LANGSMITH_HUB contém espaços: '{username}'")
        print("   Use o handle/slug do LangSmith Hub (ex: 'mainara-farias', não 'Mainara Farias')")
        print("   Encontre seu handle em: https://smith.langchain.com/prompts")
        return 1

    prompt_name = f"{username}/bug_to_user_story_v2"
    
    data = load_yaml("prompts/bug_to_user_story_v2.yml")
    if not data or "bug_to_user_story_v2" not in data:
        print("❌ Não foi possível carregar bug_to_user_story_v2 do arquivo YAML.")
        return 1
        
    prompt_data = data["bug_to_user_story_v2"]
    is_valid, errors = validate_prompt(prompt_data)
    
    if not is_valid:
        print("❌ Validação falhou:")
        for e in errors:
            print(" -", e)
        return 1
        
    print(f"📤 Fazendo push do prompt '{prompt_name}'...")
    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())