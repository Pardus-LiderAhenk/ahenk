#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Seren Piri <seren.piri@agem.com.tr>

import pexpect

from base.plugin.abstract_plugin import AbstractPlugin


class BackupUtil(AbstractPlugin):
    def __init__(self, data, context, type):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.content_type = self.get_content_type()
        self.__type = type

    def backup(self):

        if self.__type == "task":
            type = "task"
            resp_code = self.message_code.TASK_PROCESSED.value
            resp_err_code = self.message_code.TASK_ERROR.value
        else:
            type = "profile"
            resp_code = self.message_code.POLICY_PROCESSED.value
            resp_err_code = self.message_code.POLICY_ERROR.value

        self.logger.debug("Starting to backup... Reading backup " + type + " json")

        backup_profile = self.data

        self.logger.debug("Successfully read backup " + type + " json.")
        destination_path = str(backup_profile['username']) + '@' + str(backup_profile['destHost']) + ':' + str(
            backup_profile['destPath'])
        self.logger.debug("Destination path ==> " + str(destination_path))

        for source in backup_profile['directories']:
            self.logger.debug("Trying to backup for source ==> " + str(source['sourcePath']))
            options = ''
            path = source['sourcePath'] + ' ' + destination_path
            command = ''

            if backup_profile['useLvmShadow']:
                logicalVolumeSize = str(source['logicalVolumeSize'])
                logicalVolume = str(source['logicalVolume'])
                virtualGroup = str(source['virtualGroup'])
                create_lv_command = 'lvcreate -L ' + logicalVolumeSize + ' -s -n ' + logicalVolume + ' ' + virtualGroup
                (result_code, p_out, p_err) = self.execute(create_lv_command, shell=True)
                if (result_code == 0):
                    self.logger.debug('Logical volume created successfully. LV ==>' + str(logicalVolume))
                    (result_code, p_out, p_err) = self.execute('mkdir -p ' + source['sourcePath'], shell=True)
                    (result_code, p_out, p_err) = self.execute(
                        'mount ' + logicalVolume + ' ' + source['sourcePath'], shell=True)
                    self.logger.debug('Mount path created successfully. Mount path ==>' + source['sourcePath'])

            if source['recursive']:
                options = options + ' -r '
            if source['preserveGroup']:
                options = options + ' -g '
            if source['preserveOwner']:
                options = options + ' -o '
            if source['preservePermissions']:
                options = options + ' -p '
            if source['archive']:
                options = options + ' -a '
            if source['compress']:
                options = options + ' -z '
            if source['existingOnly']:
                options = options + ' --existing '
            if source['excludePattern']:
                options = options + ' --exclude "' + source['excludePattern'] + '" '

            try:
                result_code = -1
                if (backup_profile['useSsh']):
                    sshOptions = ' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null --progress -p ' + str(
                        backup_profile['destPort'])
                    command = 'rsync ' + options + ' -e "' + sshOptions + '" ' + path
                    self.logger.debug("Command ==> " + command)
                    (result_code, p_out, p_err) = self.execute(command, shell=True)
                else:
                    sshOptions = ' ssh -q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no -p ' + str(
                        backup_profile['destPort'])
                    command = 'rsync ' + options + ' -e "' + sshOptions + '" ' + path
                    self.logger.debug("Command ==> " + command)
                    result_code = self.runCommandWithPassword(command, backup_profile['password'])

                if result_code == 0:
                    self.logger.info("Sync is successfull for source ==> " + str(source['sourcePath']))
                    resp_message = "Backup işlemi başarıyla tamamlandı."
                else:
                    self.logger.error(
                        "The backup process is unsuccessfull for destination ==> " + destination_path + "  and source ==> " + str(
                            source['sourcePath'])
                        + " \n" + self.getExitStatus(int(result_code)))
                    resp_code = resp_err_code
                    resp_message = "Hata mesajı: " + self.getExitStatus(int(result_code)) + " \n[Kaynak: " + str(
                        source['sourcePath']) + " Hedef: " + destination_path + "]"

            except Exception as e:
                self.logger.error("Exception ==> " + str(e))
                resp_code = resp_err_code
                resp_message = str(e)

            self.context.create_response(code=resp_code, message=resp_message,
                                         content_type=self.content_type.APPLICATION_JSON.value)

    def runCommandWithPassword(self, command, password, timeout=30):
        try:
            child = pexpect.spawn(command, timeout=timeout)
            i = child.expect(['password: ', pexpect.EOF, pexpect.TIMEOUT])
            if i == 0:
                child.sendline(password)
                child.expect(pexpect.EOF)
                child.close()
                return child.exitstatus
            elif i == 1:
                return 999
            elif i == 2:
                return 888
        except Exception as e:
            self.logger.warning('runCommandWithPassword Error: {0}'.format(str(e)))
            if i == 0:
                return 888
            else:
                child.close()
                return child.exitstatus

    def getExitStatus(self, exitCode):
        switcher = {
            #   0 : "Success",
            1: "Syntax or usage error",
            2: "Protocol incompatibility",
            3: "Errors selecting input / output files, dirs",
            4: "Requested action not supported: an attempt was made to manipulate 64 - bit files on a platform"
               "\n that cannot support them; or an option was specified that is supported by the client and not by the server.",
            5: "Error starting client - server protocol",
            6: "Daemon unable to append to log - file",
            10: "Error in socket I / O",
            11: "Error in file I / O",
            12: "Error in rsync protocol data stream",
            13: "Errors with program diagnostics",
            14: "Error in IPC code",
            20: "Received SIGUSR1 or SIGINT",
            21: "Some error returned by waitpid()",
            22: "Error allocating core memory buffers",
            23: "Partial transfer due to error",
            24: "Partial transfer due to vanished source files",
            25: "The --max-delete limit stopped deletions",
            30: "Timeout in data send / receive",
            35: "Timeout waiting for daemon connection",
            255: "Please make certain of the backup parameters you have entered.",
            888: "Timeout exceeded. Destination could be unreachable \n or Please make certain of Password, Destination Host/Port, Dest./Source Path values you have entered.",
            999: "Rsync command returns EOF! Destination could be unreachable \n or Please make certain of Destination Host/Port you have entered."
        }
        return switcher.get(exitCode,
                            "Exit Status Message for exit code '" + str(exitCode) + "' of rsync command is not found!")
