#!/usr/bin/env python3
#
# Isotope Builder
# Copyright (C) 2020 Nichole Mattera
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import argparse
import common
import config
import modules
from pathlib import Path
import shutil
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--version',
        default=None,
        type=str,
        help='Overrides the Isotope Version from the config file.',
        metavar='IsotopeVersion')
    subparsers = parser.add_subparsers()

    # Isotope subcommands
    parser_isotope = subparsers.add_parser(
        'isotope', help='Create a release build of Isotope.')
    parser_isotope.add_argument('output', help='Zip file to create.')
    parser_isotope.set_defaults(command=common.Command.Isotope)

    # SDSetup subcommands
    parser_sdsetup = subparsers.add_parser(
        'sdsetup', help='Create a Isotope modules for SDSetup.')
    parser_sdsetup.add_argument(
        'output', help='Directory to output modules to.')
    parser_sdsetup.add_argument(
        '-a', '--auto',
        action='store_true',
        default=False,
        help='Perform an auto build.')
    parser_sdsetup.set_defaults(command=common.Command.SDSetup)

    # Isotope Minimal subcommands
    parser_isotope = subparsers.add_parser(
        'isotope-mini', help='Create a release build of Isotope Minimal.')
    parser_isotope.add_argument('output', help='Zip file to create.')
    parser_isotope.set_defaults(command=common.Command.IsotopeMinimal)

    # Isotope with patches subcommands
    parser_isotope_patches = subparsers.add_parser(
        'isotope-patches', help='Create a release build of Isotope with patches.')
    parser_isotope_patches.add_argument('output', help='Zip file to create.')
    parser_isotope_patches.set_defaults(command=common.Command.IsotopePatches)

    # Isotope minimal with patches subcommands
    parser_isotope_minimal_patches = subparsers.add_parser(
        'isotope-mini-patches', help='Create a release build of Isotope Minimal with patches.')
    parser_isotope_minimal_patches.add_argument('output', help='Zip file to create.')
    parser_isotope_minimal_patches.set_defaults(command=common.Command.IsotopeMinimalPatches)

    # Parse arguments
    args = parser.parse_args()

    if not hasattr(args, 'command'):
        parser.print_help()
        sys.exit()

    return args


def get_isotope_version(args):
    if args.version is not None:
        return args.version
    return config.version


def init_version_messages(args, isotope_version):
    if args.command == common.Command.Isotope:
        return [f'Isotope {isotope_version} built with:']
    elif args.command == common.Command.SDSetup and not args.auto:
        return ['SDSetup Modules built with:']
    elif args.command == common.Command.IsotopeMinimal:
        return [f'Isotope Minimal {isotope_version} built with:']
    elif args.command == common.Command.IsotopePatches:
        return [f'Isotope with Patches {isotope_version} built with:']
    elif args.command == common.Command.IsotopeMinimalPatches:
        return [f'Isotope Minimal with Patches {isotope_version} built with:']
    return []


if __name__ == '__main__':
    args = parse_args()

    temp_directory = common.generate_temp_path()
    common.mkdir(temp_directory)
    isotope_version = get_isotope_version(args)

    auto_build = False
    if hasattr(args, 'auto'):
        auto_build = args.auto

    version_messages = init_version_messages(args, isotope_version)

    build_messages = modules.build(
        temp_directory, isotope_version, args.command, auto_build)

    common.delete(args.output)

    if build_messages is not None:
        version_messages += build_messages

        if args.command == common.Command.SDSetup:
            common.move(temp_directory, args.output)
        else:
            shutil.make_archive(
                Path(args.output).stem,
                'zip',
                temp_directory)

        for message in version_messages:
            print(message)

    common.delete(Path.cwd().joinpath('tmp'))
