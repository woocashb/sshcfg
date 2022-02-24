#!/usr/bin/python

import jinja2
import sys
import re
import argparse
import pathlib


class SSHConfigFile(object):
    def __init__(self, ssh_config_path):
        self.path = pathlib.Path(ssh_config_path)
    #
    # def add(self, ssh_config_entry):
    #     with open(self.path, "a") as f_handle:
    #         f_handle.write(str(ssh_config_entry))

    def add(self, host, hostname, user, proxy_command=None):
        new_entry = SSHConfigEntry(host, hostname, user, proxy_command)
        with open(self.path, "a") as f_handle:
            f_handle.write("{}\n".format(str(new_entry)))

    def list(self, sought_entry=None):
        with open(self.path) as f_handle:
            f_contents = f_handle.read()
            entries = []
            for entry_match in re.finditer(SSHConfigEntry.entry_regex, f_contents):
                host = entry_match.group(1)
                hostname = entry_match.group(2)
                user = entry_match.group(3)
                proxy_command = entry_match.group(4) if len(entry_match.groups()) == 4 else None
                entries.append(SSHConfigEntry(host, hostname, user, proxy_command))
            if sought_entry:
                for entry in entries:
                    if entry.host == sought_entry:
                      print(entry)
            else:
                for entry in entries:
                    print(entry)

    def remove(self, ssh_config_entry):
        pass


class SSHConfigEntry(object):
    def __init__(self, host, hostname, user, proxy_command=None):
        self.host = host
        self.hostname = hostname
        self.user = user
        self.proxy_command = proxy_command
    entry_regex = re.compile(\
"Host (.*)\n\
\s*{0} (.*?)\n\s*{0} (.*?)\n(?:\s*{0} (.*?)\n)?".format("(?:hostname|proxycommand|user|port)"), flags=re.I | re.M)

    entry_template = jinja2.Template("""\n
Host {{ ssh_host }}
    HostName {{ ssh_hostname }}
    User {{ ssh_user }}
    {%- if ssh_proxy_command %}
    ProxyCommand {{ ssh_proxy_command }}
    {%- endif -%}
    """)

    def __str__(self):
        return (SSHConfigEntry.entry_template.render(ssh_host=self.host, ssh_hostname=self.hostname,\
              ssh_user=self.user, ssh_proxy_command=self.proxy_command))
    def is_valid_entry(self):
        pass

ssh_config_file = SSHConfigFile("./.ssh/config.dev")
# ssh_config_file.list()

ssh_entry_instance = SSHConfigEntry("dziczek", "192.168.2.9", "lboczkaja", "kocmołuch")

parser = argparse.ArgumentParser(description="Manage ssh config entries")
MANDATORY_ARGS = ('host', 'hostname', 'user')

parser.add_argument('-a', '--add', nargs=len(MANDATORY_ARGS),
                    metavar=MANDATORY_ARGS,
                    help='add new ssh config entry')

parser.add_argument('proxy_command', nargs='?', default=None)
parser.add_argument('-l', '--list', action='store_true', help='list ssh config entries')
parser.add_argument('-s', '--search', nargs=1, metavar='sought_entry', help='list ssh config entries')
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.list:
    ssh_config_file.list()

if args.search:
    ssh_config_file.list(args.search[0])

if args.add:
    ssh_config_file.add(*args.add)
