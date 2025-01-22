#!/bin/bash

# Remove existing directories
rm -rf python
rm -f lambda_layer.zip

# Create new python directory
mkdir -p python

# Install packages with no dependencies
pip install --no-deps -r requirements.txt -t python/

# Install minimal dependencies manually
pip install --no-deps charset-normalizer==3.4.1 -t python/
pip install --no-deps idna==3.10 -t python/
pip install --no-deps urllib3==2.3.0 -t python/
pip install --no-deps certifi==2024.12.14 -t python/

# Remove unnecessary files to reduce size
cd python
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name "examples" -exec rm -rf {} +
find . -type d -name "docs" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.so" -exec strip {} \; 2>/dev/null || true
find . -type f -name "*.dist-info" -exec rm -rf {} +
find . -type d -name "*.egg-info" -exec rm -rf {} +
find . -type f -name "*.md" -delete
find . -type f -name "*.txt" -delete
find . -type f -name "*.h" -delete
find . -type f -name "*.c" -delete
find . -type f -name "*.cpp" -delete
find . -type f -name "*.html" -delete
find . -type f -name "*.rst" -delete
find . -type f -name "*.xml" -delete
find . -type f -name "*.json" -delete
find . -type f -name "*.png" -delete
find . -type f -name "*.jpg" -delete
find . -type f -name "*.jpeg" -delete
find . -type f -name "*.gif" -delete

# Remove more specific unnecessary files
rm -rf */tests/
rm -rf */docs/
rm -rf */.github/
rm -rf */examples/

# Go back and create zip
cd ..
zip -r lambda_layer.zip python/

# Show final size
echo "Final layer size:"
du -h lambda_layer.zip 