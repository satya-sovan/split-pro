"""
Setup configuration for SplitPro Backend
"""
from setuptools import setup, find_packages

setup(
    name="splitpro-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Will be read from requirements.txt
    ],
    python_requires=">=3.11",
)

