# -*- coding: utf-8 -*-
"""Installer for the collective.collabora package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="collective.collabora",
    version="0.9.1.dev0",
    description="Collabora Online integration for Plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Guido A.J. Stevens",
    author_email="guido.stevens@cosent.net",
    url="https://github.com/collective/collective.collabora",
    project_urls={
        "PyPI": "https://pypi.org/project/collective.collabora/",
        "Source": "https://github.com/collective/collective.collabora",
        "Tracker": "https://github.com/collective/collective.collabora/issues",
        "Documentation": "https://collective.collabora.readthedocs.io/en/latest/",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    # keep deprecated namespace_packages for backward compatibility
    namespace_packages=["collective"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    # python_requires comma sep functions as an AND.
    # So to express ==2.7 OR >= 3.8, we have to write it as follows:
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=3.6.*,!=3.7.*",  # noqa: E501
    install_requires=[
        "setuptools",
        "future",
        "plone.api",
        "plone.app.contenttypes",
        "plone.protect",
        "plone.restapi",
        "python-dateutil",
    ],
    extras_require={
        "test": [
            "mock",
            "plone.app.testing",
            "plone.testing",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = collective.collabora.locales.update:update_locale
    """,
)
