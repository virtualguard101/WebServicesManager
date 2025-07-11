#!/bin/bash
set -ue

source .venv/bin/activate && python -m unittest discover -s test
