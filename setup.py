from setuptools import setup, find_packages

version = '0.4.2'

def read_requirements(file: str='requirements.txt'):
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
    version=version,
    description='Google drive api library',
    author='Ali Yıldırım',
    author_email='ali.yildirim@tarsierteknoloj.com',
    packages=find_packages(),
    license='MIT',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'gcapi = pydrive.cli:main'
        ]
    },
    url='https://github.com/ylrmali/py-googledrive.git'
)