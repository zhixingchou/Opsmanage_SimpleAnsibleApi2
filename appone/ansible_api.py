# -*- coding:utf-8 -*-

import os
import sys
import logging
import json

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase


logger = logging.basicConfig()

class ResultsCollector(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result


        # host = result._host
        # print u"%s 执行结果" % result._task
        # print json.dumps({host.name: result._result}, indent=4)


        # host = result._host
        # # print u"%s 执行结果" % result._task
        # # print json.dumps({host.name: result._result}, indent=4)
        # data_list = []
        # for x, y in json.loads(json.dumps({host.name: result._result})).items():
        #     cmdb_data = {}
        #     data = y.get('ansible_facts')
        #     disk_size = 0
        #     cpu = data['ansible_processor'][-1]
        #     for k, v in data['ansible_devices'].items():
        #         if k[0:2] in ['sd', 'hd', 'ss', 'vd']:
        #             disk = int((int(v.get('sectors')) * int(v.get('sectorsize'))) / 1024 / 1024 / 1024)
        #             disk_size = disk_size + disk
        #     cmdb_data['serial'] = data['ansible_product_serial'].split()[0]
        #     cmdb_data['ip'] = x
        #     cmdb_data['cpu'] = cpu.replace('@', '')
        #     ram_total = str(data['ansible_memtotal_mb'])
        #     if len(ram_total) == 4:
        #         ram_total = ram_total[0] + 'GB'
        #     elif len(ram_total) == 5:
        #         ram_total = ram_total[0:2] + 'GB'
        #     elif len(ram_total) > 5:
        #         ram_total = ram_total[0:3] + 'GB'
        #     else:
        #         ram_total = ram_total + 'MB'
        #     cmdb_data['ram_total'] = ram_total
        #     cmdb_data['disk_total'] = str(disk_size) + 'GB'
        #     cmdb_data['system'] = data['ansible_distribution'] + ' ' + data['ansible_distribution_version'] + ' ' + \
        #                           data['ansible_userspace_bits']
        #     cmdb_data['model'] = data['ansible_product_name'].split(':')[0]
        #     cmdb_data['cpu_number'] = data['ansible_processor_count']
        #     cmdb_data['vcpu_number'] = data['ansible_processor_vcpus']
        #     cmdb_data['cpu_core'] = data['ansible_processor_cores']
        #     cmdb_data['hostname'] = data['ansible_hostname']
        #     cmdb_data['kernel'] = str(data['ansible_kernel'])
        #     cmdb_data['manufacturer'] = data['ansible_system_vendor']
        #     if data['ansible_selinux']:
        #         cmdb_data['selinux'] = data['ansible_selinux'].get('status')
        #     else:
        #         cmdb_data['selinux'] = 'disabled'
        #     cmdb_data['swap'] = str(data['ansible_swaptotal_mb']) + 'MB'
        #     cmdb_data['status'] = 0
        #     data_list.append(cmdb_data)
        # if data_list:
        #     print data_list
        #
        #
        # print "-----------------------------------------------"










    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result


class MyInventory(Inventory):
    """
    this is my ansible inventory object.
    """

    def __init__(self, resource, loader, variable_manager):
        """
        resource的数据格式是一个列表字典，比如
            {
                "group1": {
                    "hosts": [{"hostname": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...],
                    "vars": {"var1": value1, "var2": value2, ...}
                }
            }

        如果你只传入1个列表，这默认该列表内的所有主机属于my_group组,比如
            [{"hostname": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...]
        """
        self.resource = resource
        self.inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=[])
        self.gen_inventory()

    def my_add_group(self, hosts, groupname, groupvars=None):
        """
        add hosts to a group
        """
        my_group = Group(name=groupname)

        # if group variables exists, add them to group
        if groupvars:
            for key, value in groupvars.iteritems():
                my_group.set_variable(key, value)

                # add hosts to group
        for host in hosts:
            # set connection variables
            hostname = host.get("hostname")
            hostip = host.get('ip', hostname)
            hostport = host.get("port")
            username = host.get("username")
            password = host.get("password")
            ssh_key = host.get("ssh_key")
            my_host = Host(name=hostname, port=hostport)
            my_host.set_variable('ansible_ssh_host', hostip)
            my_host.set_variable('ansible_ssh_port', hostport)
            my_host.set_variable('ansible_ssh_user', username)
            my_host.set_variable('ansible_ssh_pass', password)
            my_host.set_variable('ansible_ssh_private_key_file', ssh_key)

            # set other variables
            for key, value in host.iteritems():
                if key not in ["hostname", "port", "username", "password"]:
                    my_host.set_variable(key, value)
                    # add to group
            my_group.add_host(my_host)

        self.inventory.add_group(my_group)

    def gen_inventory(self):
        """
        add hosts to inventory.
        """
        if isinstance(self.resource, list):
            self.my_add_group(self.resource, 'default_group')
        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.iteritems():
                self.my_add_group(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("vars"))


