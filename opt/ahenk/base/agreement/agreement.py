from base.Scope import Scope
from base.util.util import Util


class Agreement:
    def __init__(self):
        scope = Scope().getInstance()
        self.logger = scope.getLogger()
        self.message_manager = scope.getMessageManager()
        self.messenger = scope.getMessenger()
        self.db_service = scope.getDbService()
        self.ask_path = '/opt/ahenk/base/agreement/ask.py'
        self.logger.debug('[Agreement] Instance initialized.')

    def agreement_contract_update(self):
        self.messenger.send_direct_message(self.message_manager.agreement_request_msg())
        self.logger.debug('[Agreement] Requested updated agreement contract from lider.')

    def check_agreement(self, username):
        self.logger.debug('[Agreement] Checking agreement for user {}.'.format(username))
        contract_id = self.get_current_contract_id()
        if contract_id is None:
            self.logger.debug('[Agreement] There is no any contract in database.')
            if self.db_service.select_one_result('agreement', 'id', " contract_id='{0}' and username='{1}' and choice='Y' ".format('-1', username)) is None:
                return False
            else:
                return True
        else:
            if self.db_service.select_one_result('agreement', 'id', " contract_id='{0}' and username='{1}' and choice='Y' ".format(contract_id, username)) is None:
                return False
            else:
                return True

    def get_current_contract_id(self):
        return self.db_service.select_one_result('contract', 'id', 'id =(select MAX(id) from contract)')

    def ask(self, username, display):

        result = self.db_service.select('contract', ['content', 'title', 'id'], 'id =(select MAX(id) from contract)')

        # TODO sec read from conf file

        if result is None or len(result) < 1:
            content = 'Ahenk kurulu bu bilgisayarda ilk defa oturum açıyorsunuz. ' \
                      'Devam ederseniz Lider-Ahenk in bilgisayar üzeride yapacağı ' \
                      'tüm işlemlere onay vermiş sayılacaksınız. Kabul ediyor musunuz?' \
                      ' \n({} saniye içinde olumlu cevaplandırmadığınız takdirde oturumunuz ' \
                      'sonlandırılacaktır.)'.format(10)
            title = 'Ahenk Kurulu Bilgisayar Kullanım Anlaşması'
            contract_id = '-1'
        else:
            content = result[0]
            title = result[1]
            contract_id = result[2]

        command = 'export DISPLAY={0};python3 {1} \'{2}\' \'{3}\' '.format(display, self.ask_path, content, title)
        result_code, p_out, p_err = Util.execute(command, as_user=username)
        pout = str(p_out).replace('\n', '')
        if pout != 'Error':
            if pout == 'Y':
                self.logger.debug('[Agreement] Agreement was accepted by {}.'.format(username))
                self.db_service.update('agreement', self.db_service.get_cols('agreement'), [contract_id, username, Util.timestamp(), 'Y'])
            elif pout == 'N':
                self.db_service.update('agreement', self.db_service.get_cols('agreement'), [contract_id, username, Util.timestamp(), 'N'])
                self.logger.debug('[Agreement] Agreement was ignored by {}. Session will be closed'.format(username))
                Util.execute('pkill -9 -u {}'.format(username))
            else:
                self.logger.error('[Agreement] A problem occurred while executing ask.py. Error Message: {}'.format(str(pout)))
        else:
            self.logger.error('[Agreement] A problem occurred while executing ask.py (Probably argument fault). Error Message: {}'.format(str(pout)))
