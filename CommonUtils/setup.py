from setuptools import find_packages, setup

setup(
    name="common_utils",
    version="0.1.0",
    description="Shared helpers for graph challenge components",
    packages=find_packages(),
    include_package_data=True,
    package_data={"CommonUtils": ["sql/*.sql"]},
    python_requires=">=3.12",
)
