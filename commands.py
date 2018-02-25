from __future__ import unicode_literals
from __future__ import print_function
import subprocess
import platform
import os


class NetMeta(type):
    def __new__(cls, *args, **kwargs):
        return super(NetMeta, cls).__new__(cls, *args, **kwargs)


class NetWorkCommands(object):
    __metaclass__ = NetMeta
    # base_if_path = "/etc/sysconfig/network-scripts/"
    # route_file = '/etc/rc.local'
    base_if_path = "./"
    route_file = '1.txt'
    func_map = {
        'list ips': 'list_ips',
        'list routes': 'list_routes',
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
        if platform.system() == 'Windows':
            print(stdout.decode('gbk'))
            print(stderr.decode('gbk'))
        else:
            print(stdout)
            print(stderr)
        return stdout, stderr, ps.returncode

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
        func()

    def list_ips(self):
        pass

    def list_routes(self):
        pass

    def get_ip(self, eth=None):
        if eth:
            return 'ifconfig {}'.format(eth)
        return 'ifconfig -a'

    def get_route(self):
        pass

    def set_ip(self):
        pass

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
        self.parse(text)
