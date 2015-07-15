import setuptools
import base64


def read(f):
    with open(f) as h:
        return f.read()


setuptools.setup(
    name='polkadots_dotfile_manager',
    version='0.0.1',
    author='lf',
    author_email=base64.b64decode(b'cH10aG9uQGxmY29kZS5jYQ==').decode(),
    description='Yet another dotfile manager',
    long_description = read('README.md'),
    license='MIT',
    url='https://github.com/lf-/polkadots',
    keywords='dotfiles',

    entry_points={
        'console_scripts': [
            'polkadots = polkadots:main'
        ]
    }

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities'
    ]
)
