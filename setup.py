# setup.py
from setuptools import setup, find_packages

setup(
    name="mtg-scanner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if not line.startswith("#")
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mtg-scanner=src.camera_scanner:main",
            "mtg-server=src.main:main",
        ],
    },
)