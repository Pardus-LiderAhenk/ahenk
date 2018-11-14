#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import datetime
import json
import uuid
from uuid import getnode as get_mac
from base.scope import Scope
from base.messaging.anonymous_messenger import AnonymousMessenger
from base.system.system import System
from base.util.util import Util
from helper import system as sysx
import pwd
from base.timer.setup_timer import SetupTimer
from base.timer.timer import Timer
import re
import sys
import os

class Registration:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.message_manager = scope.get_message_manager()
        self.event_manager = scope.get_event_manager()
        self.messenger = scope.get_messenger()
        self.conf_manager = scope.get_configuration_manager()
        self.db_service = scope.get_db_service()
        self.util = Util()
        self.service_name='im.liderahenk.org'

        #self.event_manager.register_event('REGISTRATION_RESPONSE', self.registration_process)
        self.event_manager.register_event('REGISTRATION_SUCCESS', self.registration_success)
        self.event_manager.register_event('REGISTRATION_ERROR', self.registration_error)

        if self.is_registered():
            self.logger.debug('Ahenk already registered')
        else:
            self.register(True)

    def registration_request(self):

        self.logger.debug('Requesting registration')
        # SetupTimer.start(Timer(System.Ahenk.registration_timeout(), timeout_function=self.registration_timeout,checker_func=self.is_registered, kwargs=None))

        self.host = self.conf_manager.get("CONNECTION", "host")
        self.servicename = self.conf_manager.get("CONNECTION", "servicename")

        self.user_name = ''
        self.user_password= ''

        user_name= os.getlogin()

        self.logger.debug('User : '+ str(user_name))

        pout = Util.show_registration_message(user_name,'Makineyi etki alanına almak için bilgileri ilgili alanlara giriniz. LÜTFEN DEVAM EDEN İŞLEMLERİ SONLANDIRDIĞINZA EMİN OLUNUZ !',
                                              'ETKI ALANINA KAYIT', self.host)

        self.logger.debug('pout : ' + str(pout))

        field_values = pout.split(' ')

        user_registration_info = list(field_values)

        if self.host == '' :
            self.host = user_registration_info[0]
            self.user_name = user_registration_info[1];
            self.user_password = user_registration_info[2];
        else:
            self.user_name = user_registration_info[0];
            self.user_password = user_registration_info[1];

        #anon_messenger = AnonymousMessenger(self.message_manager.registration_msg(user_name,user_password), self.host,self.servicename)
        #anon_messenger.connect_to_server()

        self.logger.debug('Requesting registration')
        SetupTimer.start(Timer(System.Ahenk.registration_timeout(), timeout_function=self.registration_timeout,checker_func=self.is_registered, kwargs=None))
        anon_messenger = AnonymousMessenger(self.message_manager.registration_msg(self.user_name,self.user_password), self.host,self.servicename)
        anon_messenger.connect_to_server()

    def ldap_registration_request(self):
        self.logger.info('Requesting LDAP registration')
        self.messenger.send_Direct_message(self.message_manager.ldap_registration_msg())

    def registration_success(self, reg_reply):
        self.logger.info('Registration update starting')
        try:
            dn = str(reg_reply['agentDn'])
            self.logger.info('Current dn:' + dn)
            self.logger.info('updating host name and service')
            self.install_and_config_ldap(reg_reply)
            self.update_registration_attrs(dn)

        except Exception as e:
            self.logger.error('Registartion error. Error Message: {0}.'.format(str(e)))
            print(e)
            raise

    def install_and_config_ldap(self, reg_reply):
        self.logger.info('ldap install process starting')
        server_address = str(reg_reply['ldapServer'])
        dn = str(reg_reply['ldapBaseDn'])
        version = str(reg_reply['ldapVersion'])
        admin_dn = str(reg_reply['ldapUserDn']) # get user full dn from server.. password same
        admin_password = self.user_password # same user get from server

        (result_code, p_out, p_err) = self.util.execute("/bin/bash /usr/share/ahenk/plugins/ldap-login/scripts/ldap-login.sh {0} {1} {2} {3} {4}".format(
            server_address, "\'" + dn + "\'", "\'" + admin_dn + "\'", "\'" + admin_password + "\'", version))
        if result_code == 0:
            self.logger.info("Script has run successfully")
            self.change_pam_ldap_configs()
        else:
            self.logger.error("Script could not run successfully: " + p_err)
            print("ERROR ---> " + str(p_err))
            raise Exception('LDAP Ayarları yapılırken hata oluştu. Lütfen ağ bağlantınızı kontrol ediniz. Deponuzun güncel olduğundan emin olunuz.')


    def registration_error(self, reg_reply):
       self.re_register()


    def change_pam_ldap_configs(self):
        # pattern for clearing file data from spaces, tabs and newlines
        pattern = re.compile(r'\s+')

        pam_scripts_original_directory_path = "/usr/share/ahenk/pam_scripts_original"

        ldap_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/ldap"
        ldap_original_file_path = "/usr/share/pam-configs/ldap"
        ldap_configured_file_path = "/usr/share/ahenk/plugins/ldap-login/config-files/ldap"

        pam_script_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/pam_script"
        pam_script_original_file_path = "/usr/share/pam-configs/pam_script"
        pam_script_configured_file_path = "/usr/share/ahenk/plugins/ldap-login/config-files/pam_script"

        #create pam_scripts_original directory if not exists
        if not self.util.is_exist(pam_scripts_original_directory_path):
            self.logger.info("Creating {0} directory.".format(pam_scripts_original_directory_path))
            self.util.create_directory(pam_scripts_original_directory_path)

        if self.util.is_exist(ldap_back_up_file_path):
            self.logger.info("Changing {0} with {1}.".format(ldap_original_file_path, ldap_configured_file_path))
            self.util.copy_file(ldap_configured_file_path, ldap_original_file_path)
        else:
            self.logger.info("Backing up {0}".format(ldap_original_file_path))
            self.util.copy_file(ldap_original_file_path, ldap_back_up_file_path)
            self.logger.info("{0} file is replaced with {1}.".format(ldap_original_file_path, ldap_configured_file_path))
            self.util.copy_file(ldap_configured_file_path, ldap_original_file_path)

        if self.util.is_exist(pam_script_back_up_file_path):
            self.util.copy_file(pam_script_configured_file_path, pam_script_original_file_path)
            self.logger.info("{0} is replaced with {1}.".format(pam_script_original_file_path, pam_script_configured_file_path))
        else:
            self.logger.info("Backing up {0}".format(pam_script_original_file_path))
            self.util.copy_file(pam_script_original_file_path, pam_script_back_up_file_path)
            self.logger.info("{0} file is replaced with {1}".format(pam_script_original_file_path, pam_script_configured_file_path))
            self.util.copy_file(pam_script_configured_file_path, pam_script_original_file_path)

        (result_code, p_out, p_err) = self.util.execute("DEBIAN_FRONTEND=noninteractive pam-auth-update --package")
        if result_code == 0:
            self.logger.info("'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' has run successfully")
        else:
            self.logger.error("'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' could not run successfully: " + p_err)


        # Configure nsswitch.conf
        file_ns_switch = open("/etc/nsswitch.conf", 'r')
        file_data = file_ns_switch.read()

        # cleared file data from spaces, tabs and newlines
        text = pattern.sub('', file_data)

        is_configuration_done_before = False
        if ("passwd:compatldap" not in text):
            file_data = file_data.replace("passwd:         compat", "passwd:         compat ldap")
            is_configuration_done_before = True

        if ("group:compatldap" not in text):
            file_data = file_data.replace("group:          compat", "group:          compat ldap")
            is_configuration_done_before = True

        if ("shadow:compatldap" not in text):
            file_data = file_data.replace("shadow:         compat", "shadow:         compat ldap")
            is_configuration_done_before = True

        if is_configuration_done_before:
            self.logger.info("nsswitch.conf configuration has been completed")
        else:
            self.logger.info("nsswitch.conf is already configured")

        file_ns_switch.close()
        file_ns_switch = open("/etc/nsswitch.conf", 'w')
        file_ns_switch.write(file_data)
        file_ns_switch.close()

        # Configure lightdm.service
        # check if 99-pardus-xfce.conf exists if not create
        pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
        if not self.util.is_exist(pardus_xfce_path):
            self.logger.info("99-pardus-xfce.conf does not exist.")
            self.util.create_file(pardus_xfce_path)

            file_lightdm = open(pardus_xfce_path, 'a')
            file_lightdm.write("[Seat:*]\n")
            file_lightdm.write("greeter-hide-users=true")
            file_lightdm.close()
            self.logger.info("lightdm has been configured.")
        else:
            self.logger.info("99-pardus-xfce.conf exists. Delete file and create new one.")
            self.util.delete_file(pardus_xfce_path)
            self.util.create_file(pardus_xfce_path)

            file_lightdm = open(pardus_xfce_path, 'a')
            file_lightdm.write("[Seat:*]")
            file_lightdm.write("greeter-hide-users=true")
            file_lightdm.close()
            self.logger.info("lightdm.conf has been configured.")
        self.util.execute("systemctl restart nscd.service")
        self.logger.info("Operation finished")


    def update_registration_attrs(self, dn=None):
        self.logger.debug('Registration configuration is updating...')
        self.db_service.update('registration', ['dn', 'registered'], [dn, 1], ' registered = 0')

        if self.conf_manager.has_section('CONNECTION'):
            self.conf_manager.set('CONNECTION', 'uid',
                                  self.db_service.select_one_result('registration', 'jid', ' registered=1'))
            self.conf_manager.set('CONNECTION', 'password',
                                  self.db_service.select_one_result('registration', 'password', ' registered=1'))

            if  self.host and self.servicename:
                self.conf_manager.set('CONNECTION', 'host', self.host)
                self.conf_manager.set('CONNECTION', 'servicename', self.servicename)

            # TODO  get file path?
            with open('/etc/ahenk/ahenk.conf', 'w') as configfile:
                self.conf_manager.write(configfile)
            self.logger.debug('Registration configuration file is updated')



    def is_registered(self):
        try:
            if str(System.Ahenk.uid()):
                return True
            else:
                return False
        except:
            return False

    def is_ldap_registered(self):
        dn = self.db_service.select_one_result('registration', 'dn', 'registered = 1')
        if dn is not None and dn != '':
            return True
        else:
            return False

    def register(self, uuid_depend_mac=False):
        cols = ['jid', 'password', 'registered', 'params', 'timestamp']
        vals = [str(System.Os.hostname()), str(self.generate_uuid(uuid_depend_mac)), 0,
                str(self.get_registration_params()), str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))]

        self.db_service.delete('registration', ' 1==1 ')
        self.db_service.update('registration', cols, vals)
        self.logger.debug('Registration parameters were created')

    def get_registration_params(self):
        parts = []
        for part in System.Hardware.Disk.partitions():
            parts.append(part[0])

        params = {
            'ipAddresses': str(System.Hardware.Network.ip_addresses()).replace('[', '').replace(']', ''),
            'macAddresses': str(System.Hardware.Network.mac_addresses()).replace('[', '').replace(']', ''),
            'hostname': System.Os.hostname(),
            'os.name': System.Os.name(),
            'os.version': System.Os.version(),
            'os.kernel': System.Os.kernel_release(),
            'os.distributionName': System.Os.distribution_name(),
            'os.distributionId': System.Os.distribution_id(),
            'os.distributionVersion': System.Os.distribution_version(),
            'os.architecture': System.Os.architecture(),
            'hardware.cpu.architecture': System.Hardware.Cpu.architecture(),
            'hardware.cpu.logicalCoreCount': System.Hardware.Cpu.logical_core_count(),
            'hardware.cpu.physicalCoreCount': System.Hardware.Cpu.physical_core_count(),
            'hardware.disk.total': System.Hardware.Disk.total(),
            'hardware.disk.used': System.Hardware.Disk.used(),
            'hardware.disk.free': System.Hardware.Disk.free(),
            'hardware.disk.partitions': str(parts),
            'hardware.monitors': str(System.Hardware.monitors()),
            'hardware.screens': str(System.Hardware.screens()),
            'hardware.usbDevices': str(System.Hardware.usb_devices()),
            'hardware.printers': str(System.Hardware.printers()),
            'hardware.systemDefinitions': str(System.Hardware.system_definitions()),
            'hardware.model.version': str(System.Hardware.machine_model()),
            'hardware.memory.total': System.Hardware.Memory.total(),
            'hardware.network.ipAddresses': str(System.Hardware.Network.ip_addresses()),
            'sessions.userNames': str(System.Sessions.user_name()),
            'bios.releaseDate': System.BIOS.release_date()[1].replace('\n', '') if System.BIOS.release_date()[
                                                                                       0] == 0 else 'n/a',
            'bios.version': System.BIOS.version()[1].replace('\n', '') if System.BIOS.version()[0] == 0 else 'n/a',
            'bios.vendor': System.BIOS.vendor()[1].replace('\n', '') if System.BIOS.vendor()[0] == 0 else 'n/a',
            'hardware.baseboard.manufacturer': System.Hardware.BaseBoard.manufacturer()[1].replace('\n', '') if
            System.Hardware.BaseBoard.manufacturer()[0] == 0 else 'n/a',
            'hardware.baseboard.version': System.Hardware.BaseBoard.version()[1].replace('\n', '') if
            System.Hardware.BaseBoard.version()[0] == 0 else 'n/a',
            'hardware.baseboard.assetTag': System.Hardware.BaseBoard.asset_tag()[1].replace('\n', '') if
            System.Hardware.BaseBoard.asset_tag()[0] == 0 else 'n/a',
            'hardware.baseboard.productName': System.Hardware.BaseBoard.product_name()[1].replace('\n', '') if
            System.Hardware.BaseBoard.product_name()[0] == 0 else 'n/a',
            'hardware.baseboard.serialNumber': System.Hardware.BaseBoard.serial_number()[1].replace('\n', '') if
            System.Hardware.BaseBoard.serial_number()[0] == 0 else 'n/a',
        }

        return json.dumps(params)

    def unregister(self):
        self.logger.debug('Ahenk is unregistering...')
        self.db_service.delete('registration', ' 1==1 ')
        self.logger.debug('Ahenk is unregistered')

    def re_register(self):
        self.logger.debug('Reregistrating...')
        self.unregister()
        self.register(False)

    def generate_uuid(self, depend_mac=True):
        if depend_mac is False:
            self.logger.debug('uuid creating randomly')
            return uuid.uuid4()  # make a random UUID
        else:
            self.logger.debug('uuid creating according to mac address')
            return uuid.uuid3(uuid.NAMESPACE_DNS,
                              str(get_mac()))  # make a UUID using an MD5 hash of a namespace UUID and a mac address

    def generate_password(self):
        return uuid.uuid4()

    def registration_timeout(self):
        self.logger.error(
            'Could not reach registration response from Lider. Be sure XMPP server is reachable and it supports anonymous message, Lider is running properly '
            'and it is connected to XMPP server! Check your Ahenk configuration file (/etc/ahenk/ahenk.conf)')
        self.logger.error('Ahenk is shutting down...')
        print('Ahenk is shutting down...')

        Util.show_message("Etki alanı sunucusuna ulaşılamadı. Lütfen sunucu adresini kontrol ediniz....","HATA")

        System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))



    def purge_and_unregister(self):
        self.logger.info('Ahenk conf cleaned')
        self.logger.info('Ahenk conf cleaning from db')
        self.unregister()
        self.logger.info('Purge ldap packages')
        Util.execute("sudo apt purge libpam-ldap libnss-ldap ldap-utils -y")
        Util.execute("sudo apt autoremove -y")
        self.change_configs_after_purge()
        self.logger.info('purging successfull')
        self.logger.info('Cleaning ahenk conf..')
        self.clean()

        self.logger.info('Ahenk conf cleaned from db')
        self.logger.info('Enable Users')
        self.enable_local_users()

        Util.show_message("Ahenk etki alanından çıkarılmıştır.", "")

        if Util.show_message("Değişikliklerin etkili olması için sistem yeniden başlatmanız gerekmektedir.",""):
            Util.shutdown()

        System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))
        sys.exit(2)

    def change_configs_after_purge(self):

        # pattern for clearing file data from spaces, tabs and newlines
        pattern = re.compile(r'\s+')

        ldap_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/ldap"
        ldap_original_file_path = "/usr/share/pam-configs/ldap"

        pam_script_back_up_file_path = "/usr/share/ahenk/pam_scripts_original/pam_script"
        pam_script_original_file_path = "/usr/share/pam-configs/pam_script"

        if self.util.is_exist(ldap_back_up_file_path):
            self.logger.info("Replacing {0} with {1}".format(ldap_original_file_path, ldap_back_up_file_path))
            self.util.copy_file(ldap_back_up_file_path, ldap_original_file_path)
            self.logger.info("Deleting {0}".format(ldap_back_up_file_path))
            self.util.delete_file(ldap_back_up_file_path)

        if self.util.is_exist(pam_script_back_up_file_path):
            self.logger.info("Replacing {0} with {1}".format(pam_script_original_file_path, pam_script_back_up_file_path))
            self.util.copy_file(pam_script_back_up_file_path, pam_script_original_file_path)
            self.logger.info("Deleting {0}".format(pam_script_back_up_file_path))
            self.util.delete_file(pam_script_back_up_file_path)

        (result_code, p_out, p_err) = self.util.execute("DEBIAN_FRONTEND=noninteractive pam-auth-update --package")
        if result_code == 0:
            self.logger.info("'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' has run successfully")
        else:
            self.logger.error("'DEBIAN_FRONTEND=noninteractive pam-auth-update --package' could not run successfully: " + p_err)

        # Configure nsswitch.conf
        file_ns_switch = open("/etc/nsswitch.conf", 'r')
        file_data = file_ns_switch.read()

        # cleared file data from spaces, tabs and newlines
        text = pattern.sub('', file_data)

        did_configuration_change = False
        if "passwd:compatldap" in text:
            file_data = file_data.replace("passwd:         compat ldap", "passwd:         compat")
            did_configuration_change = True

        if "group:compatldap" in text:
            file_data = file_data.replace("group:          compat ldap", "group:          compat")
            did_configuration_change = True

        if "shadow:compatldap" in text:
            file_data = file_data.replace("shadow:         compat ldap", "shadow:         compat")
            did_configuration_change = True

        if did_configuration_change:
            self.logger.info("nsswitch.conf configuration has been configured")
        else:
            self.logger.info("nsswitch.conf has already been configured")

        file_ns_switch.close()
        file_ns_switch = open("/etc/nsswitch.conf", 'w')
        file_ns_switch.write(file_data)
        file_ns_switch.close()

        # Configure lightdm.service
        pardus_xfce_path = "/usr/share/lightdm/lightdm.conf.d/99-pardus-xfce.conf"
        if self.util.is_exist(pardus_xfce_path):
            self.logger.info("99-pardus-xfce.conf exists. Deleting file.")
            self.util.delete_file(pardus_xfce_path)

        self.util.execute("systemctl restart nscd.service")
        self.logger.info("Operation finished")


    def clean(self):
        print('Ahenk cleaning..')
        import configparser
        try:
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            db_path = config.get('BASE', 'dbPath')

            if Util.is_exist(System.Ahenk.fifo_file()):
                Util.delete_file(System.Ahenk.fifo_file())

            if Util.is_exist(db_path):
                Util.delete_file(db_path)

            if Util.is_exist(System.Ahenk.pid_path()):
                Util.delete_file(System.Ahenk.pid_path())

            config.set('CONNECTION', 'uid', '')
            config.set('CONNECTION', 'password', '')

            with open(System.Ahenk.config_path(), 'w') as file:
                config.write(file)
            file.close()
            print('Ahenk cleaned.')
        except Exception as e:
            print('Error while running clean command. Error Message {0}'.format(str(e)))

    def enable_local_users(self):
        passwd_cmd = 'passwd -u {}'
        change_home = 'usermod -m -d {0} {1}'
        change_username = 'usermod -l {0} {1}'
        content = self.util.read_file('/etc/passwd')
        for p in pwd.getpwall():
            if not sysx.shell_is_interactive(p.pw_shell):
                continue
            if p.pw_uid == 0:
                continue
            if p.pw_name in content:
                new_home_dir = p.pw_dir.rstrip('-local/') + '/'
                new_username = p.pw_name.rstrip('-local')
                self.util.execute(passwd_cmd.format(p.pw_name))
                self.util.execute(change_username.format(new_username, p.pw_name))
                self.util.execute(change_home.format(new_home_dir, new_username))
                self.logger.debug("User: '{0}' will be enabled and changed username and home directory of username".format(p.pw_name))


    def disable_local_users(self):
        passwd_cmd = 'passwd -l {}'
        change_home = 'usermod -m -d {0} {1}'
        change_username = 'usermod -l {0} {1}'
        content = Util.read_file('/etc/passwd')
        kill_all_process = 'killall -KILL -u {}'
        for p in pwd.getpwall():
            self.logger.info("User: '{0}' will be disabled and changed username and home directory of username".format(p.pw_name))
            if not sysx.shell_is_interactive(p.pw_shell):
                continue
            if p.pw_uid == 0:
                continue
            if p.pw_name in content:
                new_home_dir = p.pw_dir.rstrip('/') + '-local/'
                new_username = p.pw_name+'-local'
                Util.execute(kill_all_process.format(p.pw_name))
                Util.execute(passwd_cmd.format(p.pw_name))
                Util.execute(change_username.format(new_username, p.pw_name))
                Util.execute(change_home.format(new_home_dir, new_username))
