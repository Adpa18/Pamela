#!/usr/bin/env python3

import os
import sys
import logging
from pathlib import PosixPath
from getpass import getpass
import LUKSDevice
import ParseConfig
from luksypam_log import logger
from execShellCmd import execShellCmd
from mount_umount import mount, umount
from constants import *

class Container:
    def __init__(self, name, config, data):
        self.name = name
        self.config = config
        self.data = data
        self.created = False

def getUserHome(userName):
    ret = ""
    try:
        ret = os.path.expanduser("~{}".format(userName))
    except RuntimeError:
        pass
    return ret

class LuksyPam:
    def __init__(self, userName, password=""):
        self.USER_NAME = userName
        self.PASSWORD = password
        self.USER_HOME = str()
        self.USER_ROOT_FOLDER = str()
        self.USER_CONFIG_FILE = str()
        self.containers = list()

    def init(self):
        self.USER_HOME = getUserHome(self.USER_NAME)
        if not self.USER_HOME:
            logger.log(logging.ERROR, "Can't get user {} home directory"
                       .format(self.USER_NAME))
            return False
        self.USER_ROOT_FOLDER = self.USER_HOME + "/" + LUKSYPAM_FOLDER_NAME + "/"
        self.USER_CONFIG_FILE = self.USER_ROOT_FOLDER + CONFIG_FILE_NAME
        return True

    def isLuksypamEnabled(self):
        if not PosixPath(self.USER_ROOT_FOLDER[:-1]).is_dir() or not PosixPath(self.USER_CONFIG_FILE).is_file():
            logger.log(logging.INFO,
                       "Not activated, cant find {} neither {}"
                       .format(self.USER_ROOT_FOLDER[:-1], self.USER_CONFIG_FILE))
            return False
        return True

    def loadConfs(self):
        configs = ParseConfig.ParseConfig(self.USER_CONFIG_FILE)
        if not configs.parse() or configs.isEmpty() or not configs.isValid():
            return False
        configs = configs.getContent()
        logger.log(logging.INFO,
                   "Config file for user '{}' found and valid".
                   format(self.USER_NAME))
        for name in configs:
            if configs[name]["enable"]:
                currentContainerPath = self.USER_ROOT_FOLDER + name
                self.containers.append(Container(name, configs[name], LUKSDevice.LUKSDevice(currentContainerPath)))
        return True

    def createContainers(self):
        for container in list(self.containers):
            currentContainerPath = self.USER_ROOT_FOLDER + container.name
            if not PosixPath(currentContainerPath).is_file():
                tmpPassword = self.PASSWORD if container.config["useUserPassword"] else getpass(PROMPT_PASS.format(container.name))
                if not container.data.createDevice(
                    container.config["sizeInMB"], tmpPassword, container.config["weak"]):
                    self.containers.remove(container)
                    continue
                logger.log(logging.INFO, "Container {} created with size {}"
                           .format(container.name, container.config["sizeInMB"]))
                container.created = True

    def initContainers(self):
        for container in self.containers:
            currentContainerPath = self.USER_ROOT_FOLDER + container.name
            if not container.data.init():
                self.containers.remove(container)

    def openContainers(self):
        for container in list(self.containers):
            if not container.data.isOpen():
                tmpPassword = self.PASSWORD if container.config["useUserPassword"] else getpass(PROMPT_PASS.format(container.name))
                if not container.data.open(tmpPassword):
                    self.containers.remove(container)
                    continue
            deviceInfos = container.data.c.info()
            logger.log(logging.DEBUG, "Container {} infos: {}".format(container.name, deviceInfos))
            currentDevicePath = deviceInfos["dir"] + "/" + deviceInfos["name"]
            if container.created:
                ret = execShellCmd("mkfs.{} {}".format(FORMAT_DRIVE_IN, currentDevicePath))
                if ret[0] != 0:
                    logger.log(logging.ERROR,
                               "Error formating device {}: {}".format(currentDevicePath, ret[2]))
                    self.containers.remove(container)
                    continue
            logger.log(logging.INFO, "Container {} openned successfully".format(container.name))

    def closeContainers(self):
        for container in list(self.containers):
            if container.data.isOpen():
                if not container.data.close():
                    self.containers.remove(container)
                    continue
                logger.log(logging.INFO, "Container {} closed successfully"
                           .format(container.name))

    def mountContainers(self):
        for container in list(self.containers):
            currentMountPath = self.USER_HOME + "/" + container.config["mountDir"]
            if not PosixPath(currentMountPath).is_dir():
                try:
                    PosixPath(currentMountPath).mkdir()
                except Exception as e:
                    logger.log(logging.ERROR, "Error creating folder {}: {}"
                               .format(currentMountPath, e))
                    self.containers.remove(container)
                    continue
            if PosixPath(currentMountPath).is_symlink():
                logger.log(logging.ERROR, "Error folder {} must not be a symlink"
                           .format(currentMountPath))
                self.containers.remove(container)
                continue
            if not os.path.ismount(currentMountPath):
                deviceInfos = container.data.c.info()
                currentDevicePath = deviceInfos["dir"] + "/" + deviceInfos["name"]
                ret = mount(currentDevicePath, currentMountPath, FORMAT_DRIVE_IN)
                if not ret[0]:
                    logger.log(logging.ERROR,
                               "Error mounting {} on {}: {} returned {}"
                               .format(currentDevicePath, currentMountPath, ret[1], ret[0]))
                    self.containers.remove(container)
                    continue
                logger.log(logging.INFO, "Container {} mounted".format(container.name))

    def umountContainers(self):
        for container in list(self.containers):
            currentMountPath = self.USER_HOME + "/" + container.config["mountDir"]
            if os.path.ismount(currentMountPath):
                ret = umount(currentMountPath)
                if not ret[0]:
                    logger.log(logging.ERROR, "Error umounting {}: {} returned {}"
                               .format(currentMountPath, ret[1], ret[0]))
                    self.containers.remove(container)
                    continue
                logger.log(logging.INFO, "{} umount sucessfully"
                          .format(container.name))
