"""
Create config_aiquerylog table for the AI Debug tab.

Run after deploying code that adds config.models.AIQueryLog:

$ source /data/venv/bin/activate
(venv) $ cd /data/deephunter/
(venv) $ python manage.py runscript upgrade.fr_ai_query_log
"""

from django.db import connection

from config.models import AIQueryLog


def run():
    table_name = AIQueryLog._meta.db_table
    with connection.cursor() as cursor:
        if table_name in connection.introspection.table_names(cursor):
            print(f"[i] Table {table_name} already exists — nothing to do.")
            return

    with connection.schema_editor() as editor:
        editor.create_model(AIQueryLog)

    print(f"[+] Created table {table_name} for AIQueryLog.")
