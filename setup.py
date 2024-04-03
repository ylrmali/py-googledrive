from setuptools import setup, find_packages

version = '0.4.2'

setup(
    name='py-googledrive',
    version=version,
    description='Google drive api library',
    author='Ali Yıldırım',
    author_email='ali.yildirim@tarsierteknoloj.com',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        "google-api-python-client==2.123.0"
    ],
    entry_points={
        'console_scripts': [
            'gcapi = pydrive.cli:main'
        ]
    },
    url='https://github.com/ylrmali/py-googledrive.git'
)