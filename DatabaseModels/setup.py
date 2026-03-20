from setuptools import find_packages, setup

setup(
    name="django_models",
    version="0.1.0",
    description="Django models package for graph backend challenge",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.12",
)
