#!/usr/bin/python

import jinja2
import os
import sys
import re
import argparse
from pathlib import Path

ssh_config_path = Path("./.ssh/config.dev")

ssh_entry_options = "(hostname|proxycommand|user|port)"

ssh_entry_regex = re.compile(\
"Host (.*)\n \
(\s*{0} .*)*".format(ssh_entry_options)
, flags=re.I | re.M)

ssh_entry_template = """\n
Host {{ ssh_host }}
  HostName {{ ssh_hostname }}
  User {{ ssh_user }}
  {%- if ssh_proxy_command %}
  ProxyCommand {{ ssh_proxy_command }}
  {%- endif -%}
"""


def add_entry(add_args):
    ssh_host, ssh_hostname, ssh_user = add_args.add
    ssh_proxy_command = add_args.proxy_command
    ssh_entry_instance = jinja2.Template(ssh_entry_template)
    with open(ssh_config_path, 'a') as ssh_config_fd:
        ssh_config_fd.write(ssh_entry_instance.render(ssh_host=ssh_host, ssh_hostname=ssh_hostname, ssh_user=ssh_user, ssh_proxy_command=ssh_proxy_command))

def list_entries():
    with open(ssh_config_path) as ssh_config_fd:
        print(ssh_config_fd.read())

parser = argparse.ArgumentParser(description="Manage ssh config entries")
MANDATORY_ARGS = ('host', 'hostname', 'user')

parser.add_argument('-a', '--add', nargs=len(MANDATORY_ARGS),
                    metavar=MANDATORY_ARGS,
                    help='add new ssh config entry')

parser.add_argument('proxy_command', nargs='?', default=None)
parser.add_argument('-l', '--list', action="store_true", help='list ssh config entries')


args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.add:
  add_entry(args)

if args.list:
  list_entries()


# if args.list:
#     list_entries()
