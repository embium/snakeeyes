import os
import subprocess

import click

from flask.cli import with_appcontext


APP_NAME = 'snakeeyes'
BABEL_I18N_PATH = os.path.join(APP_NAME, 'translations')
MESSAGES_PATH = os.path.join(APP_NAME, 'translations', 'messages.pot')


@click.group()
def babel():
    """ Manage i18n translations. """
    pass


@babel.command()
@with_appcontext
def extract():
    """
    Extract strings into a pot file.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel extract -F babel.cfg -k lazy_gettext ' \
                '-o {0} {1}'.format(MESSAGES_PATH, APP_NAME)
    return subprocess.call(babel_cmd, shell=True)


@babel.command()
@click.option('--language', default=None, help='The output language, ex. de')
@with_appcontext
def init(language=None):
    """
    Map translations to a different language.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel init -i {0} -d {1} -l {2}'.format(MESSAGES_PATH,
                                                           BABEL_I18N_PATH,
                                                           language)
    return subprocess.call(babel_cmd, shell=True)


@babel.command()
@with_appcontext
def compile():
    """
    Compile new translations. Remember to remove #, fuzzy lines.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel compile -d {0}'.format(BABEL_I18N_PATH)
    return subprocess.call(babel_cmd, shell=True)


@babel.command()
@with_appcontext
def update():
    """
    Update existing translations.

    :return: Subprocess call result
    """
    babel_cmd = 'pybabel update -i {0} -d {1}'.format(MESSAGES_PATH,
                                                      BABEL_I18N_PATH)
    return subprocess.call(babel_cmd, shell=True)
