from setuptools import setup, find_packages

setup(
    name="aws-utils-cli",
    version="0.1.0",
    description="CLI para facilitar operações com AWS SQS e S3",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Seu Nome",
    author_email="seu@email.com",
    url="https://github.com/greijal/aws_utils",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.26.0",
        "pyyaml>=6.0.1",
        "questionary",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "aws-utils-cli=cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    include_package_data=True,
)