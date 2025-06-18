#!/bin/bash
# Simple runner script for adsgen

MOL=$1
SURF=$2

if [ -z "$MOL" ] || [ -z "$SURF" ]; then
  echo "Usage: $0 <molecule.xyz> <surface.inp>"
  exit 1
fi

adsgen-generate --mol "$MOL" --surf "$SURF"

