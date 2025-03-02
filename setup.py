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
    version="1.0a1",
    description="Collabora Online integration for Plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
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
        # 'Documentation': 'https://collective.collabora.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    # keep deprecated namespace_packages for backward compatibility
    namespace_packages=["collective"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "plone.api>=1.8.4",
        "plone.app.contenttypes",
        "plone.restapi",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.robotframework[debug]",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = collective.collabora.locales.update:update_locale
    """,
)
