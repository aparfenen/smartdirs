from setuptools import setup, find_packages

setup(
    name="smartdirs",
    version="0.3.0",
    packages=find_packages(),
    install_requires=["pytz", "tzlocal"],
    author="Anna Parfenova",
    author_email="your.email@example.com",
    description="A simple Python package for creating directories with consistent naming and logging.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/smartdirs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)