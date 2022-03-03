#!/usr/bin/python

import sys
import re
import argparse
import pathlib
import colorama
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

    def list(self, brief=False):
        if brief:
            for index, entry in enumerate(self.entries, start=1):
                if index % 2 == 0:
                  # print("{2}{0} {1}{3}".format(entry.host, entry.hostname, entry.user, entry.proxy_command, colorama.Fore.BLUE, colorama.Style.RESET_ALL))
                   print(f"{colorama.Fore.BLUE}{entry.host} {entry.hostname} {entry.user} {entry.proxy_command or ''} {colorama.Style.RESET_ALL}")
                else:
                  print(f"{colorama.Fore.GREEN}{entry.host} {entry.hostname} {entry.user} {entry.proxy_command or ''} {colorama.Style.RESET_ALL}")

        else:
            for index, entry in enumerate(self.entries, start=1):
                if index % 2 == 0:
                    print(f"{colorama.Fore.BLUE} {entry} {colorama.Style.RESET_ALL}")
                else:
                      print(f"{colorama.Fore.GREEN} {entry} {colorama.Style.RESET_ALL}")
        # for entry in self.entries:
        #     print(entry)

    def search(self, sought_entry):
        for entry in self.entries:
            if sought_entry == entry.host:
                print(entry)
                return True
        print("No such entry found!")
        return False

    def remove(self, ssh_config_entry):
        for entry in self.entries:
            if entry.host == ssh_config_entry:
                self.entries.remove(entry)
        with open(self.path, "w") as f_handle:
            for entry in self.entries:
                f_handle.write("{}\n".format(str(entry)))

    def update(self, entry_host, new_host, new_hostname, new_user, new_proxy_command=None):
        for entry in self.entries:
            if entry.host == entry_host:
                self.remove(entry_host)
                self.add(new_host, new_hostname, new_user, new_proxy_command)
                return True
        print('No such entry found!')
        return False


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
parser.add_argument('-r', '--remove', help='remove entry from config file')
parser.add_argument('-u', '--update', nargs=len(MANDATORY_ARGS) + 1, help='update entry by given Host value')
parser.add_argument('-b', '--brief', action="store_true", help="list ssh config entries in brief format")

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.list and not args.brief:
    ssh_config_file.list()

if args.list and args.brief:
    ssh_config_file.list(args.brief)

if args.sought_entry:
    ssh_config_file.search(args.sought_entry)

if args.add:
    ssh_config_file.add(*args.add)

if args.remove:
    ssh_config_file.remove(args.remove)

if args.update:
    ssh_config_file.update(*args.update)
