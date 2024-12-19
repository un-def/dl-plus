src_dir := justfile_dir() / 'src'
scripts_dir := justfile_dir() / 'scripts'
python := 'python3'
_pythonpath := env('PYTHONPATH', '')
export PYTHONPATH := if _pythonpath == '' { src_dir } else { src_dir + ':' + _pythonpath }


@_list:
  just --list --unsorted

@clean:
  find {{src_dir}} -depth -name '__pycache__' -type d -exec rm -rf '{}' \;
  find {{src_dir}} -name '*.py[co]' -type f -delete
  rm -rf build dist {{src_dir}}/*.egg-info

dist: clean
  {{python}} -m build

exe: clean
  {{python}} {{scripts_dir}}/build_exe.py

pyz: clean
  {{python}} {{scripts_dir}}/build_pyz.py

fix:
  isort .

lint:
  isort . -c
  flake8

[positional-arguments]
@test *args:
  pytest "${@}"

[positional-arguments]
@tox *args:
  tox run "${@}"

[positional-arguments]
@run *args:
  {{python}} -m dl_plus "${@}"
