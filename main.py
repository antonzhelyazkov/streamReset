import getopt
import json
import logging
import os
import sys

verbose = False
config_file = "./config.json"
log_dir = "."
dry_run = False
argv = sys.argv[1:]

try:
    opts, argv = getopt.getopt(argv, "c:vy", ["config=", "verbose", "dry="])
except getopt.GetoptError as err:
    print(err)
    opts = []

for opt, arg in opts:
    if opt in ['-c', '--config']:
        config_file = arg
    if opt in ['-v', '--verbose']:
        verbose = True
    if opt in ['-y', '--dry']:
        dry_run = True
    else:
        print("HELP")


def print_log(debug, message):
    try:
        current_log_dir = config_data['log_dir']
    except Exception:
        current_log_dir = log_dir

    if os.path.isdir(current_log_dir):
        log_file_name = os.path.basename(sys.argv[0]).split(".")
        script_log = current_log_dir + "/" + log_file_name[0] + ".log"
        logging.basicConfig(filename=script_log, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        logging.info(message)
        if debug is True:
            print(message)

    else:
        print(f"log directory does not exist {current_log_dir}")
        exit(1)


def api_put(application, stream):
    current_url = "http://" + config_data['host'] + ":" + config_data['port']
    print_log(verbose, f"URL {current_url}")


try:
    config_open = open(config_file, encoding='utf-8')
except Exception as e:
    print_log(verbose, e)
    exit(1)
else:
    config_data = json.load(config_open)

pid_file_path = config_data['pid_file_path']
file_name = os.path.basename(sys.argv[0]).split(".")
pid_file = pid_file_path.rstrip('/') + "/" + file_name[0] + ".pid"

isPID = os.path.isfile(pid_file)
if isPID:
    print_log(verbose, f"PID file exists {pid_file}")
    sys.exit()
else:
    f = open(pid_file, "w")
    f.write(str(os.getpid()))
    f.close()

api_put("qwe", "qwe")

os.remove(pid_file)
