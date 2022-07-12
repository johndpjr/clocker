#!/bin/bash
echo "Pulling from remote..."
git pull
echo "Copying clocker.py"
cp clocker.py clocker
echo "Making clocker executable..."
chmod +x clocker.py
