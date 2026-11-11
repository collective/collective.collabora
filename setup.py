"""Installer for the collective.collabora package."""

try:
    # find_packages errors out on py3 on non-python packages
    from setuptools import find_namespace_packages
except ImportError:
    # but works fine with find_packages
    from setuptools import find_packages as find_namespace_packages

from setuptools import setup

long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="collective.collabora",
    version="2.0.0.dev0",
    description="Collabora Online integration for Plone",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    keywords="Python Plone CMS",
    author="Guido A.J. Stevens",
    author_email="guido.stevens@cosent.net",
    url="https://github.com/collective/collective.collabora",
    license_expression="GPL-2.0-only",
    project_urls={
        "PyPI": "https://pypi.org/project/collective.collabora/",
        "Source": "https://github.com/collective/collective.collabora",
        "Tracker": "https://github.com/collective/collective.collabora/issues",
        "Documentation": "https://collectivecollabora.readthedocs.io/en/latest/",
    },
    packages=find_namespace_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    # python_requires comma sep functions as an AND.
    # So to express ==2.7 OR >= 3.8, we have to write it as follows:
    python_requires=">=3.11,<3.15",
    install_requires=[
        "future",
        "plone.api",
        "plone.app.contenttypes",
        "plone.protect",
        "plone.restapi",
        "python-dateutil",
    ],
    extras_require={
        "test": [
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
