""" main
"""
import logging
import logging.config
#import colorlog
import datetime
import re

# from datetime import datetime
# import json
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import select
# from sqlalchemy.orm import Session
from sqlalchemy.engine import URL

from config import parse_arguments, load_config, LOGO
import file_io
import sql_io# as sql_io
import models #as models
import nr as mynr
# # Get the logger instance
logger = logging.getLogger(__name__)

def main_app():
    """ main app
    """
    # load environment
    load_dotenv()
    # Parse command-line arguments
    args = parse_arguments()

    # create filemanager instance
    file_mgr = file_io.FileManager()

    # Load the configuration
    cfg = load_config(args.config, file_mgr)
    logger.info(LOGO)
    logger.info("Command line args: %s", args)
    # purge things
    if args.purge is True:
        logger.info('_____purging %s',cfg.get("app_defaults",{}).get("database_path",'database.db'))
        file_mgr.delete_file(Path(cfg.get("app_defaults",{}).get("database_path",'database.db')))
    groups = {'iosxr':  {'platform': 'iosxr'},
                'iosxe':  {'platform': 'iosxe'},
                'ios':  {'platform': 'ios'},
                'nxos':  {'platform': 'nxos'}}
    defaults = {'username': cfg['env']['app_cred_u1'], 'password': cfg['env']['app_cred_p1']}

    db_mgr=sql_io.DatabaseManager(
        URL.create(
            drivername='sqlite',
            database=str(Path(cfg.get("app_defaults",{}).get("database_path",'database.db')))
            )
        )

    # Create tables
    db_mgr.create_tables(
        models.Devices, models.Users, models.InterfaceNames, models.InterfacesData
    )
    db_mgr.create_tables(models.StackData, models.Models, models.Vendors)

    logger.info('Application started')
    # logger.info("Command line args: %s", args)
    # logger.info(f'Environment variables: {cfg["env"]}')
    # logger.info(f'Logging variables: {cfg["logging"]}')
    logger.info('Application defaults: %s', cfg["app_defaults"])

    # initialize data
    with db_mgr.session_scope() as session:
        stmt = select(models.Users).filter_by(username=defaults['username'])
        user_obj = session.scalars(stmt).first()
        if not user_obj:
            logger.debug('%s does not exist', defaults['username'])
            user_data = {
                'username': defaults['username'],
                'password': defaults['password'],
                'created_at': datetime.datetime.now(),
                }
            session.add(models.Users(**user_data))
            session.commit()
            stmt = select(models.Users).filter_by(username=defaults['username'])
            user_obj = session.scalars(stmt).first()
            if user_obj:
                logger.info('_____%s created', defaults['username'])
            else:
                logger.error('_____%s not created', defaults['username'])
        else:
            logger.debug('_____%s exists', defaults['username'])
        csv_data=file_mgr.read_csv(cfg["app_defaults"]["csv_path"])
        if csv_data:
            for row in csv_data:
                logger.debug("_____%s",row['name'])
                device_data = {}
                stmt = select(models.Devices).filter_by(name=row['name'])
                dev_obj = session.scalars(stmt).first()
                if dev_obj:
                    # print(devs,row['name'])
                    logger.debug("_____%s  exists", row.get('name'))
                else:
                    logger.error('_____%s does not exist', row.get('name'))
                    usr = select(models.Users).filter_by(username=defaults['username'])
                    usr_obj = session.scalars(usr).first()
                    if usr_obj is not None:
                        # print("===============",usr_obj)
                        row_port = row["port"] if 'port' in row else None
                        device_data = {
                            'name': row['name'],
                            'hostname': row['hostname'],
                            'port': row_port,
                            'user_id': usr_obj.id, #  models.Users.id
                            'platform': row['platform'],
                            'groups': groups[row['platform']]['platform'],
                            'enabled': True,
                            'created_at': datetime.datetime.now(),
                        }
                        session.add(models.Devices(**device_data))
                        session.commit()

                    stmt = select(models.Devices).filter_by(name=row['name'])
                    devi_obj = session.scalars(stmt).first()
                    if devi_obj:
                        logger.info('_____%s %s created', row['name'], devi_obj)
                    else:
                        logger.error('_____%s  not created', row['name'])
    # next section
    # data = {}
    with db_mgr.session_scope() as session:
        nr = mynr.init_nr(session, cfg)

        result1 = nr.run(
            name="getters",
            task=mynr.getters_using_napalm,
        )
        # )

    ress1 = {}
    # ress2 = {}
    # ress3 = {}
    with db_mgr.session_scope() as session:

        for host in nr.inventory.hosts.keys():
            print("---")
            if result1[host][0].failed:
                print(f"{host} failed")
                stmt = select(models.Devices).filter_by(name=models.Devices.name)
                dev_obj = session.scalars(stmt).first()
                if dev_obj:
                    device_data = {
                        'id': dev_obj.id,
                        'enabled': False
                    }
                    session.merge(models.Devices(**device_data))
                    session.commit()
            else:
                print(f"{host} collected")
                ress1[host] = result1[host][1].result

    logger.debug("%s", ress1)
    logger.info("-------------------------------------")
    with db_mgr.session_scope() as session:
        for name, dicts in ress1.items():
            for task, result in dicts.items():
                # setum = 1
                if task == "get_facts":
                    print(task, result)

                    logger.info("\n________%s %s %s", name, task, result)
                    dev_stmt = select(models.Devices).filter_by(name=name)
                    dev_obj = session.scalars(dev_stmt).first()
                    if dev_obj:

                        vendor_data = {
                            "vendor": result["vendor"],
                        }
                        vend_stmt = select(models.Vendors).filter_by(
                            vendor=result["vendor"]
                        )
                        vend_obj = session.scalars(vend_stmt).first()
                        if vend_obj:
                            vend_id = vend_obj.id
                        else:
                            session.add(models.Vendors(**vendor_data))
                            session.commit()
                            vend_stmt = select(models.Vendors).filter_by(
                                vendor=result["vendor"]
                            )
                            vend_obj = session.scalars(vend_stmt).first()
                            vend_id = vend_obj.id

                        model_data = {
                            "model": result["model"],
                        }
                        model_stmt = select(models.Models).filter_by(
                            model=result["model"]
                        )
                        model_obj = session.scalars(model_stmt).first()
                        if model_obj:
                            model_id = model_obj.id
                        else:
                            session.add(models.Models(**model_data))
                            session.commit()
                            model_stmt = select(models.Models).filter_by(
                                model=result["model"]
                            )
                            model_obj = session.scalars(model_stmt).first()
                            model_id = model_obj.id

                        os_version_data = {
                            "os_version": result["os_version"],
                        }
                        os_v_stmt = select(models.OSVersions).filter_by(
                            os_version=result["os_version"]
                        )
                        os_v_obj = session.scalars(os_v_stmt).first()
                        if os_v_obj:
                            os_v_id = os_v_obj.id
                        else:
                            session.add(models.OSVersions(**os_version_data))
                            session.commit()
                            os_v_stmt = select(models.OSVersions).filter_by(
                                os_version=result["os_version"]
                            )
                            os_v_obj = session.scalars(os_v_stmt).first()
                            os_v_id = os_v_obj.id

                        serial_data = {
                            "serial": result["serial_number"],
                            "asset": "<None>",
                        }
                        serial_stmt = select(models.Serials).filter_by(
                            serial=result["serial_number"]
                        )
                        serial_obj = session.scalars(serial_stmt).first()
                        if serial_obj:
                            serial_id = serial_obj.id
                        else:
                            session.add(models.Serials(**serial_data))
                            session.commit()
                            serial_stmt = select(models.Serials).filter_by(
                                serial=result["serial_number"]
                            )
                            serial_obj = session.scalars(serial_stmt).first()
                            serial_id = serial_obj.id

                        int_data_stmt = select(models.InterfacesData).filter_by(
                            device_id=dev_obj.id
                        )
                        int_data_obj = session.scalars(int_data_stmt).fetchall()

                        # TODO: move to history tables
                        if int_data_obj:
                            session.delete(int_data_obj)
                            session.commit()

                        for interfacename in result["interface_list"]:

                            port_type = re.sub(r"\d+((\/\d+))", "", interfacename)

                            port = re.sub(r"\D\B", "", interfacename)
                            print(port, port_type)
                            interface_name_data = {
                                "name": port_type,
                            }
                            intn_stmt = select(models.InterfaceNames).filter_by(
                                name=port_type
                            )
                            intn_obj = session.scalars(intn_stmt).first()
                            if intn_obj:
                                intn_id = intn_obj.id
                            else:
                                session.add(
                                    models.InterfaceNames(**interface_name_data)
                                )
                                session.commit()
                                intn_stmt = select(models.InterfaceNames).filter_by(
                                    name=port_type
                                )
                                intn_obj = session.scalars(intn_stmt).first()
                                intn_id = intn_obj.id

                            interface_data = {
                                "interface_name": intn_id,
                                "port": port,
                                "device_id": dev_obj.id,
                                "created_at": datetime.datetime.now(),
                                "updated_on": datetime.datetime.now(),
                            }
                            int_data_stmt = select(models.InterfacesData).filter_by(
                                device_id=dev_obj.id
                            )
                            int_data_obj = session.scalars(int_data_stmt).fetchall()
                            if int_data_obj:
                                session.add(models.InterfacesData(**interface_data))
                                session.commit()

                        new_name = dev_obj.name
                        if result["hostname"] != dev_obj.name:
                            new_name = result["hostname"]
                        device_data = {
                            "id": dev_obj.id,
                            "name": new_name,
                            "uptime": result["uptime"],
                            "vendor_id": vend_id,
                            "model_id": model_id,
                            "os_version_data": os_v_id,
                            "serial_id": serial_id,
                        }
                        session.merge(models.Devices(**device_data))
                        session.commit()
                elif task == "get_config":
                    print(task)
                elif task == "get_interfaces":
                    print(task)


def main():
    """ main
    """
    # args = config.parse_arguments()
    main_app()


if __name__ == '__main__':
    main()
