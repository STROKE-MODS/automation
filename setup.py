"""
YouTube AI Digest - Automated AI/ML video reports to Telegram
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="youtube-ai-digest",
    version="1.0.0",
    author="STROKE-MODS",
    author_email="contact@example.com",
    description="Automated weekly AI/ML video reports delivered to Telegram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/STROKE-MODS/automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW :: HTTP :: HTTP Clients",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "youtube-digest=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
)