from __future__ import unicode_literals
from __future__ import print_function
import subprocess
import os
from prompt_toolkit.shortcuts import get_input
import click


class NetMeta(type):
    def __new__(cls, *args, **kwargs):
        return super(NetMeta, cls).__new__(cls, *args, **kwargs)


class NetWorkCommands(object):
    __metaclass__ = NetMeta
    # base_if_path = "/etc/sysconfig/network-scripts/"
    # route_file = '/etc/rc.local'
    base_if_path = "./network_tool/"
    route_file = '1.txt'
    func_map = {
        'list ips': 'list_ips',
        'list routes': 'list_routes',
        'list cards': 'list_cards',
        'get ip': 'get_ip',
        'get route': 'get_route',
        'set ip': 'set_ip',
        'set route': 'set_route',
        'set ns': 'set_ns',
        'del_ip': 'del_ip',
        'del_route': 'del_route'
    }

    def run_shell(self, cmd):
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = ps.communicate()
        return stdout, stderr, ps.returncode

    def secho(self, out, error, code, pager=False):
        if not code:
            if pager:
                click.echo_via_pager(out)
            else:
                click.secho(out, fg='green')
        else:
            click.secho(error, fg='red')

    def parse(self, instruction):
        """
        :type instruction str
        """
        token = instruction.split(' ')
        func_name = token[0] if len(token) == 1 else "{} {}".format(token[0], token[1])
        func_name = self.func_map.get(func_name)
        if not func_name:
            raise KeyError('error instruction!')
        func = self.__getattribute__(func_name)
        if not func:
            raise NotImplementedError('not implemented!')
        return func

    def list_ips(self):
        out, error, code = self.run_shell('ifconfig -a')
        self.secho(out, error, code, pager=True)

    def list_routes(self):
        pass

    def list_cards(self):
        out, error, code = self.run_shell('ls /sys/class/net/')
        self.secho(out, error, code)

    def get_ip(self):
        eth = get_input('please input the eth name:')
        out, error, code = self.run_shell('ifconfig {}'.format(eth))
        self.secho(out, error, code)

    def get_route(self):
        pass

    def set_ip(self):
        eth = get_input('network card:')
        mode = get_input('select the mode [dhcp(d)/static(s)]:')
        if mode == 'static' or mode == 's':
            ip = get_input('ip:')
            mask = get_input('mask:')
            gateway = get_input('gateway:')
            click.secho('configuration information:\n'
                        'eth:{}\n'
                        'ip:{}\n'
                        'mask:{}\n'
                        'gateway:{}\n'.format(eth, ip, mask, gateway), fg='green')
            ret = get_input('Please confirm the above information [y/n]:')
            if ret.lower() == 'y':
                self.set_ip_static(eth, ip, mask, gateway)
                click.secho('successful!', fg='green')
            else:
                click.secho('cancel!', fg='red')
        elif mode == 'dhcp' or mode == 'd':
            click.secho('configuration information:\n'
                        'eth:{}\n'.format(eth), fg='green')
            ret = get_input('Please confirm the above information [y/n]:')
            if ret.lower() == 'y':
                self.set_ip_dhcp(eth)
                click.secho('successful!', fg='green')
            else:
                click.secho('cancel!', fg='red')
        else:
            click.secho('Please select an available option!', fg='red')

    def set_route(self):
        pass

    def set_ns(self):
        pass

    def del_ip(self):
        pass

    def del_route(self):
        pass

    def set_ip_static(self, eth, ip, mask, gateway):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=static\n' \
               'ONBOOT=YES\n' \
               'IPADDR={}\n' \
               'NETMASK={}\n' \
               'GATEWAY={}\n'.format(eth, ip, mask, gateway)
        with open(os.path.join(self.base_if_path, 'ifcfg-{}'.format(eth)), 'w') as w:
            w.write(info)

    def set_ip_dhcp(self, eth):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=DHCP\n' \
               'ONBOOT=YES'.format(eth)
        with open(os.path.join(self.base_if_path, 'ifcfg-{}'.format(eth)), 'w') as w:
            w.write(info)

    def run_cmd(self, text):
        self.parse(text)()
