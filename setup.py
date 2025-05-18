from setuptools import setup, find_packages

setup(
    name="aws-utils",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "boto3>=1.26.0",
        "pyyaml>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-mock>=3.10.0",
        ],
    },
    python_requires=">=3.8",
)