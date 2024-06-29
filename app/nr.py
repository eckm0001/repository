""" nornir functions """

# note that these imports are only needed if you are annotating your code with types
#from typing import Dict
import logging
from nornir import InitNornir
#from nornir.core.inventory import Host
from nornir.core.task import (
#    AggregatedResult,
#    MultiResult,
    Result,
    Task,
    )
from nornir_napalm.plugins.tasks import (
#    napalm_configure,
#    napalm_cli,
    napalm_get,
)
from nornir_netmiko.tasks import netmiko_send_command

import sql_io

logger = logging.getLogger(__name__)

def init_nr(sess,conf):
    """ initialize nornir """
    # groups = {'iosxr':  {'platform': 'iosxr'},
    #         'iosxe':  {'platform': 'iosxe'},
    #         'ios':  {'platform': 'ios'},
    #         'nxos':  {'platform': 'nxos'}}
    #print(get_inventory(sess, conf))
    nr = InitNornir(
        runner={'plugin': "threaded", "options": {"num_workers": 10}},
        inventory={
            "plugin": "DictInventory",
            "options": {
                "hosts": sql_io.get_inventory(sess, conf),
                "groups": [],
                "defaults": []
                }
            },
        logging={"enabled": False, "to_console": True, "level": "DEBUG"},
    )
    #print(json.dumps(Host.schema(), indent=4))
    return nr

def greeter(task: Task, greet: str) -> Result:
    """ greeter function """
    return Result(host=task.host, result=f"{greet}! my name is {task.host.name}")

def napalm_facts(task: Task) -> Result:
    """
    Example on how to use the NAPALM getters.

    There are a lot more getters, find them here:
        https://napalm.readthedocs.io/en/latest/support/
    """
    napalm_getters = task.run(
        severity_level=logging.WARNING,
        task=napalm_get,
        getters=["get_facts"],
    )
    return Result(host=task.host, result=napalm_getters)

def napalm_configs(task: Task) -> Result:
    """
    Example on how to use the NAPALM getters.

    There are a lot more getters, find them here:
        https://napalm.readthedocs.io/en/latest/support/
    """
    napalm_getters = task.run(
        severity_level=logging.WARNING,
        task=napalm_get,
        getters=["get_config"],
    )
    return Result(host=task.host, result=napalm_getters)

def napalm_interfaces(task: Task) -> Result:
    """
    Example on how to use the NAPALM getters.

    There are a lot more getters, find them here:
        https://napalm.readthedocs.io/en/latest/support/
    """
    napalm_getters = task.run(
        severity_level=logging.DEBUG,
        task=napalm_get,
        getters=["get_interfaces"],
    )
    return Result(host=task.host, result=napalm_getters)


def napalm_interfaces_counters(task: Task,) -> Result:
    """
    Example on how to use the NAPALM getters.

    There are a lot more getters, find them here:
        https://napalm.readthedocs.io/en/latest/support/
    """
    napalm_getters = task.run(
        task=napalm_get,
        getters=["get_interfaces_counters"],
    )
    return Result(host=task.host, result=napalm_getters)


def getters_using_napalm(
    task: Task,
) -> Result:
    """
    Send commands using napalm_cli
    """
    cmd_ret = task.run(
        task=napalm_get,
        getters=[
            "get_facts",
            "get_config",
            "get_interfaces",
            "get_interfaces_counters",
        ],
    )
    # In case you want to work with the returns for the individual
    #  commands, uncomment the following lines:
    # show_version_output = cmd_ret[0].result['show version']
    # config = cmd_ret[0].result['show hostname']
    return Result(host=task.host, result=cmd_ret)


def command_using_netmiko(task: Task,) -> Result:
    """
    Send command using Netmiko.

    (not used in the main task in this example, included as FYI)
    """
    cmd_ret = task.run(
        task=netmiko_send_command,
        command_string="show version",
        severity_level=logging.DEBUG,
    )
    return Result(host=task.host, result=cmd_ret)

# class PrintResult:
#     def task_started(self, task: Task) -> None:
#         print(f">>> starting: {task.name}")

#     def task_completed(self, task: Task, result: AggregatedResult) -> None:
#         print(f">>> completed: {task.name}")

#     def task_instance_started(self, task: Task, host: Host) -> None:
#         pass

#     def task_instance_completed(
#         self, task: Task, host: Host, result: MultiResult
#     ) -> None:
#         print(f"  - {host.name}: - {result.result}")

#     def subtask_instance_started(self, task: Task, host: Host) -> None:
#         pass  # to keep example short and sweet we ignore subtasks

#     def subtask_instance_completed(
#         self, task: Task, host: Host, result: MultiResult
#     ) -> None:
#         pass  # to keep example short and sweet we ignore subtasks

# class SaveResultToDict:
#     def __init__(self, data: Dict[str, None]) -> None:
#         self.data = data

#     def task_started(self, task: Task) -> None:
#         self.data[task.name] = {}
#         self.data[task.name]["started"] = True

#     def task_completed(self, task: Task, result: AggregatedResult) -> None:
#         self.data[task.name]["completed"] = True

#     def task_instance_started(self, task: Task, host: Host) -> None:
#         self.data[task.name][host.name] = {"started": True}

#     def task_instance_completed(
#         self, task: Task, host: Host, result: MultiResult
#     ) -> None:
#         self.data[task.name][host.name] = {
#             "completed": True,
#             "result": result.result,
#         }

#     def subtask_instance_started(self, task: Task, host: Host) -> None:
#         pass  # to keep example short and sweet we ignore subtasks

#     def subtask_instance_completed(
#         self, task: Task, host: Host, result: MultiResult
#     ) -> None:
#         pass  # to keep example short and sweet we ignore subtasks
