#!/bin/bash

# Remove existing directories
rm -rf python
rm -f lambda_layer.zip

# Create new python directory
mkdir -p python

# Install all packages with their dependencies for x86_64 architecture
pip install -r requirements.txt --platform manylinux2014_x86_64 --target python/ --only-binary=:all:

# Save initial size
INITIAL_SIZE=$(du -sh python | awk '{print $1}')
echo "Initial size before cleanup: $INITIAL_SIZE"

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

cd ..

# Save size after cleanup
AFTER_CLEANUP_SIZE=$(du -sh python | awk '{print $1}')

# Create zip
zip -r lambda_layer.zip python/

# Save final sizes
UNZIPPED_SIZE=$(du -sh python | awk '{print $1}')
ZIPPED_SIZE=$(du -h lambda_layer.zip | awk '{print $1}')

# Delete python directory
rm -rf python

# Display all sizes at the end
echo "=================== LAYER SIZE REPORT ==================="
echo "Initial size before cleanup:     $INITIAL_SIZE"
echo "Size after cleanup:             $AFTER_CLEANUP_SIZE"
echo "Final unzipped size:            $UNZIPPED_SIZE"
echo "Final zipped layer size:        $ZIPPED_SIZE"
echo "========================================================="
