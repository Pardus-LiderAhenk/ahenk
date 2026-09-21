import json

from base.plugin.abstract_plugin import AbstractPlugin


class GetDeviceRules(AbstractPlugin):
    """Handles retrieval of current device access rules from the system"""
    
    def __init__(self, task, context):
        super(GetDeviceRules, self).__init__()
        self.task = task
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()
        
    def handle_task(self):
        """Main task handler - retrieves all device rules and sends response"""
        try:
            device_rules = self.get_all_device_rules()
            
            self.logger.info('Device rules retrieved successfully: {0}'.format(str(device_rules)))
            
            self.context.create_response(
                code=self.message_code.TASK_PROCESSED.value,
                message='Aygıt yönetimi kuralları başarıyla alındı.',
                data=json.dumps(device_rules),
                content_type=self.get_content_type().APPLICATION_JSON.value
            )
        except Exception as e:
            self.logger.error('Error occurred while getting device rules. Error: {0}'.format(str(e)))
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message='Aygıt yönetimi kuralları getirilirken hata oluştu: {0}'.format(str(e))
            )
    
    def get_all_device_rules(self):
        """
        Retrieves all device rules and returns them as a dictionary
        Returns dict with keys: storage, printer, webcam, mouseKeyboard, microphone
        """
        device_rules = {}
        
        # Get storage (USB) rules
        storage_status = self.get_device_rule_status('/etc/udev/rules.d/99-block-storage.rules')
        if storage_status is not None:
            device_rules['storage'] = storage_status
        
        # Get printer rules
        printer_status = self.get_device_rule_status('/etc/udev/rules.d/99-block-printer.rules')
        if printer_status is not None:
            device_rules['printer'] = printer_status
        
        # Get webcam rules
        webcam_status = self.get_device_rule_status('/etc/udev/rules.d/99-block-webcam.rules')
        if webcam_status is not None:
            device_rules['webcam'] = webcam_status
        
        # Get mouse/keyboard rules
        mousekeyboard_status = self.get_device_rule_status('/etc/udev/rules.d/99-block-usbhid.rules')
        if mousekeyboard_status is not None:
            device_rules['mouseKeyboard'] = mousekeyboard_status

        # Mikrofon kuralı kontrolü (WirePlumber config dosyasına bakar)
        microphone_status = self.get_device_rule_status('/etc/wireplumber/wireplumber.conf.d/90-disable-microphones.conf')
        if microphone_status is not None:
            device_rules['microphone'] = microphone_status
        
        return device_rules
    
    def get_device_rule_status(self, file_path):
        """
        Checks if a block rule or configuration file exists.
        
        Args:
            file_path: Full path to the rule/config file
        
        Returns:
            "0" if block file exists (device is blocked/disabled)
            "1" if block file does not exist (device is allowed/enabled)
            None if unable to determine
        """
        try:
            # Dosya varsa aygıt engellenmiştir (0), yoksa izin verilmiştir (1)
            if self.is_exist(file_path):
                self.logger.debug('Block file found: {0} -> Status: BLOCKED (0)'.format(file_path))
                return "0"
            else:
                self.logger.debug('Block file not found: {0} -> Status: ALLOWED (1)'.format(file_path))
                return "1"
        except Exception as e:
            self.logger.error('Error checking status for {0}: {1}'.format(file_path, str(e)))
            return None


def handle_task(task, context):
    """Entry point for task processing"""
    handler = GetDeviceRules(task, context)
    handler.handle_task()