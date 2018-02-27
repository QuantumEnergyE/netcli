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
        'list ips': 'list_ips',
        'list routes': 'list_routes',
        'list cards': 'list_cards',
        'get ip': 'get_ip',
        'get route': 'get_route',
        'set ifcfg': 'set_ifcfg',
        'set route': 'set_route',
        'set ns': 'set_ns',
        'set bond': 'set_bond',
        'set bridge': 'set_bridge',
        'del ip': 'del_ip',
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

    def list_ips(self):
        out, error, code = self.run_shell('ifconfig -a')
        self.secho(out, error, code, pager=True)

    def list_routes(self):
        out, error, code = self.run_shell('ip route show')
        self.secho(out, error, code, pager=True)

    def list_cards(self):
        out, error, code = self.run_shell('ls /sys/class/net/')
        self.secho(out, error, code)

    def get_ip(self):
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

    def set_ifcfg(self):
        eth = get_input('network card:')
        mode = get_input('select the mode [dhcp(d)/static(s)/bond(b)]/bridge(e):')
        if mode == 'static' or mode == 's':
            ip = get_input('ip:')
            mask = get_input('mask:')
            gateway = get_input('gateway:')
            self.set_ip_static(eth, ip, mask, gateway)
        elif mode == 'dhcp' or mode == 'd':
            self.set_ip_dhcp(eth)
        elif mode == 'bond' or mode == 'b':
            bond = get_input('bond name:')
            nm_controlled = get_input('nm_controlled [yes/no]:')
            self.set_ip_bond(eth, bond, nm_controlled)
        elif mode == 'bridge' or mode == 'e':
            bridge = get_input('bridge name, If this option is empty, '
                               'the bridge configuration of the network card will be deleted:')
            self.add_if_to_bridge(eth, bridge)
        else:
            click.secho('Please select an available option!', fg='red')

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
        bond = get_input('bond device [example=>bond0]:')
        cards, _, _ = self.run_shell('ls /sys/class/net/')
        mode = get_input('bond mode:')
        miimon = get_input('bond miimon:')
        ipaddr = get_input('ipaddr:')
        netmask = get_input('netmask:')
        onboot = get_input('onboot [yes/no]:')
        mtu = get_input('mtu:')
        nm_controlled = get_input('nm_controlled:')
        info = 'DEVICE={}\n' \
               'BONDING_OPTS=\'mode={} mimmon={}\'\n' \
               'IPADDR={}\n' \
               'NETMASK={}\n' \
               'ONBOOT=yes\n' \
               'MTU={}\n' \
               'NM_CONTROLLED={}\n' \
               'HOTPLUG={}'.format(bond, mode, miimon, ipaddr, netmask, onboot, mtu, nm_controlled)
        click.secho('configuration information:\n'
                    '{}'.format(info), fg='yellow')
        ret = get_input('Please confirm the above information [y/n]:')
        if ret.lower() == 'y':
            bond_file = os.path.join(self.base_if_path, 'ifcfg-{}'.format(bond))
            if os.path.exists(bond_file):
                ret = get_input('bond conf ifcfg-{} is exist, do you want to recover it! [y/n]:'.format(bond))
                if ret.lower() != 'y':
                    return
            with open(bond_file, 'w') as w:
                w.write(info)
            ret = get_input('do you want bind devices to {} [y/n]:'.format(bond))
            if ret.lower() == 'y':
                slave_devices = get_input('please select the slave devices from "{}" [example=>ens3 ens4]:'.format(
                    ';'.join(cards.split('\n'))))
                for slave_device in slave_devices.split():
                    self.set_ip_bond(slave_device, bond)
            else:
                click.secho('you can bind device to bond by execute \'set ifcfg\'', fg='green')

    def del_ip(self):
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

    def set_ip_static(self, eth, ip, mask, gateway):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=static\n' \
               'ONBOOT=yes\n' \
               'IPADDR={}\n' \
               'NETMASK={}\n' \
               'GATEWAY={}'.format(eth, ip, mask, gateway)
        self.update_ifcfg(eth, info)

    def set_ip_dhcp(self, eth):
        info = 'DEVICE={}\n' \
               'BOOTPROTO=dhcp\n' \
               'ONBOOT=yes'.format(eth)
        self.update_ifcfg(eth, info)

    def set_ip_bond(self, slave, bond, nm_controlled='no'):
        info = 'MASTER={}\n' \
               'DEVICE={}\n' \
               'ONBOOT=yes\n' \
               'SLAVE=yes\n' \
               'NM_CONTROLLED={}'.format(bond, slave, nm_controlled)
        self.update_ifcfg(slave, info)

    def add_if_to_bridge(self, eth, bridge):
        eth_file = os.path.join(self.base_if_path, 'ifcfg-{}'.format(eth))
        if not os.path.exists(eth_file):
            click.secho('can\'t find configuration file of {}, please set ifcfg with dhcp or static first!'.format(eth))
        if not bridge.strip():
            click.secho('network card {} will be removed from bridge'.format(eth))
            command = 'sed -i \'/^{}/d\' {}'.format('BRIDGE', eth_file)
            print(command)
            out, error, code = self.run_shell(command)
            self.secho(out, error, code)
            return
        ret = get_input('interface {} will be added to bridge {} [y/n]:'.format(eth, bridge))
        if ret.lower() == 'y':
            #TODO
            out, error, code = self.run_shell('sed -i \'s/^BRIDGE.*$/BRIDGE={}\' {}'.format(bridge, eth_file))
            self.secho(out, error, code)

    def update_ifcfg(self, device, info):
        click.secho('configuration information:\n{}'.format(info), fg='yellow')
        ret = get_input('Please confirm the above information [y/n]:')
        if ret.lower() == 'y':
            with open(os.path.join(self.base_if_path, 'ifcfg-{}'.format(device)), 'w') as w:
                w.write(info)
            click.secho('successful!', fg='green')
        else:
            click.secho('cancel!', fg='green')

    def restart_network(self):
        ret = get_input('The network service will be restarted! [y/n]:')
        if ret.lower() == 'y':
            out, error, code = self.run_shell('systemctl restart network')
            self.secho(out, error, code)

    def set_bridge(self):
        bridge = get_input('bridge device [example=>br0]:')
        mode = get_input('[dhcp(d)/static(s)]:')
        if mode == 'dhcp' or mode == 'd':
            info = 'device={}\n' \
                   'TYPE=Bridge\n' \
                   'BOOTPROTO=dhcp\n' \
                   'ONBOOT=yes'.format(bridge)
        else:
            ip = get_input('ip:')
            mask = get_input('mask:')
            gateway = get_input('gateway:')
            info = 'device={}\n' \
                   'TYPE=Bridge\n' \
                   'BOOTPROTO=static\n' \
                   'ONBOOT=yes\n' \
                   'IPADDR={}\n' \
                   'NETMASK={}\n' \
                   'GATEWAY={}'.format(bridge, ip, mask, gateway)
        click.secho('configuration information:\n'
                    '{}'.format(info), fg='yellow')
        ret = get_input('Please confirm the above information [y/n]:')
        if ret.lower() == 'y':
            bridge_file = os.path.join(self.base_if_path, 'ifcfg-{}'.format(bridge))
            if os.path.exists(bridge_file):
                ret = get_input('bridge conf ifcfg-{} is exist, do you want to recover it! [y/n]:'.format(bridge))
                if ret.lower() != 'y':
                    return
            with open(bridge_file, 'w') as w:
                w.write(info)
            click.secho('Successful, you can add device to the bridge by execute \'set ifcfg\'', fg='green')

    def run_cmd(self, text):
        self.parse(text)()
