import getopt
import json
import logging
import os
import sys
import requests
from requests.auth import HTTPDigestAuth

verbose = False
config_file = "./config.json"
log_dir_default = "."
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


def print_log(debug, message):
    file_name = os.path.basename(sys.argv[0]).split(".")

    current_log_dir = add_directory_slash(config_data['log_dir'])

    if os.path.isdir(current_log_dir):
        script_log = current_log_dir + "/" + file_name[0] + ".log"
    else:
        script_log = log_dir_default + "/" + file_name[0] + ".log"

    logging.basicConfig(filename=script_log, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info(message)

    if debug is True:
        print(message)


def add_directory_slash(directory):
    if not directory.endswith("/"):
        dir_return = directory + "/"
    else:
        dir_return = directory
    return dir_return


def api_url(application, stream):
    current_url = "http://" + config_data['host'] + ":" + config_data['port_api'] + \
                  "/v2/servers/_defaultServer_/vhosts/_defaultVHost_/applications/" + \
                  application + \
                  "/instances/_definst_/incomingstreams/" + \
                  stream + \
                  "/actions/resetStream"
    print_log(verbose, f"URL {current_url}")
    return current_url


def m3u8_stream(application, stream):
    current_url = "http://" + config_data['host'] + ":" + config_data['port_stream'] + "/" + \
                  application + "/" + stream + "/playlist.m3u8"
    print_log(verbose, f"current url {current_url}")
    return current_url


def api_put(url, user, password):
    header = {
        'Accept': 'application/json',
        'Content-type': 'application/json'
    }
    respond = requests.put(url, auth=HTTPDigestAuth(user, password), headers=header)
    return respond.json()


def stream_couples(apps):
    couples = []
    for app, streams in apps.items():
        for stream in streams:
            couple = [app, stream]
            couples.append(couple)

    return couples


if os.path.isfile(config_file):
    config_open = open(config_file, encoding='utf-8')
    config_data = json.load(config_open)
else:
    print_log(verbose, f"ERROR config file {config_file} not found")
    sys.exit(1)

pid_file_path = config_data['pid_file_path']
FILE_NAME = os.path.basename(sys.argv[0]).split(".")
pid_file = pid_file_path.rstrip('/') + "/" + FILE_NAME[0] + ".pid"

isPID = os.path.isfile(pid_file)
if isPID:
    print_log(verbose, f"PID file exists {pid_file}")
    sys.exit()
else:
    f = open(pid_file, "w")
    f.write(str(os.getpid()))
    f.close()

arr_couples = stream_couples(config_data['apps'])
for c_app, c_stream in arr_couples:
    m3u8_url = m3u8_stream(c_app, c_stream)
    try:
        status = requests.get(m3u8_url).status_code
    except requests.ConnectionError as e:
        print_log(verbose, f"ERROR http {e}")
        os.remove(pid_file)
        sys.exit(1)
    else:
        print_log(verbose, f"status {status} url {m3u8_url}")

    if int(status) != 200:
        print_log(verbose, f"ERROR in {m3u8_url}")
        api_respond = api_put(api_url(c_app, c_stream), config_data['user'], config_data['pass'])
        if not api_respond['success']:
            print_log(verbose, f"ERROR in restart {m3u8_url}")
        else:
            print_log(verbose, f"OK in restart {m3u8_url}")
    else:
        print_log(verbose, f"OK {m3u8_url}")


os.remove(pid_file)
