from setuptools import find_packages, setup

setup(
    name="lox",
    version="0.1",
    packages=find_packages("lox"),
    package_dir={"": "lox"},
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "lox=lox:main",
        ],
    },
)
