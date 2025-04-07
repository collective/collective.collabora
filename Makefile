.PHONY: dev test clean start61 build61 start60 build60 start3852 build3852 start2752 build2722 start43 build43

default: dev

all: dev test

dev: dev61/bin/instance dev60/bin/instance dev3852/bin/instance dev2752/bin/instance dev43/bin/instance

test:
	tox -p
	@echo "You may need to run 'tox -r' to recreate the test environments."

clean:
	rm -rf dev61 dev60 dev3852 dev2752 dev43

start61: dev61/bin/instance
	./dev61/bin/instance fg

build61: dev61/bin/instance
	./dev61/bin/buildout -c ./dev_plone61.cfg buildout:directory=$(CURDIR)/dev61 buildout:develop=$(CURDIR) install

dev61/bin/instance: dev61
	./dev61/bin/pip install -r requirements_plone61.txt
	./dev61/bin/buildout -c ./dev_plone61.cfg buildout:directory=$(CURDIR)/dev61 buildout:develop=$(CURDIR) bootstrap
	./dev61/bin/buildout -c ./dev_plone61.cfg buildout:directory=$(CURDIR)/dev61 buildout:develop=$(CURDIR) install

dev61:
	tox --devenv ./dev61 -e py312-Plone61

start60: dev60/bin/instance
	./dev60/bin/instance fg

build60: dev60/bin/instance
	./dev60/bin/buildout -c ./dev_plone60.cfg buildout:directory=$(CURDIR)/dev60 buildout:develop=$(CURDIR) install

dev60/bin/instance: dev60
	./dev60/bin/pip install -r requirements_plone60.txt
	./dev60/bin/buildout -c ./dev_plone60.cfg buildout:directory=$(CURDIR)/dev60 buildout:develop=$(CURDIR) bootstrap
	./dev60/bin/buildout -c ./dev_plone60.cfg buildout:directory=$(CURDIR)/dev60 buildout:develop=$(CURDIR) install

dev60:
	tox --devenv ./dev60 -e py311-Plone60

start3852: dev3852/bin/instance
	./dev3852/bin/instance fg

build3852: dev3852/bin/instance
	./dev3852/bin/buildout -c ./dev38_plone52.cfg buildout:directory=$(CURDIR)/dev3852 buildout:develop=$(CURDIR) install

dev3852/bin/instance: dev3852
	./dev3852/bin/pip install -r requirements_plone52.txt
	./dev3852/bin/buildout -c ./dev38_plone52.cfg buildout:directory=$(CURDIR)/dev3852 buildout:develop=$(CURDIR) bootstrap
	./dev3852/bin/buildout -c ./dev38_plone52.cfg buildout:directory=$(CURDIR)/dev3852 buildout:develop=$(CURDIR) install

dev3852:
	tox --devenv ./dev3852 -e py38-Plone52

start2752: dev2752/bin/instance
	./dev2752/bin/instance fg

build2752: dev2752/bin/instance
	./dev2752/bin/buildout -c ./dev27_plone52.cfg buildout:directory=$(CURDIR)/dev2752 buildout:develop=$(CURDIR) install

dev2752/bin/instance: dev2752
	./dev2752/bin/pip install -r requirements_plone52.txt
	./dev2752/bin/buildout -c ./dev27_plone52.cfg buildout:directory=$(CURDIR)/dev2752 buildout:develop=$(CURDIR) bootstrap
	./dev2752/bin/buildout -c ./dev27_plone52.cfg buildout:directory=$(CURDIR)/dev2752 buildout:develop=$(CURDIR) install

dev2752:
	tox --devenv ./dev2752 -e py27-Plone52

start43: dev43/bin/instance
	./dev43/bin/instance fg

build43: dev43/bin/instance
	./dev43/bin/buildout -c ./dev_plone43.cfg buildout:directory=$(CURDIR)/dev43 buildout:develop=$(CURDIR) install

dev43/bin/instance: dev43
	./dev43/bin/pip install -r requirements_plone43.txt -cconstraints_py27.txt
	./dev43/bin/buildout -c ./dev_plone43.cfg buildout:directory=$(CURDIR)/dev43 buildout:develop=$(CURDIR) bootstrap
	./dev43/bin/buildout -c ./dev_plone43.cfg buildout:directory=$(CURDIR)/dev43 buildout:develop=$(CURDIR) install

dev43:
	tox --devenv ./dev43 -e py27-Plone43
