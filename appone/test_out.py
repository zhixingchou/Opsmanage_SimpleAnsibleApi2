import json
from ansible_api import AnsibleAPI
from ansible_interface import AnsiInterface

resource = [
    {"hostname": "192.168.2.159", "port": "22", "username": "root", "password": "met21sh159", "ip": '192.168.2.159'}]
interface = AnsiInterface(resource)

# print interface.exec_setup_2('192.168.2.159')



interface.handle_cmdb_data('192.168.2.159')


# data_list = []
# for k, v in json.loads(json.dumps(interface.exec_setup_2('192.168.2.159'))).items():
#     if k == "success":
#         for x, y in v.items():
#             cmdb_data = {}
#             data = y.get('ansible_facts')
#             disk_size = 0
#             cpu = data['ansible_processor'][-1]
#             for k, v in data['ansible_devices'].items():
#                 if k[0:2] in ['sd', 'hd', 'ss', 'vd']:
#                     disk = int((int(v.get('sectors')) * int(v.get('sectorsize'))) / 1024 / 1024 / 1024)
#                     disk_size = disk_size + disk
#             cmdb_data['serial'] = data['ansible_product_serial'].split()[0]
#             cmdb_data['ip'] = x
#             cmdb_data['cpu'] = cpu.replace('@', '')
#             ram_total = str(data['ansible_memtotal_mb'])
#             if len(ram_total) == 4:
#                 ram_total = ram_total[0] + 'GB'
#             elif len(ram_total) == 5:
#                 ram_total = ram_total[0:2] + 'GB'
#             elif len(ram_total) > 5:
#                 ram_total = ram_total[0:3] + 'GB'
#             else:
#                 ram_total = ram_total + 'MB'
#             cmdb_data['ram_total'] = ram_total
#             cmdb_data['disk_total'] = str(disk_size) + 'GB'
#             cmdb_data['system'] = data['ansible_distribution'] + ' ' + data['ansible_distribution_version'] + ' ' + \
#                                   data['ansible_userspace_bits']
#             cmdb_data['model'] = data['ansible_product_name'].split(':')[0]
#             cmdb_data['cpu_number'] = data['ansible_processor_count']
#             cmdb_data['vcpu_number'] = data['ansible_processor_vcpus']
#             cmdb_data['cpu_core'] = data['ansible_processor_cores']
#             cmdb_data['hostname'] = data['ansible_hostname']
#             cmdb_data['kernel'] = str(data['ansible_kernel'])
#             cmdb_data['manufacturer'] = data['ansible_system_vendor']
#             if data['ansible_selinux']:
#                 cmdb_data['selinux'] = data['ansible_selinux'].get('status')
#             else:
#                 cmdb_data['selinux'] = 'disabled'
#             cmdb_data['swap'] = str(data['ansible_swaptotal_mb']) + 'MB'
#             cmdb_data['status'] = 0
#             data_list.append(cmdb_data)
#         if data_list:
#             print data_list
#
#         print "-----------------------------------------------"
