#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Cemre ALPSOY <cemre.alpsoy@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json


class ServiceManagement(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        self.service_status = 'service {} status'

    def start_stop_service(self, service_name, service_action):
        (result_code, p_out, p_err) = self.execute('service {0} {1}'.format(service_name, service_action))
        if result_code == 0:
            message = 'Service start/stop action was successful: '.format(service_action)

        else:
            message = 'Service action was unsuccessful: {0}, return code {1}'.format(service_action, str(result_code))

        self.logger.debug(message)
        return result_code, message

    def is_service_exist(self, service_name):
        result_code, p_out, p_err = self.execute("service --status-all")
        p_err = ' ' + p_err
        p_out = ' ' + p_out
        lines = p_out.split('\n')
        for line in lines:
            line_split = line.split(' ')
            if len(line_split) >= 5:
                result, out, err = self.execute(self.service_status.format(service_name))

                if 'Unknown job' not in str(err):
                    if line_split[len(line_split) - 4] == '+':
                        return "ACTIVE"
                    elif line_split[len(line_split) - 4] == '-':
                        return "INACTIVE"
                else:
                    return "NOTFOUND"

    def is_service_running(self, service_name):
        result_code, p_out, p_err = self.execute("ps -A")
        if service_name in p_out:
            return True
        else:
            return False

    def set_startup_service(self, service_name):
        (result_code, p_out, p_err) = self.execute('update-rc.d {} defaults'.format(service_name))

        if result_code == 0:
            message = 'Service startup action was successful: {}'.format(service_name)
        else:
            message = 'Service action was unsuccessful: {0}, return code {1}'.format(service_name, str(result_code))

        self.logger.debug('SERVICE' + message)
        return result_code, message

    def send_mail(self, stopped_services, all_services):
        if self.context.is_mail_send():
            mail_content = self.context.get_mail_content();
            if mail_content.__contains__('{stopped_services}'):
                mail_content = str(mail_content).replace('{stopped_services}', str(stopped_services));
            if mail_content.__contains__('{ahenk}'):
                mail_content = str(mail_content).replace('{ahenk}', str(self.Ahenk.dn()));

            self.context.set_mail_content(mail_content)

            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Servis izleme görevi başarıyla oluşturuldu.',
                                         data=json.dumps({
                                             'Result': 'İşlem Başarı ile gercekleştirildi',
                                             'mail_content': str(self.context.get_mail_content()),
                                             'mail_subject': str(self.context.get_mail_subject()),
                                             'mail_send': self.context.is_mail_send(),
                                             'services': all_services
                                         }),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)
        else:
            self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                         message='Servis izleme görevi başarıyla oluşturuldu.',
                                         data=json.dumps({
                                             'Result': 'İşlem Başarı ile gercekleştirildi',
                                             'mail_send': self.context.is_mail_send(),
                                             'services': all_services
                                         }),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

    def save_service(self, service):
        cols = ['serviceName', 'serviceStatus', 'timestamp', 'task_id'];
        values = [service["serviceName"], service["serviceStatus"], self.timestamp(),service['task_id']]
        return self.db_service.update('service', cols, values)

    def save_service_list(self, service_list):
        cols = ['serviceName', 'serviceStatus', 'timestamp', 'task_id'];
        values = [service_list[1], service_list[2], self.timestamp(), service_list[4]]
        return self.db_service.update('service', cols, values, 'id='+ str(service_list[0]))

    def get_service_status(self,service):
        service_name = service["serviceName"] + ".service"
        serviceStatus = service["serviceStatus"]
        result_code, p_out, p_err = self.execute("systemctl status " + str(service_name) + " | grep 'Active\|Loaded'")
        # self.logger.debug("-----p_out"+ str(p_out))
        if 'not-found' in p_out:
            service["serviceStatus"] = 'Service Not Found'

        elif 'running' in p_out:
            service["serviceStatus"] = 'Running'

        elif ('inactive' in p_out) or ('failed' in p_out):
            service["serviceStatus"] = 'Stopped'
        elif ('abandoned' in p_out):
            service["serviceStatus"] = 'Active Abandoned'
        else:
            service["serviceStatus"] = 'Running'

        return service

    def save_service_status(self, service):
        service= self.get_service_status(service)
        self.save_service(service)


    def get_services_status(self, services):
        for service in services:
            service= self.get_service_status(service)

    def get_services_status_and_save(self, services):
        for service in services:
            service= self.get_service_status(service)
            service_id_from_db=self.save_service(service)
            service['id']=service_id_from_db

    def handle_task(self):
        try:
            self.logger.debug("Service Management task is started.")
            services = self.data['serviceManageParam']
            task_id= self.context.get('task_id')
            # setting task id
            for srv in services:
                srv['task_id']=task_id
                srv['agentDn']=self.Ahenk.dn()
                srv['isServiceMonitoring']= True

            db_services = self.db_service.select('service', '*','task_id=' +str(task_id))

            if len(db_services) < 1:
                self.get_services_status_and_save(services)

                stopped_services = ''
                for servc in services:
                    if servc['serviceStatus'] == 'Stopped':
                        stopped_services += servc['serviceName'] + ' ,'

                if stopped_services != '':
                    self.send_mail(stopped_services, services)
                else:
                    self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Servis izleme görevi başarıyla oluşturuldu.',
                                             data=json.dumps({
                                                 'Result': 'İşlem Başarı ile gercekleştirildi',
                                                 'services': services,
                                             }),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                servicesStatusChanged =[]
                self.get_services_status(services)
                for srv in services:
                    isExist=False;
                    for srvDb in db_services:
                        if srv['serviceName'] == srvDb[1]:
                            isExist=True
                    if isExist ==False:
                        srv=self.get_service_status(srv)
                        self.save_service(srv)


                for srv in services:
                    for srvDb in db_services:
                        srvDbList=list(srvDb)
                        if  srv['serviceName'] == srvDb[1] and srv['serviceStatus'] != srvDbList[2]:
                            srvDbList[2]=srv['serviceStatus']
                            self.save_service_list(srvDbList)
                            servicesStatusChanged.append(srv)

                if len(servicesStatusChanged)>0:

                    stopped_services=''
                    for servc in servicesStatusChanged:
                        if servc['serviceStatus']== 'Stopped' :
                            stopped_services += servc['serviceName'] + ' ,'

                    if stopped_services != '':

                        self.send_mail(stopped_services,servicesStatusChanged)

                    else:
                        self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                                     message='Servis izleme görevi başarıyla oluşturuldu.',
                                                     data=json.dumps({
                                                         'Result': 'İşlem Başarı ile gercekleştirildi',
                                                         'services': servicesStatusChanged
                                                     }),
                                                     content_type=self.get_content_type().APPLICATION_JSON.value)
                else:
                    self.context.create_response(code=None,
                                                 message='Servis izleme görevi başarıyla oluşturuldu.',
                                                 data=None,
                                                 content_type=self.get_content_type().APPLICATION_JSON.value)


        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Servis yönetimi sırasında bir hata oluştu: {0}'.format(
                                             str(e)))


def handle_task(task, context):
    plugin = ServiceManagement(task, context)
    plugin.handle_task()
