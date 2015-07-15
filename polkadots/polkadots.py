import json
import sys
import os
import os.path
import abc
import argparse
import logging


CONFIG_LOCATION = os.path.expanduser('~/.config/polkadots/config.json')


class MissingActionError(Exception):
    pass


class NotALinkError(Exception):
    pass


class Action(metaclass=abc.ABCMeta):

    def __init__(self, **args):
        """
        Instantiate an Action.

        Arguments:
        Whatever's in the config file for this Action
        """
        pass

    def execute(self):
        """
        Execute an action and throw an exception if it fails
        """
        pass


class SymlinkAction(Action):

    def __init__(self, **args):
        """
        Instantiate a SymlinkAction

        Keyword Arguments:
        dir_mode -- symlink everything in the source directory to the same
                    names in the destination directory?
        source -- source file/directory
        destination -- destination file/directory
        """
        self.dir_mode = args.get('dir_mode', False)
        self.source = get_intuitive_path(args['source'])
        self.destination = get_intuitive_path(args['destination'])

    def execute(self):
        if self.dir_mode:
            for f in os.listdir(self.source):
                rmlink(self.destination, ignore_absent=True)
                os.symlink(f, os.path.join(self.destination, f))
        else:
            rmlink(self.destination, ignore_absent=True)
            os.symlink(self.source, self.destination)


def rmlink(link, ignore_absent=False):
    if os.path.exists(link) and os.path.islink(link):
        os.remove(link)
    elif not os.path.exists(link):
        if not ignore_absent:
            raise FileNotFoundError('{} when attempting to delete it as '
                                    'a link'.format(link))
    else:
        raise NotALinkError('Found that {} is not a link when attempting '
                            'overwrite. Please fix your config or '
                            'move this file'.format(link))


def get_intuitive_path(path):
    """
    Take a path and get the absolute, user expanded, variable expanded version
    """
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


def get_actions(action_list):
    actions = []
    for action in action_list:
        try:
            logging.info('Processing {}'.format(action['type']))
            klass = getattr(sys.modules[__name__], action['type'])
            actions.append(klass(**action))
        except:
            logging.error('Error creating Action {}. It might not be '
                          'implemented'.format(action['type']))
            raise
    return actions


def get_config(config=CONFIG_LOCATION):
    if os.path.isfile(config):
        return load_conf(config)
    else:
        logging.error('No config found in {}'.format(config))
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description='Yet another dotfile manager')
    ap.add_argument('--verbose', '-v', action='count', default=0)
    ap.add_argument('--config', '-c', help='Config to use rather than the '
                    'default. Can be a directory')
    args = ap.parse_args()

    log_level = logging.WARNING

    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    conf = get_config(args.config)
    actions = get_actions(conf['actions'])
    for action in actions:
        action.execute()


if __name__ == '__main__':
    main()
