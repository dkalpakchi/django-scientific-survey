import sys
from os import path

import setuptools

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

DESCRIPTION = (
    'A django survey app for conducting scientific surveys, based on "django-survey-and-report" by Pierre Sassoulas.'
)

THIS_DIRECTORY = path.abspath(path.dirname(__file__))
with open(path.join(THIS_DIRECTORY, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

DEPENDENCIES = [
    "django>=2.2,<=3.2.16",
    "django-bootstrap-form>=3.4",
    "django-registration>=3.0",
    "django-nested-admin>=3.3.3",
    "pytz>=2018.9",
    "ordereddict>=1.1",
    "pyyaml>=6.0",
    "django-tinymce4-lite==1.8.0",
]
DEV_DEPENDENCIES = [
    "django-rosetta",
    "coverage",
    "python-coveralls",
    "coveralls",
    "colorama",
    "pylint",
    "flake8",
    "pre-commit",
]

setuptools.setup(
    name="django-scientific-survey",
    version="0.3.0",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Dmytro Kalpakchi",
    license="AGPL",
    url="https://github.com/dkalpakchi/django-scientific-survey",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Natural Language :: English",
        "Natural Language :: French",
        "Natural Language :: Japanese",
        "Natural Language :: Chinese (Traditional)",
        "Natural Language :: Russian",
        "Natural Language :: Spanish",
        "Natural Language :: German",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
    ],
    install_requires=DEPENDENCIES,
    extras_require={"dev": DEV_DEPENDENCIES},
)
