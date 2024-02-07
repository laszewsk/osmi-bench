doc = """
Usage:
    create_model_conf.py [--config=<file>]

Options:
    --config=<file>  Path to the configuration file [default: models.in.conf]
"""

import docopt
from cloudmesh.common.util import readfile, writefile
import os
from cloudmesh.common.util import banner

def main():

    args = docopt.docopt(doc)

    config_file = args['--config']
    config = readfile(config_file)
    filename = config_file.replace(".in" , "")

    # Add your code here

    pwd = os.getcwd()
    config = config.replace("{pwd}",pwd)

    banner("Write mod")
    print(config)   
    
    writefile(filename, config)    

if __name__ == "__main__":
    main()