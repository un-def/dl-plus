.PHONY:	clean
clean:
	find -name '*.py[co]' -delete
	rm -rf build dist src/*.egg-info

.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.DEFAULT_GOAL :=
