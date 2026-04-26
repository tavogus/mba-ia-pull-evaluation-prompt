"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.load import dumps
from utils import check_env_vars, print_section_header

load_dotenv()

# Mapeando LANGSMITH para LANGCHAIN
if "LANGSMITH_API_KEY" in os.environ and "LANGCHAIN_API_KEY" not in os.environ:
    os.environ["LANGCHAIN_API_KEY"] = os.environ["LANGSMITH_API_KEY"]


def pull_prompts_from_langsmith():
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_file = "prompts/bug_to_user_story_v1.yml"

    try:
        print(f"📥 Puxando '{prompt_name}'...")
        prompt = hub.pull(prompt_name)

        # Serializa via LangChain nativo e converte para YAML
        prompt_dict = json.loads(dumps(prompt))

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(prompt_dict, f, allow_unicode=True, sort_keys=False)

        print(f"✅ Prompt salvo em {output_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao puxar prompt: {e!r}")
        import traceback; traceback.print_exc()
        return False

def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())