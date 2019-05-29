#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

from base.scope import Scope
from base.util.util import Util
from base.system.system import System


class Agreement:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.message_manager = scope.get_message_manager()
        self.messenger = scope.get_messenger()
        self.db_service = scope.get_db_service()
        self.ask_path = '/usr/share/ahenk/base/agreement/ask.py'
        self.logger.debug('Instance initialized.')

    def agreement_contract_update(self):
        self.messenger.send_direct_message(self.message_manager.agreement_request_msg())
        self.logger.debug('Requested updated agreement contract from lider.')

    def check_agreement(self, username):
        self.logger.debug('Checking agreement for user {0}.'.format(username))
        contract_id = self.get_current_contract_id()
        if contract_id is None:
            self.logger.debug('There is no any contract in database.')
            contract_id = '-1'

        if self.db_service.select_one_result('agreement', 'id',
                                             " contract_id='{0}' and username='{1}' and choice='Y' "
                                                     .format(contract_id, username)) is not None:
            self.logger.debug('{0} answered agreement..')
            return True
        elif self.db_service.select_one_result('agreement', 'id',
                                               " contract_id='{0}' and username='{1}' and choice='N' ".format(
                                                   contract_id, username)) is not None:
            return False
        else:
            return None

    def get_current_contract_id(self):
        return self.db_service.select_one_result('contract', 'id', 'id =(select MAX(id) from contract)')

    def ask(self, username, display):

        result = self.db_service.select('contract', ['content', 'title', 'id'], 'id =(select MAX(id) from contract)')

        if result is None or len(result) < 1:
            content = 'Ahenk kurulu bu bilgisayarda ilk defa oturum açıyorsunuz. ' \
                      'Devam ederseniz Lider-Ahenk in bilgisayar üzeride yapacağı ' \
                      'tüm işlemlere onay vermiş sayılacaksınız. Kabul ediyor musunuz?' \
                      ' \n(Tanımlanmış zaman aralığında olumlu cevaplandırmadığınız takdirde oturumunuz ' \
                      'sonlandırılacaktır.)'
            title = 'Ahenk Kurulu Bilgisayar Kullanım Anlaşması'
            contract_id = '-1'
        else:
            content = str(result[0][0])
            title = result[0][1]
            contract_id = result[0][2]
        try:
            agreement_path = System.Ahenk.received_dir_path() + Util.generate_uuid()
            Util.write_file(agreement_path, content)
            Util.set_permission(agreement_path, 777)
            command = 'export DISPLAY={0};su - {1} -c \'python3 {2} \"$(cat {3})\" \"{4}\"\''.format(display, username,
                                                                                                     self.ask_path,
                                                                                                     agreement_path,
                                                                                                     title)
            result_code, p_out, p_err = Util.execute(command)

            pout = str(p_out).replace('\n', '')
            if pout != 'Error':
                if pout == 'Y':
                    self.logger.debug('Agreement was accepted by {0}.'.format(username))
                    self.db_service.update('agreement', self.db_service.get_cols('agreement'),
                                           [contract_id, username, Util.timestamp(), 'Y'])
                elif pout == 'N':
                    self.db_service.update('agreement', self.db_service.get_cols('agreement'),
                                           [contract_id, username, Util.timestamp(), 'N'])
                    self.logger.debug(
                        'Agreement was ignored by {0}. Session will be closed'.format(username))
                else:
                    self.logger.error(
                        'A problem occurred while executing ask.py. Error Message: {0}'.format(str(pout)))
                Util.delete_file(agreement_path)
            else:
                self.logger.error(
                    'A problem occurred while executing ask.py (Probably argument fault). Error Message: {0}'.format(
                        str(pout)))

        except Exception as e:
            self.logger.error(
                'A Problem occurred while displaying agreement. Error Message: {0}'.format(str(e)))
