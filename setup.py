#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="changeblogger",
    version="1.0.0",
    author="ObsoleteNerd",
    author_email="me@obsoletenerd.com",
    description="An AI-assisted Git changes summarizer that automatically analyzes your staged changes and updates your README.md with intelligent changelog entries.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/obsoletenerd/changeblogger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "changeblogger=changeblogger.main:main",
        ],
    },
    keywords="git changelog ai openai documentation automation",
)
