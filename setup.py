import os
from setuptools import setup, find_packages

REQUIREMENTS_PATH = "./"
REQUIREMENTS_FILE_NAME = "requirements.txt"
DEV_REQUIREMENTS_FILE_NAME = "dev-requirements.txt"

requirements = {}

for file_name in os.listdir(REQUIREMENTS_PATH):
    if file_name == REQUIREMENTS_FILE_NAME:
        path = os.path.join(REQUIREMENTS_PATH, file_name)
        with open(path) as f:
            requirements["requirements"] = f.read().splitlines()
    elif file_name == DEV_REQUIREMENTS_FILE_NAME:
        path = os.path.join(REQUIREMENTS_PATH, file_name)
        with open(path) as f:
            requirements["dev_requirements"] = f.read().splitlines()

if __name__ == "__main__":
    setup(
        packages=["pytctracer"],
        install_requires=requirements["requirements"],
        include_package_data=True,
        extras_require={"dev": requirements["dev_requirements"]},
    )