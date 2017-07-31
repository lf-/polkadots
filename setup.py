import setuptools
import base64
import re


def read(f):
    with open(f) as h:
        return h.read()

# read the version from version.py

with open('polkadots/version.py') as h:
    PKG_VERSION = re.match("version = '(.*)'", h.read()).groups()[0]


setuptools.setup(
    name='polkadots_dotfile_manager',
    version=PKG_VERSION,
    packages=setuptools.find_packages(),
    author='lf',
    author_email=base64.b64decode(b'cH10aG9uQGxmY29kZS5jYQ==').decode(),
    description='Yet another dotfile manager',
    long_description=read('README.rst'),
    license='MIT',
    url='https://github.com/lf-/polkadots',
    keywords='dotfiles',
    python_requires='>=3.6',

    entry_points={
        'console_scripts': [
            'polkadots = polkadots:main'
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
    ]
)
