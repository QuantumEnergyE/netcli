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
    base_if_path = "/etc/sysconfig/network-scripts/"
    route_file = '/etc/sysconfig/network-scripts/route-'
    func_map = {
        'list ifs': 'list_ifs',
        'list routes': 'list_routes',
        'list cards': 'list_cards',
        'get if': 'get_if',
        'get route': 'get_route',
        'set if': 'set_if',
        'set route': 'set_route',
        'set ns': 'set_ns',
        'set bond': 'set_bond',
        'set bridge': 'set_bridge',
        'del if': 'del_if',
        'del route': 'del_route',
        "restart network": 'restart_network'
    }

    def run_shell(self, cmd):
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = ps.communicate()
        return stdout, stderr, ps.returncode

    def secho(self, out, error, code, pager=False):
        if not code:
            if not out:
                click.secho('successful!', fg='green')
                return
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

    def list_ifs(self):
        out, error, code = self.run_shell('ifconfig -a')
        self.secho(out, error, code, pager=True)

    def list_routes(self):
        out, error, code = self.run_shell('ip route show')
        self.secho(out, error, code, pager=True)

    def list_cards(self):
        out, error, code = self.run_shell('ls /sys/class/net/')
        self.secho(out, error, code)

    def get_if(self):
        eth = get_input('please input the eth name:')
        out, error, code = self.run_shell('ifconfig {}'.format(eth))
        self.secho(out, error, code)

    def get_route(self):
        card = get_input('card name:')
        card_conf = self.route_file + card
        if not os.path.exists(card_conf):
            click.secho('can\'t find configure', fg='red')
            return
        with open(card_conf, 'r') as r:
            routes = r.read()
            click.secho(routes, fg='green')

    def set_if(self):
        eth = get_input('network card:')
        mode = get_input('select the mode [dhcp(d)/static(s)/bond(b)/bridge(e)]:')
        if mode == 'static' or mode == 's':
            ip = get_input('ip:')
            mask = get_input('mask:')
            gateway = get_input('gateway:')
            self.set_if_static(eth, ip, mask, gateway)
        elif mode == 'dhcp' or mode == 'd':
            self.set_if_dhcp(eth)
        elif mode == 'bond' or mode == 'b':
            bond = get_input('bond name:')
            self.add_if_to_bond(eth, bond)
        elif mode == 'bridge' or mode == 'e':
            bridge = get_input('bridge name:')
            self.add_if_to_bridge(eth, bridge)
        else:
            click.secho('Please select an available option!', fg='red')

    def set_if_static(self, eth, ip, mask, gateway):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=static\n' \
               'ONBOOT=yes\n' \
               'IPADDR={}\n' \
               'NETMASK={}\n' \
               'GATEWAY={}'.format(eth, ip, mask, gateway)
        self.update_ifcfg(eth, info)

    def set_if_dhcp(self, eth):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=dhcp\n' \
               'ONBOOT=yes'.format(eth)
        self.update_ifcfg(eth, info)

    def add_if_to_bond(self, slave, bond):
        info = 'MASTER={}\n' \
               'DEVICE={}\n' \
               'ONBOOT=yes\n' \
               'SLAVE=yes\n' \
               'NM_CONTROLLED=no'.format(bond, slave)
        self.update_ifcfg(slave, info)

    def add_if_to_bridge(self, eth, bridge):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=none\n' \
               'ONBOOT=yes\n' \
               'BRIDGE={}'.format(eth, bridge)
        self.update_ifcfg(eth, info)

    def update_ifcfg(self, device, info):
        click.secho('configuration information:\n{}'.format(info), fg='yellow')
        ret = get_input('Please confirm the above information [y/n]:')
        if ret.lower() == 'y':
            with open(os.path.join(self.base_if_path, 'ifcfg-{}'.format(device)), 'w') as w:
                w.write(info)
            click.secho('successful!', fg='green')
        else:
            click.secho('cancel!', fg='green')

    def set_route(self):
        net = get_input('net:')
        via = get_input('via:')
        dev = get_input('dev:')
        command = '{} via {} dev {}\n'.format(net, via, dev)
        # TODO: if the gw is exist, warning!
        click.secho('configuration information:\n'
                    '{}'.format(command), fg='yellow')
        ret = get_input('Please confirm the above information [y/n]:')
        if ret.lower() == 'y':
            with open(self.route_file + dev, 'a') as f:
                f.write(command)
            click.secho('successful', fg='green')

    def set_ns(self):
        pass

    def set_bond(self):
        cards, _, _ = self.run_shell('ls /sys/class/net/')
        bond = get_input('bond device [example=>bond0]:')
        bond_mode = get_input('bond mode:')
        miimon = get_input('bond miimon:')
        onboot = get_input('onboot [yes/no]:')
        mode = get_input('select the mode [dhcp(d)/static(s)//bridge(e)]:')

        if mode == 'dhcp' or mode == 'd':
            self.set_bond_dhcp(bond, bond_mode, miimon, onboot)
        elif mode == 'bridge' or mode == 'e':
            bridge = get_input('bridge name:')
            self.add_bond_to_bridge(bond, bond_mode, miimon, onboot, bridge)
        else:
            ipaddr = get_input('ipaddr:')
            netmask = get_input('netmask:')
            gateway = get_input('gateway:')
            self.set_bond_static(bond, bond_mode, miimon, ipaddr, netmask, gateway, onboot)

    def set_bond_static(self, bond, bond_mode, miimon, ipaddr, netmask, gateway, onboot):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=static\n' \
               'BONDING_OPTS=\'mode={} mimmon={}\'\n' \
               'IPADDR={}\n' \
               'NETMASK={}\n' \
               'GATEWAY={}\n' \
               'ONBOOT={}\n' \
               'NM_CONTROLLED=no\n' \
               'HOTPLUG=no'.format(bond, bond_mode, miimon, ipaddr, netmask, gateway, onboot)
        self.update_ifcfg(bond, info)

    def set_bond_dhcp(self, bond, bond_mode, miimon, on_boot):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=dhcp\n' \
               'BONDING_OPTS=\'mode={} mimmon={}\'\n' \
               'ONBOOT={}\n' \
               'NM_CONTROLLED=no\n' \
               'HOTPLUG=no'.format(bond, bond_mode, miimon, on_boot)
        self.update_ifcfg(bond, info)

    def add_bond_to_bridge(self, bond, bond_mode, miimon, on_boot, bridge):
        info = 'DEVICE={}\n' \
               'BONDING_OPTS=\'mode={} mimmon={}\'\n' \
               'ONBOOT={}\n' \
               'NM_CONTROLLED=no\n' \
               'HOTPLUG=no\n' \
               'BRIDGE={}'.format(bond, bond_mode, miimon, on_boot, bridge)
        self.update_ifcfg(bond, info)

    def set_bridge(self):
        bridge = get_input('bridge device [example=>br0]:')
        mode = get_input('[dhcp(d)/static(s)]:')
        if mode == 'dhcp' or mode == 'd':
            self.set_bridge_dhcp(bridge)
        else:
            ip = get_input('ip:')
            mask = get_input('mask:')
            gateway = get_input('gateway:')
            self.set_bridge_static(bridge, ip, mask, gateway)

    def set_bridge_static(self, bridge, ip, mask, gateway):
        info = 'device={}\n' \
               'TYPE=Bridge\n' \
               'BOOTPROTO=static\n' \
               'ONBOOT=yes\n' \
               'IPADDR={}\n' \
               'NETMASK={}\n' \
               'GATEWAY={}'.format(bridge, ip, mask, gateway)
        self.update_ifcfg(bridge, info)

    def set_bridge_dhcp(self, bridge):
        info = 'device={}\n' \
               'TYPE=Bridge\n' \
               'BOOTPROTO=dhcp\n' \
               'ONBOOT=yes'.format(bridge)
        self.update_ifcfg(bridge, info)

    def del_if(self):
        pass

    def del_route(self):
        net = get_input('net:')
        command = 'ip route show | grep {}'.format(net)
        out, error, code = self.run_shell(command)
        if not code and out:
            ret = get_input('route "{}" will be deleted! [y/n]:'.format(out.strip()))
            if ret.lower() == 'y':
                dev = out.split()[-1]
                route_file = os.path.join(self.route_file + dev)
                if not os.path.exists(route_file):
                    click.secho('route file can\'t find!')
                else:
                    command = 'sed -i \'/^{}/d\' {}'.format(net.replace('/', '\/'), route_file)
                    out, error, code = self.run_shell(command)
                    self.secho(out, error, code)
        else:
            click.secho('can\'t find route!', fg='red')

    def restart_network(self):
        ret = get_input('The network service will be restarted! [y/n]:')
        if ret.lower() == 'y':
            out, error, code = self.run_shell('systemctl restart network')
            self.secho(out, error, code)

    def run_cmd(self, text):
        self.parse(text)()
