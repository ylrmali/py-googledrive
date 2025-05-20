from setuptools import setup, find_packages
from pathlib import Path
import os


BASE_DIR = Path(__file__).parent
SRC_DIR = os.path.join(BASE_DIR, "gcapi") 

def read_version():
    """
    Get version from VERSION file in source folder
    """
    with open(f"{SRC_DIR}/VERSION", "r") as file:
        __version__ = file.read()
        return __version__

def read_requirements():
    """
    Get requirements library from requirements file
    """
    dependencies = []    
    with open('requirements.txt', 'r') as f:
        for line in f:
            # Remove leading/trailing whitespaces and ignore comments
            line = line.strip()
            if line and not line.startswith('#'):
                dependencies.append(line)
    return dependencies 

setup(
    name='py-googledrive',
    version=read_version(),
    description='Google drive api wrapper for python, and Django easy backup/restore library',
    author='Ali Yıldırım',
    author_email='ylrmali1289@gmail.com',
    packages=find_packages(),
    license='MIT',
    install_requires=read_requirements(),
    extras_require={
        'django': [
            'django>=4.2'
        ]
    },
    entry_points={
        'console_scripts': [
            'gcapi = gcapi.cli:main'
        ]
    },
    keywords=[
        "python",
        "django",
        "google",
        "database",
        "media",
        "drive",
        "backup",
        "cli"
    ],
    url='https://github.com/ylrmali/py-googledrive.git'
)