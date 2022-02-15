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

parser = argparse.ArgumentParser(description="Manage ssh config entries")
MANDATORY_ARGS = ('host', 'hostname', 'user')
for mandatory_arg in MANDATORY_ARGS:
    parser.add_argument(mandatory_arg)
parser.add_argument('proxy_command', nargs='?', default=None)
ssh_cfg_entry = parser.parse_args()

ssh_entry_instance = jinja2.Template(ssh_entry_template)
with open(ssh_config_path, 'a') as ssh_config_fd:
    ssh_config_fd.write(ssh_entry_instance.render(ssh_host=ssh_cfg_entry.host, ssh_hostname=ssh_cfg_entry.hostname, ssh_user=ssh_cfg_entry.user, ssh_proxy_command=ssh_cfg_entry.proxy_command))
