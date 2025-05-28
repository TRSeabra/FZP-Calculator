@echo off
call .venv\Scripts\activate
set PYTHONPATH=src
python -m fzp_calculator.GUI
