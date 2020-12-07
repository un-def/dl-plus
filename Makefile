PYTHON := python3
SCRIPTS_DIR := scripts

.PHONY:	clean
clean:
	find -name '*.py[co]' -delete
	rm -rf build dist src/*.egg-info

.PHONY: dist
dist: clean
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: exe
exe: clean
	$(PYTHON) $(SCRIPTS_DIR)/build_exe.py

.PHONY: pyz
pyz: clean
	$(PYTHON) $(SCRIPTS_DIR)/build_pyz.py

.DEFAULT_GOAL :=
