import abc
import argparse
import functools
import json
import logging
import os
import os.path
from pathlib import Path
import shutil
import sys
from typing import Callable, cast, Dict, List, Optional
import runpy

from . import version


CONFIG_DIRECTORY = Path('~/.config/polkadots').expanduser()


class Error(Exception):
    pass


class MissingAction(Error):
    pass


class NotALink(Error):
    pass


class Action(metaclass=abc.ABCMeta):

    def __init__(self, dotfile_repo, **args):
        """
        Instantiate an Action.

        Positional arguments:
        The dotfile repository

        Keyword arguments:
        Whatever's in the config file for this Action
        """
        pass

    def execute(self):
        """
        Execute an action and throw an exception if it fails
        """
        pass


class CopyAction(Action):
    """
    An action that copies files and optionally overwrites them
    """

    def __init__(self, dotfile_repo, source, destination, dir_mode=False,
                 overwrite=False, **kwargs):
        """
        Create a CopyAction

        Positional arguments:
        dotfile_repo -- dotfile repository to use for relative paths
        source -- source file/directory
        destination -- destination file/directory

        Keyword arguments:
        overwrite -- overwrite files or print a message?
        dir_mode -- symlink everything in the source directory to the same
                    names in the destination directory?
        """
        self.source = get_intuitive_path(source, base=dotfile_repo)
        self.destination = get_intuitive_path(destination,
                                              base=dotfile_repo)
        self.dotfile_repo = dotfile_repo
        self.overwrite = overwrite
        self.dir_mode = dir_mode

    def execute(self):
        files = []
        if self.dir_mode:
            files.extend((os.path.join(self.source, f)
                          for f in os.listdir(self.source)))
        else:
            files.append(self.source)
        for f in files:
            if os.path.isdir(self.destination):
                if os.path.exists(os.path.join(self.destination,
                                  os.path.basename(f))) and not \
                                  self.overwrite:
                    logging.warning('Skipping file {} because overwrite '
                                    'is False and it exists in the '
                                    'destination'.format(f))
                    continue
            else:
                if os.path.exists(self.destination) and not self.overwrite:
                    logging.warning('Skipping file {} because overwrite is '
                                    'False'.format(f))
                    continue
            shutil.copy(f, self.destination)


class SymlinkAction(Action):

    def __init__(self, dotfile_repo, source, destination, dir_mode=False,
                 **args):
        """
        Instantiate a SymlinkAction

        Positional arguments:
        dotfile_repo -- the dotfile repository. Make everything relative to
                        this.
        source -- source file/directory
        destination -- destination file/directory

        Keyword Arguments:
        dir_mode -- symlink everything in the source directory to the same
                    names in the destination directory?
        """
        self.source = get_intuitive_path(source, base=dotfile_repo)
        self.destination = get_intuitive_path(destination,
                                              base=dotfile_repo)
        self.dir_mode = dir_mode

    def execute(self):
        if self.dir_mode:
            for f in os.listdir(self.source):
                fdest = os.path.join(self.destination, f)
                fsource = os.path.join(self.source, f)
                rmlink(fdest, ignore_absent=True)
                os.symlink(fsource, fdest)
                logging.info('Linked %s to %s', fsource, fdest)
        else:
            rmlink(self.destination, ignore_absent=True)
            os.symlink(self.source, self.destination)
            logging.info('Linked %s to %s', self.source, self.destination)


class CatAction(Action):
    def __init__(self, dotfile_repo, destination, *sources, **args):
        """
        Concatenate n files together. Overwrites the destination file.
        Meow.

        Positional arguments:
        dotfile_repo -- the dotfile repository. Make everything relative to
                        this.
        destination  -- destination file/directory
        *sources     -- any number of source files that will be in the provided
                        order
        """
        self.sources = [get_intuitive_path(source, base=dotfile_repo)
                        for source in sources]
        self.destination = get_intuitive_path(destination, base=dotfile_repo)

    def execute(self):
        with open(self.destination, 'wb') as out:
            for src in self.sources:
                with open(src, 'rb') as h:
                    out.write(h.read())


