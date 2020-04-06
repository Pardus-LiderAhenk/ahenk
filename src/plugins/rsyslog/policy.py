#!/usr/bin/python
# -*- coding: utf-8 -*-


# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

import json

from base.plugin.abstract_plugin import AbstractPlugin


class Rsyslog(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.rsyslog_path = '/etc/rsyslog.d/ahenk.conf'
        self.default_config = "#  /etc/rsyslog.conf\tConfiguration file for rsyslog.\n#\n#\t\t\tFor more information see\n#\t\t\t/usr/share/doc/rsyslog-doc/html/rsyslog_conf.html\n#\n#  Default logging rules can be found in /etc/rsyslog.d/50-default.conf\n\n\n#################\n#### MODULES ####\n#################\n\n$ModLoad imuxsock # provides support for local system logging\n$ModLoad imklog   # provides kernel logging support\n#$ModLoad immark  # provides --MARK-- message capability\n\n# provides UDP syslog reception\n#$ModLoad imudp\n#$UDPServerRun 514\n\n# provides TCP syslog reception\n$ModLoad imtcp\n$InputTCPServerRun 514\n\n# Enable non-kernel facility klog messages\n$KLogPermitNonKernelFacility on\n\n###########################\n#### GLOBAL DIRECTIVES ####\n###########################\n\n#\n# Use traditional timestamp format.\n# To enable high precision timestamps, comment out the following line.\n#\n$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat\n\n# Filter duplicated messages\n$RepeatedMsgReduction on\n\n#\n# Set the default permissions for all log files.\n#\n$FileOwner syslog\n$FileGroup adm\n$FileCreateMode 0640\n$DirCreateMode 0755\n$Umask 0022\n$PrivDropToUser syslog\n$PrivDropToGroup syslog\n\n#\n# Where to place spool and state files\n#\n$WorkDirectory /var/spool/rsyslog\n\n#\n# Include all config files in /etc/rsyslog.d/\n#\n$IncludeConfig /etc/rsyslog.d/*.conf\n\n#RULE_STR#\n\n#\n# Logging for the mail system.  Split it up so that\n# it is easy to write scripts to parse these files.\n#\n#mail.info\t\t\t-/var/log/mail.info\n#mail.warn\t\t\t-/var/log/mail.warn\nmail.err\t\t\t/var/log/mail.err\n\n#\n# Logging for INN news system.\n#\nnews.crit\t\t\t/var/log/news/news.crit\nnews.err\t\t\t/var/log/news/news.err\nnews.notice\t\t\t-/var/log/news/news.notice\n\n#\n# Some \"catch-all\" log files.\n#\n#*.=debug;\\\n#\tauth,authpriv.none;\\\n#\tnews.none;mail.none\t-/var/log/debug\n#*.=info;*.=notice;*.=warn;\\\n#\tauth,authpriv.none;\\\n#\tcron,daemon.none;\\\n#\tmail,news.none\t\t-/var/log/messages\n\n#\n# Emergencies are sent to everybody logged in.\n#\n*.emerg                                :omusrmsg:*\n\n#\n# I like to have messages displayed on the console, but only on a virtual\n# console I usually leave idle.\n#\n#daemon,mail.*;\\\n#\tnews.=crit;news.=err;news.=notice;\\\n#\t*.=debug;*.=info;\\\n#\t*.=notice;*.=warn\t/dev/tty8\n\n# The named pipe /dev/xconsole is for the `xconsole\' utility.  To use it,\n# you must invoke `xconsole\' with the `-file\' option:\n# \n#    $ xconsole -file /dev/xconsole [...]\n#\n# NOTE: adjust the list below, or you\'ll go crazy if you have a reasonably\n#      busy site..\n#\ndaemon.*;mail.*;\\\n\tnews.err;\\\n\t*.=debug;*.=info;\\\n\t*.=notice;*.=warn\t|/dev/xconsole"
        self.rsyslog_conf = ""
        self.remote_conf = ""
        self.protocol = '@@'

        self.rsyslog_conf_file_path = '/etc/rsyslog.conf'
        self.remote_conf_file_path = '/etc/rsyslog.d/remote.conf'
        self.log_rotate_conf_file_path = '/etc/logrotate.conf'

    def handle_policy(self):
        try:
            if str(json.loads(self.data)['PROTOCOL']) == 'UDP':
                self.protocol = '@'
            self.logger.debug('Handling profile ...')
            items = json.loads(self.data)['items']
            for item in items:
                if str(item['isLocal']).upper() == 'EVET' or str(item['isLocal']).upper() == 'YES':
                    self.rsyslog_conf += str(item['recordDescription']) + '\t' + str(item['logFilePath']) + '\n'
                else:
                    self.remote_conf += str(item['recordDescription']) + ' ' + self.protocol + str(
                        json.loads(self.data)['ADDRESS']) + ':' + str(json.loads(self.data)['PORT']) + '\n'
            self.rsyslog_conf = self.default_config.replace("#RULE_STR#", self.rsyslog_conf)
            self.logger.debug('Rsyslog config files are ready')
            (result_code, p_out, p_err) = self.execute(
                "find /etc/rsyslog.d/ -name '*.conf' -exec bash -c 'sudo mv ${0/conf/conf.orig}' {} \;", shell=True)
            if str(result_code) == '0':
                self.logger.debug('Backup up old config files.')
            else:
                self.logger.debug('Error while backing up old config files')

            rsyslog_conf_contents = str(self.rsyslog_conf).strip()
            self.logger.debug(self.rsyslog_conf_file_path + ': \n' + rsyslog_conf_contents + '\n')

            config_file = open(self.rsyslog_conf_file_path, 'w+')
            config_file.write(rsyslog_conf_contents)
            config_file.close()
            remote_conf_contents = str(self.remote_conf).strip()
            # self.logger.debug(self.remote_conf_file_path + ': \n' + remote_conf_contents + '\n')
            if remote_conf_contents and not remote_conf_contents.isspace():
                self.logger.debug('Updating remote.conf')
                remote_config_file = open(self.remote_conf_file_path, 'w+')
                remote_config_file.write(remote_conf_contents)
                remote_config_file.close()
            else:
                self.logger.debug('CANNOT update remote.conf')
            self.execute('service rsyslog restart', shell=True)
            self.logger.debug('Rsyslog service restarted.')
            self.logger.debug('Processing logrotate config')
            rotation_interval = str(json.loads(self.data)['rotationInterval'])
            keep_back_logs = str(json.loads(self.data)['keepBacklogs'])
            max_size = str(json.loads(self.data)['maxSize'])
            create_new_log_files = json.loads(self.data)['createNewLogFiles']
            compress_old_log_files = json.loads(self.data)['compressOldLogFiles']
            missing_ok = json.loads(self.data)['missingOk']
            f = open(self.log_rotate_conf_file_path, 'w')
            if rotation_interval:
                f.write(rotation_interval + '\n')
            else:
                f.write('weekly\n')
            if keep_back_logs:
                f.write('rotate ' + keep_back_logs + '\n')
            else:
                f.write('rotate 4\n')
            if max_size:
                f.write('maxsize ' + max_size + 'M\n')
            if create_new_log_files:
                f.write('create\n')
            if compress_old_log_files:
                f.write('compress\n')
            if missing_ok:
                f.write('missingok\n')
            f.write('include /etc/logrotate.d\n')
            f.close()
            self.logger.debug('Rsyslog Profile Processed')
            self.context.create_response(code=self.message_code.POLICY_PROCESSED.value,
                                         message='Ajan Rsyslog Profili başarıyla uygulandı.',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(
                'A problem occurred while applying rsyslog profile. Error Message: {0}'.format(str(e)))
            self.context.create_response(code=self.message_code.POLICY_ERROR.value,
                                         message='Rsyslog Profili uygulanırken bir hata oluştu.',
                                         content_type=self.get_content_type().APPLICATION_JSON.value)


def handle_policy(profile_data, context):
    plugin = Rsyslog(profile_data, context)
    plugin.handle_policy()


class Item(object):
    record_description = ""
    log_file_path = ""

    def __init__(self, record_description, log_file_path):
        self.record_description = record_description
        self.log_file_path = log_file_path
