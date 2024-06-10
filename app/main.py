
import logging
import logging.config
import datetime
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.engine import URL
import sqlalchemy as db
#from nornir_table_inventory import FlatDataInventory
import pandas as pd
import nornir as nornir
from nornir import InitNornir
from nornir.core.inventory import ConnectionOptions, Host
from nornir_utils.plugins.functions import print_result
from napalm import get_network_driver
#from rich import print as rprint
import config as config
import file_io as file_io
import sql_io as sql_io
import models as models
import nr as mynr
# # Get the logger instance
logger = logging.getLogger(__name__)



def get_inventory(sess, conf):
    defaults = {'username': conf['env']['app_cred_u1'], 'password': conf['env']['app_cred_p1']}
    users = sess.execute(
        select(models.User).where(models.User.username.in_([defaults['username']]))
    ).first()[0]
    username = users.username
    password = users.password
    devices = sess.execute(
        select(models.Device)
    ).fetchall()
    inv = {}
    for line in devices:
    #if not line.Device.name == 'oconomowoc':
        inv[line.Device.name] = {
            "name": line.Device.name,
            "connection_options": {
                "napalm": {
                    "hostname": line.Device.hostname,
                    "port": 22,
                    "username": username,
                    "password": password,
                    "platform": line.Device.platform
                }
            },
        }
    inv2={
    "name": "str",
    "connection_options": {
        "$connection_type": {
            "extras": {
                "$key": "$value"
            },
            "hostname": "str",
            "port": "int",
            "username": "str",
            "password": "str",
            "platform": "str"
        }
    },
    "groups": [
        "$group_name"
    ],
    "data": {
        "$key": "$value"
    },
    "hostname": "str",
    "port": "int",
    "username": "str",
    "password": "str",
    "platform": "str"
    }
    logger.info(inv)
    return inv
def init_nr(sess,conf):
    groups = {'iosxr':  {'platform': 'iosxr'},
            'iosxe':  {'platform': 'iosxe'},
            'ios':  {'platform': 'ios'},
            'nxos':  {'platform': 'nxos'}}
    #print(get_inventory(sess, conf))
    nr = nornir.InitNornir(
        runner={'plugin': "threaded", "options": {"num_workers": 10}},
        inventory={
            "plugin": "DictInventory",
            "options": {
                "hosts": get_inventory(sess, conf),
                "groups": [],
                "defaults": []
                }
            },
        logging={"enabled": False, "to_console": True, "level": "DEBUG"},
    )
    #print(json.dumps(Host.schema(), indent=4))
    return nr

def main_app():

    # load environment
    load_dotenv()
    # Parse command-line arguments
    args = config.parse_arguments()
    print(args)

    #create filemanager instance
    file_manager = file_io.FileManager({})

    # Load the configuration
    cfg = config.load_config(args.config, file_manager)
    logger.info(config.LOGO)
    # purge things
    if args.purge==True:
        logger.info('_____purging')
        file_manager.delete_file(cfg.get("app_defaults", {}).get("database", 'database.db'))


    # Read a CSV file
    file_manager = file_io.FileManager(config)

    groups = {'iosxr':  {'platform': 'iosxr'},
                'iosxe':  {'platform': 'iosxe'},
                'ios':  {'platform': 'ios'},
                'nxos':  {'platform': 'nxos'}}
    defaults = {'username': cfg['env']['app_cred_u1'], 'password': cfg['env']['app_cred_p1']}

    db_url = URL.create(
        drivername='sqlite',
        database= 'app/data/output/' + cfg.get("app_defaults", {}).get("database", 'database.db')
    )
    #db_url = 'sqlite:///app/data/output/' + cfg.get("app_defaults", {}).get("database", 'database.db')

        # Create a DatabaseManager instance
    db_manager = sql_io.DatabaseManager(db_url)

    # Create tables
    db_manager.create_tables(models.Device, models.User)

    logger.info('Application started')
    logger.info(f"Command line args: {args}")
    #logger.info(f'Environment variables: {cfg["env"]}')
    #logger.info(f'Logging variables: {cfg["logging"]}')
    logger.info(f'Application defaults: {cfg["app_defaults"]}')

#initialize data
    with db_manager.session_scope() as session:
        stmt = select(models.User).filter_by(username=defaults['username'])
        user_obj = session.scalars(stmt).first()
        if not user_obj:
            logger.debug(f"_____{defaults['username']} does not exist")
            user_data = {
                'username': defaults['username'],
                'password': defaults['password'],
                'created_at': datetime.datetime.now(),
                }
            session.add(models.User(**user_data))
            session.commit()
            stmt = select(models.User).filter_by(username=defaults['username'])
            user_obj = session.scalars(stmt).first()
            if user_obj:
                logger.info(f"_____{defaults['username']} created")
            else:
                logger.error(f"_____{defaults['username']} not created")
        else:
            logger.debug(f"_____{defaults['username']} exists")

        for row in file_manager.read_csv('devices.csv'):
            logger.debug("_____%s",row['name'])
            device_data = {}
            stmt = select(models.Device).filter_by(name=row['name'])
            dev_obj = session.scalars(stmt).first()
            if dev_obj:
                #print(devs,row['name'])
                logger.debug(f"_____{row.get('name')} exists")
            else:
                logger.error(f"_____{row.get('name')} does not exist")
                user = select(models.User).filter_by(username=defaults['username'])
                usr_obj = session.scalars(user).first()
                #print("===============",usr_obj)
                row_port = row["port"] if 'port' in row else None

                device_data = {
                'name': row['name'],
                'hostname': row['hostname'],
                'port': row_port,
                'user_id': usr_obj.id,
                'platform': row['platform'],
                'groups': groups[row['platform']]['platform'],
                'created_at': datetime.datetime.now(),
                }
                session.add(models.Device(**device_data))
                session.commit()

                stmt = select(models.Device,models.User).filter_by(id=models.User.id)
                dev_obj = session.scalars(stmt).first()
                if dev_obj:
                    logger.info(f"_____{row['name']} created {dev_obj}")
                else:
                    logger.error(f"_____{row['name']} not created")
    # next section
    #data = {}
    with db_manager.session_scope() as session:
        nr = init_nr(session, cfg)
        #print(nr.inventory.hosts)
        #ios_driver = get_network_driver("ios")
        
        #nr_with_processors = nr.with_processors([mynr.SaveResultToDict(data), mynr.PrintResult()])
        result1=nr.run(
            name='facts',
            task=mynr.napalm_facts,
        )
        result2=nr.run(
            name='interfaces',
            task=mynr.napalm_interfaces,
        )
        result3=nr.run(
            name='configs',
            task=mynr.napalm_configs,
        )
    

    ress1 = {}
    ress2 = {}
    ress3 = {}
    for host in nr.inventory.hosts.keys():
        print("---")
        if result1[host][0].failed:
            print(f"{host} failed")
        else:
            ress1[host]=(result1[host][1].result)["get_facts"]
            ress2[host]=(result2[host][1].result)["get_interfaces"]
            ress3[host]=(result3[host][1].result)["get_config"]
    print(ress1)
    print(ress2)
    print(ress3)

def main():
    #args = config.parse_arguments()
    main_app()

if __name__ == '__main__':
    main()
    """
    {
    "name": "str",
    "connection_options": {"$connection_type": {"extras": {"$key": "$value"},
        "hostname": "str",
        "port": "int",
        "username": "str",
        "password": "str",
        "platform": "str"}},
    "groups": ["$group_name"],
    "data": {"$key": "$value"},
    "hostname": "str",
    "port": "int",
    "username": "str",
    "password": "str",
    "platform": "str"
}
    """