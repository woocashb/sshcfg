#!/usr/bin/python

import sys
import re
import argparse
import pathlib
import colorama
import jinja2
import re
import getpass
import pathlib
import fabric
import paramiko

class SSHConfigFile(object):
    def __init__(self, ssh_config_path):
        self.path = pathlib.Path(ssh_config_path)
        self.contents = self.path.read_text()
        self._get_entries()

    def _get_entries(self):
        self.entries = []
        for entry_match in re.finditer(SSHConfigEntry.entry_regex, self.contents):
                self.host = entry_match.group(1)
                self.hostname = entry_match.group(2)
                self.user = entry_match.group(3)
                self.proxy_command = entry_match.group(4) if len(entry_match.groups()) == 4 else None
                self.entries.append(SSHConfigEntry(self.host, self.hostname, self.user, self.proxy_command))

    def add(self, host, hostname, user, proxy_command=None):
        new_entry = SSHConfigEntry(host, hostname, user, proxy_command)
        for entry in self.entries:
            if new_entry.host == entry.host:
                print(f'Host "{new_entry.host}" already exists!')
                sys.exit(1)
        with open(self.path, "a") as f_handle:
            f_handle.write("{}\n".format(str(new_entry)))
        try:
            ssh_client = fabric.Connection(host=hostname, user=user).run('ls', hide=True)
        except paramiko.ssh_exception.AuthenticationException:
            self.add_authorized_key(hostname, user)


    def add_authorized_key(self, hostname, user):
        password =  getpass.getpass(f"Enter password for {self.user}@{self.hostname}:")
        ssh_client = fabric.Connection(host=hostname, user=user ,connect_kwargs={"password": password})
        public_key = open(pathlib.Path.home() / '.ssh/id_rsa.pub').read()
        run_add_public_key = ssh_client.run(f'echo "{public_key}" >> $HOME/.ssh/authorized_keys', hide=True)
        if run_add_public_key.return_code == 0:
            print(f"Added ssh public key to {self.hostname} authorized_keys")
        else:
            print(f"An error occured trying to add ssh public key to {self.hostname} authorized_keys - return_core: {run_add_public_key.return_code}")

    def list(self, verbose=False):
        if verbose:
            for index, entry in enumerate(self.entries, start=1):
                if index % 2 == 0:
                    print(f"{colorama.Fore.BLUE} {entry} {colorama.Style.RESET_ALL}")
                else:
                      print(f"{colorama.Fore.GREEN} {entry} {colorama.Style.RESET_ALL}")
        else:
            for index, entry in enumerate(self.entries, start=1):
                if index % 2 == 0:
                   print(f"{colorama.Fore.BLUE}{entry.host} {entry.hostname} {entry.user} {entry.proxy_command or ''} {colorama.Style.RESET_ALL}")
                else:
                  print(f"{colorama.Fore.GREEN}{entry.host} {entry.hostname} {entry.user} {entry.proxy_command or ''} {colorama.Style.RESET_ALL}")

    def search(self, sought_entry):
        # Check if argument is an IP address and if so try to match against entry hostname instead
        if re.search(r'^[0-9]{1,3}(\.[0-9]{1,3}){3}$', sought_entry):
            for entry in self.entries:
                if sought_entry == entry.hostname:
                    print(f"{colorama.Fore.GREEN} {entry} {colorama.Style.RESET_ALL}")
                    return True
        else:
            for entry in self.entries:
                if sought_entry == entry.host:
                    print(f"{colorama.Fore.GREEN} {entry} {colorama.Style.RESET_ALL}")
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
parser.add_argument('-v', '--verbose', action="store_true", help="list ssh config entries in brief format")
parser.add_argument('-f', '--config-file', nargs=1, help="Specify path to ssh config file")

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

if args.config_file:
    ssh_config_file = SSHConfigFile(*args.config_file)
else:
    ssh_config_file = SSHConfigFile(pathlib.Path.home() / ".ssh/config")

if args.list and not args.verbose:
    ssh_config_file.list()

if args.list and args.verbose:
    ssh_config_file.list(args.verbose)

if args.sought_entry:
    ssh_config_file.search(args.sought_entry)

if args.add:
    ssh_config_file.add(*args.add)

if args.remove:
    ssh_config_file.remove(args.remove)

if args.update:
    ssh_config_file.update(*args.update)
