#!/usr/bin/env python

import argparse
import os
import subprocess
from os.path import (
    abspath,
    dirname,
    exists,
    join,
)
from pprint import pprint
try:
    from inspect import signature
except ImportError:
    from funcsigs import signature

from jupyter_core.paths import jupyter_config_dir, ENV_CONFIG_PATH


def install(enable=False, **kwargs):
    """ Install the nbbrowserpdf nbextension assets and optionally enables the
        nbextension and server extension for every run.

        Parameters
        ----------
        enable: bool
            Enable the extension on every notebook launch
        **kwargs: keyword arguments
            Other keyword arguments passed to the install_nbextension command
    """
    from notebook.nbextensions import install_nbextension
    from notebook.services.config import ConfigManager

    directory = join(dirname(abspath(__file__)), 'static', 'nbbrowserpdf')

    kwargs = {k: v for k, v in kwargs.items() if not (v is None)}

    kwargs["destination"] = "nbbrowserpdf"
    install_nbextension(directory, **kwargs)

    if enable:
        if "prefix" in kwargs:
            path = join(kwargs["prefix"], "etc", "jupyter")
            if not exists(path):
                print("Making directory", path)
                os.makedirs(path)

        cm = ConfigManager(config_dir=path)
        print("Enabling nbbrowserpdf server component in", cm.config_dir)
        cfg = cm.get("jupyter_notebook_config")
        print("Existing config...")
        pprint(cfg)
        server_extensions = (
            cfg.setdefault("NotebookApp", {})
            .setdefault("server_extensions", [])
        )
        if "nbbrowserpdf" not in server_extensions:
            cfg["NotebookApp"]["server_extensions"] += ["nbbrowserpdf"]

        cm.update("jupyter_notebook_config", cfg)
        print("New config...")
        pprint(cm.get("jupyter_notebook_config"))

        try:
            subprocess.call(["conda", "info", "--root"])
            print("conda detected")
            _jupyter_config_dir = ENV_CONFIG_PATH[0]
        except OSError:
            print("conda not detected")
            _jupyter_config_dir = jupyter_config_dir()

        cm = ConfigManager(config_dir=join(_jupyter_config_dir, "nbconfig"))
        print(
            "Enabling nbpresent nbextension at notebook launch in",
            cm.config_dir
        )

        if not exists(cm.config_dir):
            print("Making directory", cm.config_dir)
            os.makedirs(cm.config_dir)

        cm.update(
            "notebook", {
                "load_extensions": {
                    "nbbrowserpdf/index": True
                },
            }
        )


if __name__ == '__main__':
    from notebook.nbextensions import install_nbextension

    install_kwargs = list(signature(install_nbextension).parameters)

    parser = argparse.ArgumentParser(
        description="Installs nbbrowserpdf nbextension")

    parser.add_argument(
        "-e", "--enable",
        help="Automatically load server and nbextension on notebook launch",
        action="store_true")

    # inherit the arguments of the upstream install_nbextension
    [parser.add_argument(
        "--{}".format(arg),
        **(dict(action="store_true")
           if arg in ["symlink", "overwrite", "quiet", "user"] else
           dict(action="store", nargs="?"))
        )
        for arg in install_kwargs]

    install(**parser.parse_args().__dict__)
