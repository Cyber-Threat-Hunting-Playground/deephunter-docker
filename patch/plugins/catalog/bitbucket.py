"""
Bitbucket connector
Used for repo sync with Bitbucket
"""

from urllib.parse import urlparse
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from django.conf import settings
from notifications.utils import add_error_notification

def get_connector_metadata():
    return {
        'description': 'Bitbucket repo sync',
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
        TIMEOUT_SECONDS = int(getattr(settings, "CONNECTOR_HTTP_TIMEOUT_SECONDS", 30))
        VERIFY_TLS = not bool(getattr(settings, "INSECURE_SKIP_TLS_VERIFY", False))
        _globals_initialized = True


def get_requirements():
    return ["requests"]


def parse_bitbucket_url(url):
    init_globals()

    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    repo_owner = parts[0]
    repo_slug = parts[1]
    branch = parts[3]
    path = parts[4] if len(parts) > 4 else ""
    return repo_owner, repo_slug, branch, path


def _get(url, *, auth=None):
    init_globals()
    try:
        return requests.get(
            url,
            proxies=PROXY,
            auth=auth,
            timeout=TIMEOUT_SECONDS,
            verify=VERIFY_TLS,
        )
    except RequestException as e:
        add_error_notification(f"Bitbucket connector: request failed connecting to {url}: {e}")
        return None


def get_bitbucket_contents(repo):
    """
    Returns a list of JSON files in a Bitbucket repo
    :param repo: The repo object
    :return: A list of JSON files or empty list if error
    """
    init_globals()

    full = []
    repo_owner, repo_slug, branch, path = parse_bitbucket_url(repo.url)
    if path:
        api_url = f"https://api.bitbucket.org/2.0/repositories/{repo_owner}/{repo_slug}/src/{branch}/{path}"
    else:
        api_url = f"https://api.bitbucket.org/2.0/repositories/{repo_owner}/{repo_slug}/src/{branch}/"

    auth = HTTPBasicAuth(repo_owner, repo.token) if repo.token else None
    response = _get(api_url, auth=auth)
    if response is None:
        return []

    if response.status_code == 200:
        data = response.json()
        for item in data.get("values", []):
            if item.get("type") == "commit_file" and Path(item.get("path", "")).suffix == ".json":
                full.append(
                    {"name": item["path"], "download_url": item["links"]["self"]["href"]}
                )

        # Bitbucket is paginating results. The "next" key returns the URL of the next page results
        while "next" in data:
            api_url = data["next"]
            response = _get(api_url, auth=auth)
            if response is None:
                return full
            data = response.json()
            for item in data.get("values", []):
                if item.get("type") == "commit_file" and Path(item.get("path", "")).suffix == ".json":
                    full.append(
                        {"name": item["path"], "download_url": item["links"]["self"]["href"]}
                    )

        return full

    # In case of an error
    add_error_notification(
        f"Bitbucket connector: error (status code {response.status_code}) connecting to {repo.url}"
    )
    return []
