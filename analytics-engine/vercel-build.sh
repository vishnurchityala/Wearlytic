#!/bin/bash
echo "Installing setuptools first..."
pip install setuptools==65.5.1
echo "Installing other dependencies..."
pip install -r requirements.txt
echo "Build completed successfully!" 