"""
Changeblogger - AI-powered Git changes summarizer

A tool that analyzes your staged Git changes and generates human-readable
summaries using OpenAI's API, then automatically updates your README.md
with a changelog entry.
"""

__version__ = "1.0.0"
__author__ = "ObsoleteNerd"
__email__ = "me@obsoletenerd.com"

from .main import GitChangesSummarizer

__all__ = ["GitChangesSummarizer"]
