from setuptools import setup, find_packages

setup(
    name="SearchTube",
    version="1.0",
    packages=find_packages(),
    author='Keenan Chen',
    install_requires=[
        'pandas',
        'numpy',
        'google-api-python-client>=2.112.0', 
        'requests',  
        'python-dotenv' 
                     ]
    )