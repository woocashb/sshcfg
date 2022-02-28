#!/usr/bin/python

import sys
import re
import argparse
import pathlib
import jinja2

class SSHConfigFile(object):
    def __init__(self, ssh_config_path):
        self.path = pathlib.Path(ssh_config_path)
        self.contents = self.path.read_text()
        self._get_entries()

    def _get_entries(self):
        self.entries = []
        for entry_match in re.finditer(SSHConfigEntry.entry_regex, self.contents):
                host = entry_match.group(1)
                hostname = entry_match.group(2)
                user = entry_match.group(3)
                proxy_command = entry_match.group(4) if len(entry_match.groups()) == 4 else None
                self.entries.append(SSHConfigEntry(host, hostname, user, proxy_command))

    def add(self, host, hostname, user, proxy_command=None):
        new_entry = SSHConfigEntry(host, hostname, user, proxy_command)
        with open(self.path, "a") as f_handle:
            f_handle.write("{}\n".format(str(new_entry)))

    def list(self):
        for entry in self.entries:
            print(entry)

    def search(self, sought_entry):
        for entry in self.entries:
            if sought_entry == entry.host:
                print(entry)
        else:
            print("No such entry found.")

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

parser = argparse.ArgumentParser(description="Manage ssh config entries")
MANDATORY_ARGS = ('host', 'hostname', 'user')

parser.add_argument('-a', '--add', nargs=len(MANDATORY_ARGS),
                    metavar=MANDATORY_ARGS,
                    help='add new ssh config entry')

parser.add_argument('proxy_command', nargs="?", default=None)
parser.add_argument('-l', '--list', action="store_true", help='list all ssh config entries within config file')
parser.add_argument('-s', '--search', dest="sought_entry", help='search for particular entry within config file')
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.list:
    ssh_config_file.list()

if args.sought_entry:
    ssh_config_file.search(args.sought_entry)

if args.add:
    ssh_config_file.add(*args.add)
