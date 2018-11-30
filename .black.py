#!/usr/bin/env python3

"""
Chron.
Copyright (C) 2018 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O’Flynn, Mikhail Orlov.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import subprocess
import sys

path = sys.argv[-1]
current_path = os.path.dirname(os.path.abspath(__file__))

if path.startswith(current_path + "/project/"):
    path = path.replace(current_path + "/project/", "/src/")
    subprocess.run(
        [
            "docker-compose",
            "exec",
            "-T",
            "web",
            "sh",
            "-c",
            "black {} {}".format(" ".join(sys.argv[1:-1]), path),
        ],
        stdout=sys.stdout,
    )
else:
    subprocess.run([os.environ["HOME"] + "/.local/bin/black"] + sys.argv[1:])
