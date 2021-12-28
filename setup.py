from setuptools import setup

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='django-agendjang',
    version='1.0.3',
    packages=['agendjang', 'agendjang.migrations', 'agendjang.static', 'agendjang.templates'],
    package_dir={'': 'hostproject'},
    url='https://github.com/Guilouf/AgenDjang',
    license='Apache 2.0',
    author='Guilouf',
    description='Django app for task scheduling',
    install_requires=['djangorestframework',
                      'markdown'],
    long_description=long_description,  # will be included in METADATA file in dist-info folder
    long_description_content_type='text/markdown',
    include_package_data=True  # for non python files, e.g html templates or static css
)
