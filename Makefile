PYTHON := python3
SRC_DIR := src
SCRIPTS_DIR := scripts

.PHONY:	clean
clean:
	find $(SRC_DIR) -depth -name '__pycache__' -type d -exec rm -rf '{}' \;
	find $(SRC_DIR) -name '*.py[co]' -type f -delete
	rm -rf build dist $(SRC_DIR)/*.egg-info

.PHONY: dist
dist: clean
	$(PYTHON) -m build

.PHONY: exe
exe: clean
	$(PYTHON) $(SCRIPTS_DIR)/build_exe.py

.PHONY: pyz
pyz: clean
	$(PYTHON) $(SCRIPTS_DIR)/build_pyz.py

.DEFAULT_GOAL :=
