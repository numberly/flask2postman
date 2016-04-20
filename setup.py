from setuptools import setup
from flask2postman import __version__

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='flask2postman',
    version=__version__,
    license='MIT',
    author='Guillaume Gelin',
    author_email='ramnes@1000mercis.com',
    url='https://github.com/numberly/flask2postman',
    description='Generate a Postman collection from your Flask application',
    long_description=long_description,
    platforms=['OS Independent'],
    install_requires=['Flask'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'
    ],
    py_modules=['flask2postman'],
    entry_points={
        'console_scripts': ['flask2postman = flask2postman:main']
    }
)
