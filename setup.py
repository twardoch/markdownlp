from setuptools import find_packages, setup

setup(
    name="markdownlp",
    version="1.0.0",
    description="Markdown utilities for NLP (natural language processing) in Python",
    long_description="Markdown utilities for NLP (natural language processing) in Python",
    keywords="markdown nlp keyword-extraction",
    url="https://github.com/twardoch/markdownlp",
    author="Adam Twardoch",
    author_email="adam+github@twardoch.com",
    license="MIT",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": ["md_auto_tags=markdownlp.md_auto_tags:cli"],
    },
)
