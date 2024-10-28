.PHONY: dev test clean start60 build60 start52 build52

default: dev

all: dev test

dev: dev60/bin/instance dev52/bin/instance

test:
	tox
	@echo "You may need to run 'tox -r' to recreate the test environments."

clean:
	rm -rf dev60 dev52

start60: dev60/bin/instance
	./dev60/bin/instance fg

build60: dev60/bin/instance
	./dev60/bin/buildout -c ./dev_plone60.cfg buildout:directory=$(CURDIR)/dev60 buildout:develop=$(CURDIR) buildout:update-versions-file=$(CURDIR)/dev_plone60.cfg install

dev60/bin/instance: dev60
	./dev60/bin/pip install -r requirements_plone60.txt
	./dev60/bin/buildout -c ./dev_plone60.cfg buildout:directory=$(CURDIR)/dev60 buildout:develop=$(CURDIR) buildout:update-versions-file=$(CURDIR)/dev_plone60.cfg bootstrap
	./dev60/bin/buildout -c ./dev_plone60.cfg buildout:directory=$(CURDIR)/dev60 buildout:develop=$(CURDIR) buildout:update-versions-file=$(CURDIR)/dev_plone60.cfg install

dev60:
	tox --devenv ./dev60 -e py311-Plone60

start52: dev52/bin/instance
	./dev52/bin/instance fg

build52: dev52/bin/instance
	./dev52/bin/buildout -c ./dev_plone52.cfg buildout:directory=$(CURDIR)/dev52 buildout:develop=$(CURDIR) buildout:update-versions-file=$(CURDIR)/dev_plone52.cfg install

dev52/bin/instance: dev52
	./dev52/bin/pip install -r requirements_plone52.txt
	./dev52/bin/buildout -c ./dev_plone52.cfg buildout:directory=$(CURDIR)/dev52 buildout:develop=$(CURDIR) buildout:update-versions-file=$(CURDIR)/dev_plone52.cfg bootstrap

dev52:
	tox --devenv ./dev52 -e py38-Plone52
