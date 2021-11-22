from setuptools import setup

setup(
    name='django-agendjang',
    version='1.0',
    packages=['agendjang', 'agendjang.migrations', 'agendjang.static', 'agendjang.templates'],
    package_dir={'': 'hostproject'},
    url='https://github.com/Guilouf/AgenDjang',
    license='Apache 2.0',
    author='Guilouf',
    description='Django app for task scheduling',
    include_package_data=True  # for non python files, e.g html templates or static css
)
