#!/bin/bash
rm -rf python
mkdir -p python
pip install -r requirements.txt -t python/
zip -r lambda_layer.zip python/ 