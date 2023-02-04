from setuptools import setup, find_packages

setup(
    name='apys',
    description='Set of python functions to access different APIs',
    author='Fernando Corrales',
    author_email='corrales_fernando@hotmail.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'datar',
        'pandas',
        'numpy',
        'pyhomebroker',
        'requests',
        'SQLAlchemy',
        'urllib3'
    ]
)
