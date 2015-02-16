from setuptools import setup, find_packages

setup(
    name='babycam',
    version='1.0.0',
    packages=find_packages(),
    entry_points=dict(
        console_scripts=['babycam=babycam:main'],
    ),
)
