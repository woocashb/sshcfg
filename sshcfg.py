#!/usr/bin/python

import jinja2
import os
import sys

def usage():
    print("Add new entry to ssh config at default location for current user\nUsage: {} Host Hostname User [ProxyCommand]".format(sys.argv[0]))

if not len(sys.argv) >= 4:
    print("Missing mandatory arguments!")
    usage()
    sys.exit(1)

ssh_config_path = os.path.expanduser("~/.ssh/config2")

ssh_config_entry = """
Host {{ ssh_host }}
  HostName {{ ssh_host_ip }}
  User {{ ssh_user }}
  {% if ssh_proxy_command -%}
  ProxyCommand {{ ssh_proxy_command }}
  {%- endif -%}
"""

ssh_host_arg = sys.argv[1]
ssh_host_ip_arg = sys.argv[2]
ssh_user_arg = sys.argv[3]
if len(sys.argv) == 5:
  ssh_proxy_command_arg = sys.argv[4]
else:
  ssh_proxy_command_arg = None


ssh_config_entry_template = jinja2.Template(ssh_config_entry)
with open(ssh_config_path, 'a') as ssh_config_fd:
    ssh_config_fd.write(ssh_config_entry_template.render(ssh_host=ssh_host_arg, ssh_host_ip=ssh_host_ip_arg, ssh_user=ssh_user_arg, ssh_proxy_command=ssh_proxy_command_arg))
