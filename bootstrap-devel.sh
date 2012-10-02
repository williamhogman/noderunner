#!/bin/sh

cd $(dirname $0)

virtualenv -q -p python2.7 --clear --prompt="(nr)" .venv
source .venv/bin/activate

mkdir .pip_download_cache
export PIP_DOWNLOAD_CACHE=".pip_download_cache"

pip install -r requirements-test.txt

echo
echo "Development virtualenv setup in .venv"
echo "source .venv/bin/activate to activate"