def rmlink(link, ignore_absent=False):
    if os.path.islink(link):
        logging.info('Deleting {}'.format(link))
        os.remove(link)
    elif not os.path.exists(link):
        logging.debug('File missing when trying to delete {}'.format(link))
        if not ignore_absent:
            raise FileNotFoundError('{link} when attempting to delete it as '
                                    'a link'.format(link))
    else:
        raise NotALink(f'Found that {link} is not a link when attempting '
                        'overwrite. Please fix your config or '
                        'move this file')


def get_intuitive_path(path, base='.'):
    """
    Take a path and get the absolute, user expanded, variable expanded version
    """
    os.chdir(os.path.abspath(os.path.expanduser(os.path.expandvars(base))))
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def load_conf(f):
    """
    Load a JSON based config file/directory

    Returns: a dictionary with the unserialized config
    """
    conf = {}
    if os.path.isdir(f):
        for name in os.listdir(f):
            with open(name) as h:
                conf.update(json.loads(h.read()))
    else:
        with open(f) as h:
            conf.update(json.loads(h.read()))
    return conf


def get_actions(action_list, dotfile_repo):
    actions = []
    for action in action_list:
        try:
            logging.info('Processing {}'.format(action['type']))
            klass = getattr(sys.modules[__name__], action['type'])
            actions.append(klass(dotfile_repo=dotfile_repo, **action))
        except:
            logging.error('Error creating Action {}. It might not be '
                          'implemented'.format(action['type']))
            raise
    return actions


def get_config(config: str):
    if os.path.exists(config) and os.path.isfile(config):
        logging.info('Loading config from {}'.format(config))
        return load_conf(config)
    else:
        logging.error('No config found in {}'.format(config))
        sys.exit(1)


def load_conf2(config_dir: Path) -> Dict:
    """
    Load a new-style runpy based config

    This expects two files in the provided directory:
    dotfile_repo -- a file containing one line (trailing whitespace is trimmed)
                    with where all paths should be relative to (if relative
                    paths are used)
    config.py -- a valid python source file with one global: actions.
                 actions should be a list of Action subclasses. The context
                 that is passed into the execution of this file contains
                 all the Action subclasses as globals.

    Parameters:
    config_dir -- directory to pull dotfile_repo and config.py from

    Returns: a dict with the unserialized config
    """
    if not config_dir.is_dir():
        raise ValueError(f'Provided config directory {config_dir} is not '
                          'a directory')
    with (config_dir / 'dotfile_repo').open() as h:
        dotfile_repo = Path(h.read().rstrip()).expanduser()

    f = config_dir / 'config.py'
    actions = Action.__subclasses__()
    conf_globals = {a.__name__:
                    functools.partial(a, dotfile_repo)
                    for a in actions}
    conf = runpy.run_path(f, init_globals=conf_globals)
    return conf


def get_config_path(basedir: Path = CONFIG_DIRECTORY,
                    profile_name: Optional[str] = None,
                    config2: bool = False) -> str:
    """
    Find the correct path to pull a config from

    Optional parameters:
    basedir -- directory to work under
    profile_name -- if specified, loads from profiles/profile_name
    config2 -- whether to look for a directory or a config.json
    """
    path = basedir
    if profile_name:
        path = path / 'profiles' / profile_name
    if config2:
        return path
    else:
        return path / 'config.json'


def main():
    ap = argparse.ArgumentParser(description='Yet another dotfile manager')
    ap.add_argument('--verbose', '-v', action='count', default=0)
    ap.add_argument('--config2', '-2', action='store_true',
                    help='Use new python-based config format')
    ap.add_argument('--config', '-c', help='Config to use rather than the '
                    'default. Can be a directory')
    ap.add_argument('--profile', '-p', help='Like --config, except it loads'
                    'a profile from the polkadots/profiles directory')
    ap.add_argument('--version', action='store_true')
    args = ap.parse_args()

    if args.version:
        print(version.version)
        sys.exit(0)

    log_level = logging.WARNING

    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    config_path = get_config_path(
        profile_name=args.profile,
        config2=args.config2
    )
    if args.config2:
        conf = load_conf2(config_path)
        actions = conf['actions']
    else:
        conf = get_config(config_path)
        actions = get_actions(conf['actions'], conf['dotfile_repo'])

    for action in actions:
        action.execute()


if __name__ == '__main__':
    main()
