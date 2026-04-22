"""
OpenAI-Compatible Custom Server plugin for DeepHunter

Requirements
------------
- pip install openai

Description
-----------
This plugin integrates any OpenAI-compatible server (e.g. Ollama, vLLM, LM Studio,
llama.cpp, LocalAI) to suggest MITRE techniques based on a given query.
Unlike the standard OpenAI plugin, this one lets you configure a custom BASE_URL
so requests are sent to your own server instead of the OpenAI cloud.
"""

from django.conf import settings
from connectors.utils import get_connector_conf
import re


def get_connector_metadata():
    return {
        'description': (
            "This plugin integrates any OpenAI-compatible server "
            "(e.g. Ollama, vLLM, LM Studio, llama.cpp, LocalAI) to suggest "
            "MITRE techniques based on a given query.\n\n"
            "Unlike the standard OpenAI plugin, this one lets you configure a "
            "custom BASE_URL so requests are sent to your own server instead "
            "of the OpenAI cloud."
        ),
        'domain': 'ai',
        'connector_conf': [
            {
                'key': 'BASE_URL',
                'value': 'http://localhost:11434/v1',
                'fieldtype': 'url',
                'description': 'Base URL of your OpenAI-compatible server (e.g. "http://localhost:11434/v1" for Ollama, "http://localhost:8000/v1" for vLLM).',
            },
            {
                'key': 'API_KEY',
                'value': 'not-needed',
                'fieldtype': 'password',
                'description': 'API key for the custom server. Use "not-needed" if the server does not require authentication.',
            },
            {
                'key': 'MODEL',
                'value': 'llama3',
                'fieldtype': 'char',
                'description': 'Model name served by your custom server (e.g. "llama3", "mistral", "codellama").',
            },
        ],
    }

_globals_initialized = False
def init_globals():
    global DEBUG, PROXY, API_KEY, MODEL, BASE_URL
    global _globals_initialized
    if not _globals_initialized:
        DEBUG = False
        PROXY = settings.PROXY
        BASE_URL = get_connector_conf('openai_custom', 'BASE_URL')
        API_KEY = get_connector_conf('openai_custom', 'API_KEY') or "not-needed"
        MODEL = get_connector_conf('openai_custom', 'MODEL')
        _globals_initialized = True


def get_requirements():
    return ['openai']

def get_mitre_techniques_from_query(query):
    from openai import OpenAI
    init_globals()

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    prompt = f"""
    List only the MITRE ATT&CK TTP IDs (e.g., T1059, T1021.002) that match this query. No descriptions, no explanation.

    Query:
    {query}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    mitre_ttps = re.findall(r'T\d{4}(?:\.\d{3})?', response.choices[0].message.content)
    return list(set(mitre_ttps))

def write_query_with_ai(prompt):
    from openai import OpenAI
    init_globals()

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
