Polkadots is a small dotfile manager
====================================

What not to expect
------------------

A giant pile of features. That being said, this is extensible and will
probably get some sort of plugin support.

Future plans
------------

-  [ ] Plugin support

-  [ ] World domination

-  [x] Config directories

How to use the damn thing
-------------------------

Install it:
~~~~~~~~~~~

``pip install polkadots-dotfile-manager``

Make a polkadots config file in .config/polkadots/config.json:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code:: json

    {
        "dotfile_repo": "~/.dotfiles",
        "actions": [
            {
                "type": "SymlinkAction",
                "source": "derpityapp",
                "destination": "~/.config/derp"
            },
            {
                "type": "SymlinkAction",
                "source": "main",
                "destination": "~",
                "dir_mode": true
            }
        ]
    }

This configuration makes two actions. The first one symlinks the entire
derpityapp directory (but it could also do files the same).

The second one goes through every item in the "main" folder in the
dotfile repo and symlinks them all into the destination directory. For
example, the file .vimrc in main would be symlinked to ~/.vimrc.
