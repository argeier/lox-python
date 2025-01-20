from setuptools import find_packages, setup

setup(
    name="lox",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "lox=lox.lox:main",
        ],
    },
)
