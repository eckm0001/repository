import argparse
import yaml
import os
import logging
import logging.config
import colorlog
logger = logging.getLogger(__name__)

import file_io as file_io

def setup_logging(logging_config):
    """
    Set up logging based on the provided configuration.
    """
    logging.config.dictConfig(logging_config)

def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description='My Python Application')
    parser.add_argument('-c', '--config', help='Path to the configuration file', default='config.yaml', required=False)
    parser.add_argument("-p", "--purge", action='store_true', default=False, help="purge database before storing")
    args = parser.parse_args()

    return args

def load_config(config_path, file_manager_inst):
    """
    Load the application configuration from a YAML file and environment variables.
    """
    env_vars = {
        key.lower(): value
        for key, value in os.environ.items()
        if key.startswith('APP_')
    }
    if 'APP_CONFIG_FILE' in env_vars:
        if env_vars['APP_CONF_FILE'] != config_path:
            cfg_path = os.environ['APP_CONFIG_FILE']
        else:
            cfg_path = config_path
    #print(config_path)
    config = file_manager_inst.read_yaml(cfg_path)
    if config:
        setup_logging(config["logging"])
        #config = yaml.safe_load(config_content)
        #print(config)
        # Load environment variables

        # Merge environment variables into the configuration
        config["env"] = env_vars
        #config.update(env_vars)

        return config
    else:
        return {}

LOGO = """

                         __    _
                    _wr""        "-q__
                 _dP                 9m_
               _#P                     9#_
              d#@                       9#m
             d##                         ###
            J###                         ###L
            {###K                       J###K
            ]####K      ___aaa___      J####F
        __gmM######_  w#P""   ""9#m  _d#####Mmw__
     _g##############mZ_         __g##############m_
   _d####M@PPPP@@M#######Mmp gm#########@@PPP9@M####m_
  a###""          ,Z"#####@" '######"\\g          ""M##m
 J#@"             0L  "*##     ##@"  J#              *#K
 #"               `#    "_gmwgm_~    dF               `#_
7F                 "#_   ]#####F   _dK                 JE
]                    *m__ ##### __g@"                   F
                       "PJ#####LP"
 `                       0######_                      '
                       _0########_
     .               _d#####^#####m__              ,
      "*w_________am#####P"   ~9#####mw_________w*"
          ""9@#####@M""           ""P@#####@M""

"""
