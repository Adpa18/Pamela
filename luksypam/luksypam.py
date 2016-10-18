#!/usr/bin/env python3

import sys
import os
import logging
from systemd.journal import JournalHandler
import ParseConfig
import LUKSDevice
from mount_umount import mount, umount
from execShellCmd import execShellCmd

password = input()[:-1]

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)

print(os.environ)

USER_HOME="/home/{}/".format(os.environ["PAM_USER"])
USER_ROOT_FOLDER=USER_HOME + ".luksypam/"
USER_CONFIG_FILE=USER_ROOT_FOLDER + "config.json"
FORMAT_DRIVE_IN="ext4"

# Check if luksypam is activated

if not os.path.isdir(USER_ROOT_FOLDER[:-1]) or not os.path.isfile(USER_CONFIG_FILE):
    logger.log(logging.INFO, "not activated, cant find {} neither {}".format(USER_ROOT_FOLDER[:-1], USER_CONFIG_FILE))
    sys.exit(0)

config = ParseConfig.ParseConfig(USER_CONFIG_FILE)

if not config.parse() or config.isEmpty() or not config.isValid():
    sys.exit(0)

print("A config file exists and it is valid!")
infos = config.getContent()
print(infos)

for container in infos:
    created = False
    print(infos[container])
    if not infos[container]["enable"]:
        logger.log(logging.INFO, "Container {} not enabled".format(container))
        continue
    currentContainerPath = USER_ROOT_FOLDER + container
    d = LUKSDevice.LUKSDevice(currentContainerPath)
    if not os.path.isfile(currentContainerPath):
        logger.log(logging.INFO, "Container {} does not exist".format(container))
        # create volume
        if not d.createDevice(infos[container]["sizeInMB"], password):
            logger.log(logging.INFO, "Container {} can not create".format(container))
            sys.exit(0)
        created = True
    if not d.init():
        logger.log(logging.INFO, "Container {} can not init".format(container))
        sys.exit(0)
    # Open volume
    if not d.isOpen():
        logger.log(logging.INFO, "Container {} is not open".format(container))
        if not d.open(password):
            logger.log(logging.INFO, "Container {} can not open".format(container))
            sys.exit(0)
    deviceInfos = d.c.info()
    currentDevicePath = deviceInfos["dir"] + "/" + deviceInfos["name"]
    # if new volume, format
    if created:
        logger.log(logging.INFO, "Container {} formating".format(container))
        ret = execShellCmd("mkfs.{} {}".format(FORMAT_DRIVE_IN, currentDevicePath))
        if ret[0] != 0:
            logger.log(logging.ERROR, "Error formating device: {}".format(ret[2]))
            sys.exit(0)
    # Mount volume
    currentMountPath = USER_HOME + infos[container]["mountDir"]
    if not os.path.isdir(currentMountPath):
        try:
            os.makedirs(currentMountPath)
        except Exception as e:
            logger.log(logging.ERROR,
                       "Error creating folder {}: {}"
                       .format(currentMountPath, e))
            sys.exit(0)

    if not os.path.ismount(currentMountPath):
        logger.log(logging.INFO, "Container {} not mount".format(container))
        ret = mount(currentDevicePath, currentMountPath, FORMAT_DRIVE_IN)
        if not ret[0]:
            logger.log(logging.ERROR,
                       "Error mounting {} on {}: {}"
                       .format(currentDevicePath, currentMountPath, ret[1]))

sys.exit(0)
