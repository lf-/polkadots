Polkadots dotfile manager
=========================

This is a simple dotfile manager. You could use home-manager or other things,
but this is mine. Despite its simplicity, the deliberately Turing-complete
nature of its Python based config files allows for highly dynamic
behaviour.

How to use it
-------------

Install it:
~~~~~~~~~~~

``pip install polkadots-dotfile-manager``

For development:

``pip install --user -e .``

Make a polkadots config directory in .config/polkadots:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic example:

``~/.config/polkadots/config.py``:

.. code-block:: python

    actions = [
        SymlinkAction('aiopanel', '~/.config/aiopanel'),
        SymlinkAction('main', '~', dir_mode=True),
    ]

``~/.config/polkadots/dotfile_repo``:

.. code-block:: text

    ~/.dotfiles

This configuration executes two actions. The first one symlinks the entire
aiopanel directory (files are also supported).

The second one goes through every item in the "main" folder in the
dotfile repo and symlinks them all into the destination directory. For
example, the file .vimrc in main would be symlinked to ~/.vimrc.

Run it:
~~~~~~~

``polkadots --config2 -v``

Options used:

- ``--config2`` -- enables the new python-based config format.
  ``-2`` is an alias for this.
- ``-v`` -- verbose logging

