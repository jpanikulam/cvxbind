from setuptools import setup

setup(
    name='cvxbind',
    version='1.0',
    description='Python Oculus Rift DK2 Driver',
    author='Jacob Panikulam',
    author_email='jpanikulam@ufl.edu',
    url='https://www.python.org/',
    entry_points={
        "console_scripts": ["cvxbind=cvxbind.main:main"]
    },
    package_dir={
        '': '.',
    },
    packages=[
        'cvxbind',
    ],
    test_suite="test"

)
