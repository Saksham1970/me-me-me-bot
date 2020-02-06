from os import system

with open("packages.txt") as f:
    packages = f.read().split("\n")

for package in packages:
    system(f"pip install {package}")