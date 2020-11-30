NAME=pytest_playbook_runner

.PHONY: build _build check-local dist check docs major _major minor _minor patch _patch _debug _publish check-local

build: check  _debug _build

_build:
	@echo "Building"

_publish: clean
	@echo "Publishing"
	vmn show --verbose ${NAME} > ver.yml
	python3 ${PWD}/gen_ver.py
	python3 setup.py sdist bdist_wheel
	twine upload ${PWD}/dist/*
	git checkout -- ${PWD}/version.py
	rm -rf ${PWD}/dist
	rm -rf ${PWD}/build

major: check _major _build _publish

_major:
	@echo "Major Release"
	$(eval VERSION := $(shell vmn stamp -r major ${NAME}))

minor: check _minor _build _publish

_minor:
	@echo "Minor Release"
	$(eval VERSION := $(shell vmn stamp -r minor ${NAME}))

patch: check _patch _build _publish

_patch:
	@echo "Patch Release"
	$(eval VERSION := $(shell vmn stamp -r patch ${NAME}))

_debug:
	@echo "Debug Release"
	$(eval VERSION := $(shell vmn show ${NAME}))

check: check-local

check-local:
	@echo "-------------------------------------------------------------"
	@echo "-------------------------------------------------------------"
	@echo "-~      Running static checks                              --"
	@echo "-------------------------------------------------------------"
	@echo "-------------------------------------------------------------"
	@echo "-~      Running unit tests                                 --"
	@echo "-------------------------------------------------------------"
	@echo "-------------------------------------------------------------"
	@echo "-------------------------------------------------------------"

clean:
	git checkout -- ${PWD}/version.py
	rm -rf ${PWD}/dist
	rm -rf ${PWD}/build
