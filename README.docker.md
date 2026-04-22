================================================================================
                    DEEPHUNTER DOCKER - ORIGINAL SETUP GUIDE
================================================================================

⚠️  NOTE: This is the original setup documentation.
    For the enhanced deployment with automation and better tools, see:
    
    📖 README.md - Complete modern deployment guide
    🚀 QUICKSTART.md - Get started in 5 minutes
    
    Or simply run: make install
    
    After cloning, run `make setup-hooks` to activate the git secret-string guard
    (prevents accidental commits of forbidden strings like company names).

================================================================================

ORIGINAL MANUAL SETUP INSTRUCTIONS:

1. adapt ./data/settings.py to your needs

2. to build deephunter image, run:

$ ./build.sh

3. based on provided example `docker-compose.yml` file -> adapt to your needs, run:
$ docker compose up -d

4. init database: run:
$ docker exec -it <mariadb container name> mariadb -u root -p
------------------
create database deephunter;
create user deephunter identified by 'Awes0meP4ssW0rd';
grant all privileges on deephunter.* to deephunter;
------------------

$ docker exec -it <deephunter container name> bash
------------------
$ sed -i 's/import qm.signals/pass #import qm.signals/' /data/deephunter/qm/apps.py
$ source /data/venv/bin/activate
$ ./manage.py makemigrations qm
$ ./manage.py makemigrations extensions
$ ./manage.py makemigrations reports
$ ./manage.py makemigrations connectors
$ ./manage.py makemigrations repos
$ ./manage.py makemigrations notifications
$ ./manage.py makemigrations dashboard
$ ./manage.py makemigrations config
$ ./manage.py makemigrations
$ ./manage.py migrate
$ ./manage.py createsuperuser
$ ./manage.py loaddata install/fixtures/v2.5/qm_country.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_threatactor.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_threatname.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_vulnerability.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_mitretactic.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_mitretechnique.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_tag.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_category.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_targetos.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_savedsearch.json
$ ./manage.py loaddata install/fixtures/v2.5/config.json
$ sed -i 's|"visible_in_analytics": true|"domain": "analytics"|' install/fixtures/v2.5/connectors.json
$ sed -i 's|"visible_in_analytics": false|"domain": ""|' install/fixtures/v2.5/connectors.json
$ ./manage.py loaddata install/fixtures/v2.5/connectors.json
$ ./manage.py loaddata install/fixtures/v2.5/qm_analytic.json	
$ sed -i 's/pass #import qm.signals/import qm.signals/' /data/deephunter/qm/apps.py
------------------

4. Point your browser to https://localhost:9000 or any address that fits your .env configuration

5. (Bug workaround)
The presence of a MicrosoftSentinel analytics rule prevents the editing of all other analytics rules (as by default microsoft sentinel plugin is not enabled)
options:
- enable microsoftsentinel plugin
or
- delete from database (admin settings) the microsoft sentinel analytic rule

6. Enjoy
