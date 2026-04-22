"""
GitHub connector
Used for repo sync with GitHub
"""

from urllib.parse import urlparse
from pathlib import Path

import requests
from requests.exceptions import RequestException
from django.conf import settings
from notifications.utils import add_error_notification

def get_connector_metadata():
    return {
        'description': 'Github repo sync',
        'domain': 'repos',
        'connector_conf': [],
    }

_globals_initialized = False


def init_globals():
    global DEBUG, PROXY, TIMEOUT_SECONDS, VERIFY_TLS
    global _globals_initialized
    if not _globals_initialized:
        DEBUG = False
        PROXY = settings.PROXY
        # Avoid hanging Celery tasks on blocked corporate networks.
        TIMEOUT_SECONDS = int(getattr(settings, "CONNECTOR_HTTP_TIMEOUT_SECONDS", 30))
        # If your environment intercepts SSL, settings may disable verification.
        VERIFY_TLS = not bool(getattr(settings, "INSECURE_SKIP_TLS_VERIFY", False))
        _globals_initialized = True


def get_requirements():
    return ["requests"]


def parse_github_url(url):
    init_globals()

    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    owner = parts[0]
    repo = parts[1]
    # Find if 'tree' is present and get the path after branch name
    if "tree" in parts:
        tree_index = parts.index("tree")
        branch = parts[tree_index + 1]
        path = "/".join(parts[tree_index + 2 :])
    else:
        branch = None
        path = ""
    return owner, repo, branch, path


def get_github_contents(repo):
    """
    Returns a list of JSON files in a GitHub repo
    :param repo: The repo object
    :return: A list of JSON files or empty list if error
    """
    init_globals()

    owner, repo_name, branch, path = parse_github_url(repo.url)
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{path}"

    if repo.token:
        headers = {
            "Authorization": f"token {repo.token}",
            "Accept": "application/vnd.github.v3+json",
        }
    else:
        headers = {}

    try:
        response = requests.get(
            api_url,
            headers=headers,
            proxies=PROXY,
            timeout=TIMEOUT_SECONDS,
            verify=VERIFY_TLS,
        )
    except RequestException as e:
        add_error_notification(f"GitHub connector: request failed connecting to {api_url}: {e}")
        return []

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            add_error_notification(f"GitHub connector: invalid JSON response from {api_url}: {e}")
            return []

        return [
            {"name": item["name"], "download_url": item["download_url"]}
            for item in data
            if item.get("type") == "file" and Path(item.get("name", "")).suffix == ".json"
        ]

    # In case of an error
    add_error_notification(
        f"GitHub connector: error (status code {response.status_code}) connecting to {repo.url}"
    )
    return []
