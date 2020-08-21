#!/usr/bin/env python3
# This source file is part of Obozrenie
# Copyright 2015 Artem Vorotnikov

# For more information, see https://github.com/obozrenie/obozrenie

# Obozrenie is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.

# Obozrenie is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Obozrenie.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess

from obozrenie.global_settings import *
from obozrenie.global_strings import *

from obozrenie import helpers


def steam_launch_pattern(game_settings: dict, host: str, port: str, password: str, steam_app_id: str, **kwargs) -> list:
    steam_path = str(game_settings["steam_path"])
    launch_cmd = [steam_path, "-applaunch",
                  steam_app_id, "+connect", host + ":" + port]
    if password:
        launch_cmd += ["+password", password]

    return launch_cmd


def rigsofrods_launch_pattern(path: str, **kwargs) -> list:
    launch_cmd = [path]

    return launch_cmd


def rigsofrods_prelaunch_hook(game_settings: dict, host: str, port: str, password: str, **kwargs) -> None:
    config_file = os.path.expanduser("~/.rigsofrods/config/RoR.cfg")

    if os.path.exists(config_file):
        subprocess.call(
            ["sed", "-i", "s/Network enable.*/Network enable=Yes/", config_file])
        subprocess.call(
            ["sed", "-i", "s/Server name.*/Server name=" + host + "/", config_file])
        subprocess.call(
            ["sed", "-i", "s/Server port.*/Server port=" + port + "/", config_file])
        subprocess.call(
            ["sed", "-i", "s/Server password.*/Server password=" + password + "/", config_file])
    else:
        if os.path.exists(os.path.dirname(config_file)) is False:
            os.makedirs(os.path.dirname(config_file))
        with open(config_file, "x") as f:
            f.write("Network enable=Yes" + "\n")
            f.write("Server name=" + host + "\n")
            f.write("Server port=" + port + "\n")
            f.write("Server password=" + password + "\n")
            f.close()


def rigsofrods_postlaunch_hook(**kwargs) -> None:
    config_file = os.path.expanduser("~/.rigsofrods/config/RoR.cfg")

    subprocess.call(
        ["sed", "-i", "s/Network enable.*/Network enable=No/", config_file])


def quake_launch_pattern(path: str, host: str, port: str, password: str, **kwargs) -> list:
    launch_cmd = [path, "+connect", host + ":" + port]
    if password:
        launch_cmd += ["+password", password]

    return launch_cmd


def hl2_launch_pattern(game: str, path: str, game_settings: dict, host: str, port: str, password: str, **kwargs) -> list:
    workdir = os.path.dirname(path)
    env_dict = dict(os.environ)
    try:
        if game_settings["workdir"]:
            workdir = os.path.expanduser(game_settings["workdir"])
    except KeyError:
        pass
    env_dict['PWD'] = workdir
    ld_dir = "./bin"
    try:
        env_dict['LD_LIBRARY_PATH'] = ":".join(
            [ld_dir, env_dict['LD_LIBRARY_PATH']])
    except KeyError:
        env_dict['LD_LIBRARY_PATH'] = ld_dir

    launch_cmd = [path, "-game", game, "+connect", host + ":" + port]
    if password:
        launch_cmd += ["+password", password]

    return launch_cmd


def openttd_launch_pattern(path: str, host: str, port: str, **kwargs) -> list:
    launch_cmd = [path, "-n", host + ":" + port]

    return launch_cmd


def minetest_launch_pattern(game_settings: dict, path: str, host: str, port: str, password: str, **kwargs) -> list:
    nickname = str(game_settings["nickname"])
    launch_cmd = [path, "--go", "--address",
                  host, "--port", port, "--name", nickname]
    if password:
        launch_cmd += ["--password", password]

    return launch_cmd


def do_launch(launch_cmd: list) -> Exception:
    try:
        # Launch
        helpers.debug_msg([LAUNCHER_MSG, i18n._("Launching '%(launch_cmd)s'") % {
                          'launch_cmd': " ".join(launch_cmd)}])
        env_dict = dict(os.environ)
        pid = subprocess.Popen(
            launch_cmd, cwd=env_dict['PWD'], env=env_dict, start_new_session=True)
        return None
    except OSError as e:
        helpers.debug_msg([LAUNCHER_MSG, e])
        return e


def launch_game(game: str, launch_pattern: str, game_settings: dict, host: str, port: str, password: str, steam_app_id: str = None) -> Exception:
    """Launches the game based on specified launch pattern"""
    try:
        path = os.path.expanduser(str(game_settings["path"]))

        # Pre-launch
        try:
            launch_cmd = globals()[launch_pattern + "_launch_pattern"](game=game, path=path,
                                                                       game_settings=game_settings, host=host, port=port, password=password, steam_app_id=steam_app_id)
        except KeyError:
            raise Exception(
                " ".join([LAUNCHER_MSG, i18n._("Launch pattern does not exist")]))

    except OSError as e:
        print(e)
        return e
    else:
        try:
            globals()[launch_pattern + "_prelaunch_hook"]()
        except KeyError:
            pass

        do_launch(launch_cmd)

        try:
            globals()[launch_pattern + "_postlaunch_hook"]()
        except KeyError:
            pass
