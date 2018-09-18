import os
import facebook_login

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = open('requirements.txt').read().splitlines()

dev_requires = [
    'pytest',
    'pytest-django',
    'pytest-cov',
    'responses',
    'fabric',
    'mixer',
]

setup(
    name='django-facebook-login',
    version=facebook_login.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description=
    'A GraphQL endpoint and authentication backend to signup or login a valid user access token from Facebook',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/theartling/django-facebook-login/',
    author='Martin Brochhaus',
    author_email='mbrochh@gmail.com',
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