class AnsibleAPI(object):
    """
    This is a General object for parallel execute modules.
    """

    def __init__(self, resource, *args, **kwargs):
        self.resource = resource
        self.inventory = None
        self.variable_manager = None
        self.loader = None
        self.options = None
        self.passwords = None
        self.callback = None
        self.__initializeData()
        self.results_raw = {}

    def __initializeData(self):
        """
        初始化ansible
        """
        Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'timeout', 'remote_user',
                                         'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                         'sftp_extra_args',
                                         'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass',
                                         'verbosity',
                                         'check', 'listhosts', 'listtasks', 'listtags', 'syntax'])

        # initialize needed objects
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.options = Options(connection='smart', module_path='/usr/share/ansible', forks=100, timeout=10,
                               remote_user='root', ask_pass=False, private_key_file=None, ssh_common_args=None,
                               ssh_extra_args=None,
                               sftp_extra_args=None, scp_extra_args=None, become=None, become_method=None,
                               become_user='root', ask_value_pass=False, verbosity=None, check=False, listhosts=False,
                               listtasks=False, listtags=False, syntax=False)

        self.passwords = dict(sshpass=None, becomepass=None)
        self.inventory = MyInventory(self.resource, self.loader, self.variable_manager).inventory
        self.variable_manager.set_inventory(self.inventory)

    def run(self, host_list, module_name):
        """
        run module from andible ad-hoc.
        module_name: ansible module_name
        module_args: ansible module args
        """
        # create play with tasks
        play_source = dict(
            name="Ansible Play",
            hosts=host_list,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name))]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        # actually run it
        tqm = None
        self.callback = ResultsCollector()
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
            )
            tqm._stdout_callback = self.callback
            tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def run_playbook(self, host_list, role_name, role_uuid, temp_param):
        """
        run ansible palybook
        """
        try:
            self.callback = ResultsCollector()
            filenames = ['' + '/handlers/ansible/v1_0/sudoers.yml']  # playbook的路径
            template_file = ''  # 模板文件的路径
            if not os.path.exists(template_file):
                sys.exit()

            extra_vars = {}  # 额外的参数 sudoers.yml以及模板中的参数，它对应ansible-playbook test.yml --extra-vars "host='aa' name='cc' "
            host_list_str = ','.join([item for item in host_list])
            extra_vars['host_list'] = host_list_str
            extra_vars['username'] = role_name
            extra_vars['template_dir'] = template_file
            extra_vars['command_list'] = temp_param.get('cmdList')
            extra_vars['role_uuid'] = 'role-%s' % role_uuid
            self.variable_manager.extra_vars = extra_vars
            # actually run it
            executor = PlaybookExecutor(
                playbooks=filenames, inventory=self.inventory, variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options, passwords=self.passwords,
            )
            executor._tqm._stdout_callback = self.callback
            executor.run()
        except Exception as e:
            print "error:",e.message

    def get_result(self):
        self.results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.callback.host_ok.items():
            self.results_raw['success'][host] = result._result

        for host, result in self.callback.host_failed.items():
            self.results_raw['failed'][host] = result._result.get('msg') or result._result

        for host, result in self.callback.host_unreachable.items():
            self.results_raw['unreachable'][host] = result._result['msg']

        return self.results_raw