from setuptools import setup, find_packages

setup(
    name='apys',
    description='Set of python functions to access different APIs',
    author='Fernando Corrales',
    author_email='fscpython@gmail.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'datar',
        'datar-numpy',
        'datar-pandas',
        'pandas',
        'numpy',
        'pyhomebroker',
        'requests',
        'SQLAlchemy>=1,<2',
        'urllib3',
        'pyRofex',
    ]
)
