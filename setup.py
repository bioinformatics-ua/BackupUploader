from setuptools import setup, find_packages
import json
import os

with open(os.path.join(os.path.dirname(__file__), "version.json")) as version_file:
    version = json.load(version_file)["version"]

setup(
    name="backup_uploader",
    packages=find_packages(include=[
        "backup_uploader",
        "backup_uploader.clients",
    ]),
    license="MIT",
    version=version,
    url="https://github.com/aspedrosa/BackupsUploader",
    author="André Pedrosa",
    author_email="aspedr0sa@protonmail.com",
    keywords=["backup", "uploader"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
    include_package_data=True,
    install_requires=["click"],
    extras_require={
        "dropbox": ["dropbox"],
        "mega": ["mega.py"],
    },
    entry_points="""
    [console_scripts]
    backup_uploader=backup_uploader.cli:main
    """,
)
