#!/bin/bash

###
# This script generates Ahenk package (ahenk.deb)
#
# Generated file can be found under /tmp/ahenk
###
set -e

pushd $(dirname $0) > /dev/null
PRJ_ROOT_PATH=$(dirname $(pwd -P))
popd > /dev/null
echo "Project path: $PRJ_ROOT_PATH"

# Generate Ahenk packages
echo "Generating Ahenk packages..."
cd "$PRJ_ROOT_PATH"
dpkg-buildpackage -b
echo "Generated Ahenk packages"

EXPORT_PATH=/tmp/ahenk
echo "Export path: $EXPORT_PATH"

# Copy resulting files
echo "Copying generated Ahenk packages to $EXPORT_PATH..."
mkdir -p "$EXPORT_PATH"
cp -rf "$PRJ_ROOT_PATH"/../ahenk*.deb "$EXPORT_PATH"
cp -rf "$PRJ_ROOT_PATH"/../ahenk*.changes "$EXPORT_PATH"
echo "Copied generated Ahenk packages."

echo "Built finished successfully!"
echo "Files can be found under: $EXPORT_PATH"
