from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_desc = fh.read()

setup(
    name="crashlab",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "dnspython",
        "aiohttp",
        "rich",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "crashlab = crashlab.cli:main",
        ],
    },
    author="Cyber Tech Teacher",
    description="Educational DoS simulation lab for closed networks",
    long_description=long_desc,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Free for non-commercial educational use",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
