#
# Run install_packages as root.
# Then run local_install from current directory (for local install + app build).
#

SHELL = bash

VIRTUAL_ENV = var/ve
LOCALPATH = $(CURDIR)
PYTHONPATH = $(LOCALPATH)
SETTINGS = settings
DJANGO_SETTINGS_MODULE = settings.$(SETTINGS)
DJANGO_POSTFIX = --settings=$(DJANGO_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)
PYTHON_BIN = $(VIRTUAL_ENV)/bin
PYTHON = python3
PYTHON_VERSION_FULL := $(wordlist 2,4,$(subst ., ,$(shell python --version 2>&1)))
PYTHON_VERSION_MAJOR := $(word 1,${PYTHON_VERSION_FULL}).$(word 2,${PYTHON_VERSION_FULL})
TYPE = dev
OS = $(shell uname)

INIT_DATA_PATH = data
INIT_DATA_FILE = $(INIT_DATA_PATH)/init.json
INIT_DATA_MEDIA = $(INIT_DATA_PATH)/media

test_modules = apps.test_security.tests

clean:
	find . -name "*.pyc" -delete;
	find . -type d -empty -delete;

cleanvirtualenv:
	rm -rf $(VIRTUAL_ENV)

cleanvar: clean cleanvirtualenv
	rm -rf $(LOCALPATH)/var

cleanall: cleanvar

pip:
	$(PYTHON_BIN)/pip install -r requirements.txt

initvirtualenv:
	virtualenv -p $(PYTHON) $(VIRTUAL_ENV)

bootstrap: initvirtualenv pip

reinstallvirtualenv: cleanvirtualenv bootstrap initvirtualenv initenv

test: clean
	$(PYTHON_BIN)/coverage run $(LOCALPATH)/manage.py test $(test_modules) $(DJANGO_POSTFIX) -v 2 --noinput $(extra)

htmlcoverage: test
	$(PYTHON_BIN)/coverage html -d $(LOCALPATH)/var/reports/htmlcov --rcfile=$(LOCALPATH)/../.coveragerc
	$(OPENHTML) $(LOCALPATH)/var/reports/htmlcov/index.html

initdb:
	mkdir -p $(LOCALPATH)/var/db

syncdb:
	$(PYTHON_BIN)/python manage.py migrate --run-syncdb --noinput $(DJANGO_POSTFIX)

initdata: syncmedia
	if [ -a $(LOCALPATH)/$(INIT_DATA_FILE) ]; then $(PYTHON_BIN)/python manage.py loaddata $(LOCALPATH)/$(INIT_DATA_FILE) $(DJANGO_POSTFIX); fi;

resetdb:
	$(PYTHON_BIN)/python manage.py reset_db --noinput $(DJANGO_POSTFIX)
	$(MAKE) syncdb

syncmedia:
	if [ -d "$(LOCALPATH)/$(INIT_DATA_MEDIA)" ]; then\
		cp -R $(LOCALPATH)/$(INIT_DATA_MEDIA)/* $(LOCALPATH)/media/;\
	fi;

initlog:
	mkdir -p $(LOCALPATH)/var/log

initenv:
	echo -e '\nDJANGO_SETTINGS_MODULE="$(DJANGO_SETTINGS_MODULE)"' >> $(VIRTUAL_ENV)/bin/activate
	echo -e 'export DJANGO_SETTINGS_MODULE' >> $(VIRTUAL_ENV)/bin/activate

callcommand:
	@$(PYTHON_BIN)/python manage.py $(command) $(DJANGO_POSTFIX)

runservices:
	docker run --name=security-elasticsearch -d -e "discovery.type=single-node" -e "xpack.security.enabled=false" -p 9200:9200 docker.elastic.co/elasticsearch/elasticsearch:7.14.0

stopservices:
	docker rm $$(docker stop $$(docker ps -a -q --filter="name=security-elasticsearch"))

runserver:
	$(PYTHON_BIN)/python manage.py runserver --insecure $(DJANGO_POSTFIX)

makemigrations:
	$(PYTHON_BIN)/python manage.py makemigrations

install: cleanvar bootstrap initlog initdb syncdb initdata initenv

update: clean cleanvirtualenv cleanjs bootstrap syncdb initenv
