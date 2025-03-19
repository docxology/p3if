from setuptools import setup, find_packages

setup(
    name="p3if",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "networkx",
        "pytest",
        "pytest-asyncio",
    ],
    extras_require={
        "web": ["beautifulsoup4"],
    },
    python_requires=">=3.7",
    description="Property-Process-Perspective Integration Framework",
    author="P3IF Team",
) 