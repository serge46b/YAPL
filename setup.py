from setuptools import setup
import yapl
import os

local_folder = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(local_folder, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
with open(os.path.join(local_folder, "requirements.txt"), encoding="utf-8") as f:
    requirements = f.read().split("\n")

setup(
    name="yapl",
    version=yapl.__version__,
    description="Yet Another Python Logger - module that helps you ",
    author="Serge46b",
    author_email="serg46b@gmail.com",
    packages=["yapl"],
    install_requires=requirements,
)
