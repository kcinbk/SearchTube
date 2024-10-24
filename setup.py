from setuptools import setup, find_packages

setup(
    name="SearchTube",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'google-api-python-client>=2.112.0', 
        'requests>=2.20.0',  
        'python-dotenv>=1.0.0', 
    ],
)