#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Registration class
"""
import pytest
import json
import uuid
from unittest.mock import MagicMock, Mock, patch, PropertyMock
from datetime import datetime
import sys

# Mock dependencies before importing Registration
# Mock System module first to avoid cpuinfo import error
mock_system_module = MagicMock()
sys.modules['base.system.system'] = mock_system_module

# Mock other dependencies
sys.modules['base.messaging.anonymous_messenger'] = MagicMock()
sys.modules['base.timer.setup_timer'] = MagicMock()
sys.modules['base.timer.timer'] = MagicMock()
sys.modules['base.system.disk_info'] = MagicMock()
sys.modules['base.registration.execute_sssd_authentication'] = MagicMock()
sys.modules['base.registration.execute_sssd_ad_authentication'] = MagicMock()
sys.modules['base.registration.execute_cancel_sssd_authentication'] = MagicMock()
sys.modules['base.registration.execute_cancel_sssd_ad_authentication'] = MagicMock()

# Now we can import Registration
from base.registration.registration import Registration


class TestRegistration:
    """Test cases for Registration class"""
    
    @patch('base.registration.registration.Scope')
    @patch('base.registration.registration.System')
    @patch('base.registration.registration.Util')
    @patch('base.registration.registration.ExecuteSSSDAuthentication')
    @patch('base.registration.registration.ExecuteSSSDAdAuthentication')
    @patch('base.registration.registration.ExecuteCancelSSSDAuthentication')
    @patch('base.registration.registration.ExecuteCancelSSSDAdAuthentication')
    def test_init_when_registered(self, mock_cancel_ad, mock_cancel_sssd, mock_ad, mock_sssd, 
                                   mock_util_class, mock_system_class, mock_scope_class):
        """Test Registration initialization when already registered"""
        # Setup mock scope
        mock_scope = MagicMock()
        mock_logger = MagicMock()
        mock_message_manager = MagicMock()
        mock_event_manager = MagicMock()
        mock_messenger = MagicMock()
        mock_conf_manager = MagicMock()
        mock_db_service = MagicMock()
        
        mock_scope.get_logger.return_value = mock_logger
        mock_scope.get_message_manager.return_value = mock_message_manager
        mock_scope.get_event_manager.return_value = mock_event_manager
        mock_scope.get_messenger.return_value = mock_messenger
        mock_scope.get_configuration_manager.return_value = mock_conf_manager
        mock_scope.get_db_service.return_value = mock_db_service
        
        # Mock Scope() constructor and get_instance()
        mock_scope_instance = MagicMock()
        mock_scope_instance.get_instance.return_value = mock_scope
        mock_scope_class.return_value = mock_scope_instance
        
        # Mock System.Ahenk.uid() to return a value (registered)
        mock_ahenk = MagicMock()
        mock_ahenk.uid.return_value = 'test_uid'
        mock_system = MagicMock()
        mock_system.Ahenk = mock_ahenk
        mock_system_class.System = mock_system
        
        registration = Registration()
        
        # Verify event registration - check that register_event was called
        assert mock_event_manager.register_event.called
        calls = mock_event_manager.register_event.call_args_list
        event_names = [call[0][0] for call in calls]
        assert 'REGISTRATION_SUCCESS' in event_names
        assert 'REGISTRATION_ERROR' in event_names
        
        # Should log debug message (already registered)
        mock_logger.debug.assert_called_with('Ahenk already registered')
    
    @patch('base.registration.registration.Scope')
    @patch('base.registration.registration.System')
    @patch('base.registration.registration.Util')
    @patch('base.registration.registration.ExecuteSSSDAuthentication')
    @patch('base.registration.registration.ExecuteSSSDAdAuthentication')
    @patch('base.registration.registration.ExecuteCancelSSSDAuthentication')
    @patch('base.registration.registration.ExecuteCancelSSSDAdAuthentication')
    @patch.object(Registration, 'register')
    def test_init_when_not_registered(self, mock_register, mock_cancel_ad, mock_cancel_sssd, mock_ad, mock_sssd,
                                       mock_util_class, mock_system_class, mock_scope_class):
        """Test Registration initialization when not registered"""
        # Setup mock scope
        mock_scope = MagicMock()
        mock_logger = MagicMock()
        mock_message_manager = MagicMock()
        mock_event_manager = MagicMock()
        mock_messenger = MagicMock()
        mock_conf_manager = MagicMock()
        mock_db_service = MagicMock()
        
        mock_scope.get_logger.return_value = mock_logger
        mock_scope.get_message_manager.return_value = mock_message_manager
        mock_scope.get_event_manager.return_value = mock_event_manager
        mock_scope.get_messenger.return_value = mock_messenger
        mock_scope.get_configuration_manager.return_value = mock_conf_manager
        mock_scope.get_db_service.return_value = mock_db_service
        
        # Mock Scope() constructor and get_instance()
        mock_scope_instance = MagicMock()
        mock_scope_instance.get_instance.return_value = mock_scope
        mock_scope_class.return_value = mock_scope_instance
        
        # Mock System.Ahenk.uid() to return empty (not registered)
        mock_ahenk = MagicMock()
        mock_ahenk.uid.return_value = ''
        mock_system = MagicMock()
        mock_system.Ahenk = mock_ahenk
        mock_system_class.System = mock_system
        
        # Patch System in the registration module so is_registered() uses the mock
        with patch('base.registration.registration.System', mock_system):
            registration = Registration()
        
        # Should call register with True
        mock_register.assert_called_once_with(True)
    
    @patch('base.registration.registration.System')
    def test_is_registered_true(self, mock_system_class):
        """Test is_registered when uid exists"""
        mock_ahenk = MagicMock()
        mock_ahenk.uid.return_value = 'test_uid'
        mock_system_class.System = MagicMock()
        mock_system_class.System.Ahenk = mock_ahenk
        
        registration = Registration.__new__(Registration)
        result = registration.is_registered()
        
        assert result is True
    
    def test_is_registered_false_when_empty(self, mock_scope):
        """Test is_registered when uid is empty"""
        mock_ahenk = MagicMock()
        mock_ahenk.uid.return_value = ''
        
        # Create a proper System mock structure
        mock_system = MagicMock()
        mock_system.Ahenk = mock_ahenk
        
        registration = Registration.__new__(Registration)
        
        # Patch System in the registration module
        with patch('base.registration.registration.System', mock_system):
            result = registration.is_registered()
        
        # str('') is '', which is falsy, so should return False
        assert result is False
    
    def test_is_registered_false_on_exception(self, mock_scope):
        """Test is_registered when exception occurs"""
        mock_ahenk = MagicMock()
        mock_ahenk.uid.side_effect = Exception("Error")
        
        # Create a proper System mock structure
        mock_system = MagicMock()
        mock_system.Ahenk = mock_ahenk
        
        registration = Registration.__new__(Registration)
        
        # Patch System in the registration module
        with patch('base.registration.registration.System', mock_system):
            result = registration.is_registered()
        
        assert result is False
    
    def test_is_ldap_registered_true(self, mock_scope):
        """Test is_ldap_registered when dn exists"""
        mock_db = MagicMock()
        mock_db.select_one_result.return_value = 'cn=test,dc=example,dc=com'
        
        registration = Registration.__new__(Registration)
        registration.db_service = mock_db
        
        result = registration.is_ldap_registered()
        
        assert result is True
        mock_db.select_one_result.assert_called_once_with('registration', 'dn', 'registered = 1')
    
    def test_is_ldap_registered_false_when_none(self, mock_scope):
        """Test is_ldap_registered when dn is None"""
        mock_db = MagicMock()
        mock_db.select_one_result.return_value = None
        
        registration = Registration.__new__(Registration)
        registration.db_service = mock_db
        
        result = registration.is_ldap_registered()
        
        assert result is False
    
    def test_is_ldap_registered_false_when_empty(self, mock_scope):
        """Test is_ldap_registered when dn is empty"""
        mock_db = MagicMock()
        mock_db.select_one_result.return_value = ''
        
        registration = Registration.__new__(Registration)
        registration.db_service = mock_db
        
        result = registration.is_ldap_registered()
        
        assert result is False
    
    @patch('base.registration.registration.System')
    @patch('base.registration.registration.datetime')
    def test_register(self, mock_datetime, mock_system_class, mock_scope):
        """Test register method"""
        mock_db = MagicMock()
        mock_logger = MagicMock()
        mock_datetime.datetime.now.return_value.strftime.return_value = '01-01-2024 12:00'
        
        registration = Registration.__new__(Registration)
        registration.db_service = mock_db
        registration.logger = mock_logger
        registration.util = MagicMock()
        
        # Mock get_registration_params
        with patch.object(Registration, 'get_registration_params', return_value='{"test": "data"}'):
            with patch.object(Registration, 'generate_uuid', return_value='test-uuid'):
                registration.register(True)
                
                # Verify database operations
                mock_db.delete.assert_called_once_with('registration', ' 1==1 ')
                assert mock_db.update.called
                mock_logger.debug.assert_called_with('Registration parameters were created')
    
    def test_unregister(self, mock_scope):
        """Test unregister method"""
        mock_db = MagicMock()
        mock_logger = MagicMock()
        
        registration = Registration.__new__(Registration)
        registration.db_service = mock_db
        registration.logger = mock_logger
        
        registration.unregister()
        
        # Verify database delete
        mock_db.delete.assert_called_once_with('registration', ' 1==1 ')
        mock_logger.debug.assert_any_call('Ahenk is unregistering...')
        mock_logger.debug.assert_any_call('Ahenk is unregistered')
    
    @patch('base.registration.registration.System')
    @patch('base.registration.registration.datetime')
    def test_re_register(self, mock_datetime, mock_system_class, mock_scope):
        """Test re_register method"""
        mock_db = MagicMock()
        mock_logger = MagicMock()
        mock_datetime.datetime.now.return_value.strftime.return_value = '01-01-2024 12:00'
        
        registration = Registration.__new__(Registration)
        registration.db_service = mock_db
        registration.logger = mock_logger
        registration.util = MagicMock()
        
        with patch.object(Registration, 'unregister') as mock_unregister:
            with patch.object(Registration, 'register') as mock_register:
                registration.re_register()
                
                mock_unregister.assert_called_once()
                mock_register.assert_called_once_with(False)
                mock_logger.debug.assert_called_with('Reregistrating...')
    
    @patch('base.registration.registration.uuid')
    @patch('base.registration.registration.get_mac')
    def test_generate_uuid_with_mac(self, mock_get_mac, mock_uuid_module, mock_scope):
        """Test generate_uuid when depend_mac is True"""
        mock_get_mac.return_value = 123456789
        mock_uuid_module.uuid3.return_value = 'uuid-with-mac'
        mock_uuid_module.NAMESPACE_DNS = uuid.NAMESPACE_DNS
        
        mock_logger = MagicMock()
        registration = Registration.__new__(Registration)
        registration.logger = mock_logger
        
        result = registration.generate_uuid(True)
        
        assert result == 'uuid-with-mac'
        mock_uuid_module.uuid3.assert_called_once_with(uuid.NAMESPACE_DNS, '123456789')
        mock_logger.debug.assert_called_with('uuid creating according to mac address')
    
    @patch('base.registration.registration.uuid')
    def test_generate_uuid_without_mac(self, mock_uuid_module, mock_scope):
        """Test generate_uuid when depend_mac is False"""
        mock_uuid_module.uuid4.return_value = 'random-uuid'
        
        mock_logger = MagicMock()
        registration = Registration.__new__(Registration)
        registration.logger = mock_logger
        
        result = registration.generate_uuid(False)
        
        assert result == 'random-uuid'
        mock_uuid_module.uuid4.assert_called_once()
        mock_logger.debug.assert_called_with('uuid creating randomly')
    
    @patch('base.registration.registration.uuid')
    def test_generate_password(self, mock_uuid_module, mock_scope):
        """Test generate_password method"""
        mock_uuid_module.uuid4.return_value = 'password-uuid'
        
        registration = Registration.__new__(Registration)
        
        result = registration.generate_password()
        
        assert result == 'password-uuid'
        mock_uuid_module.uuid4.assert_called_once()
    
    @patch('base.registration.registration.System')
    @patch('base.registration.registration.DiskInfo')
    @patch('base.registration.registration.Util')
    def test_get_registration_params(self, mock_util_class, mock_disk_info_class, mock_system_class, mock_scope):
        """Test get_registration_params method"""
        # Setup System mocks
        mock_system_class.System.Hardware.Disk.partitions.return_value = [('/dev/sda1',), ('/dev/sda2',)]
        mock_system_class.System.Hardware.Network.ip_addresses.return_value = ['192.168.1.1']
        mock_system_class.System.Hardware.Network.mac_addresses.return_value = ['00:11:22:33:44:55']
        mock_system_class.System.Os.hostname.return_value = 'test-hostname'
        mock_system_class.System.Os.name.return_value = 'Linux'
        mock_system_class.System.Os.version.return_value = '5.15.0'
        mock_system_class.System.Os.kernel_release.return_value = '5.15.0-139-generic'
        mock_system_class.System.Os.distribution_name.return_value = 'Ubuntu'
        mock_system_class.System.Os.distribution_id.return_value = 'ubuntu'
        mock_system_class.System.Os.distribution_version.return_value = '22.04'
        mock_system_class.System.Os.architecture.return_value = 'x86_64'
        mock_system_class.System.Hardware.Cpu.architecture.return_value = 'x86_64'
        mock_system_class.System.Hardware.Cpu.logical_core_count.return_value = 4
        mock_system_class.System.Hardware.Cpu.physical_core_count.return_value = 2
        mock_system_class.System.Hardware.Cpu.brand.return_value = 'Intel Core i5'
        mock_system_class.System.Hardware.Disk.total.return_value = 1000000000
        mock_system_class.System.Hardware.Disk.used.return_value = 500000000
        mock_system_class.System.Hardware.Disk.free.return_value = 500000000
        mock_system_class.System.Hardware.monitors.return_value = []
        mock_system_class.System.Hardware.screens.return_value = []
        mock_system_class.System.Hardware.usb_devices.return_value = []
        mock_system_class.System.Hardware.printers.return_value = []
        mock_system_class.System.Hardware.system_definitions.return_value = {}
        mock_system_class.System.Hardware.machine_model.return_value = 'Test Model'
        mock_system_class.System.Hardware.Memory.total.return_value = 8000000000
        mock_system_class.System.Sessions.user_name.return_value = ['user1']
        mock_system_class.System.BIOS.release_date.return_value = (0, '01/01/2020\n')
        mock_system_class.System.BIOS.version.return_value = (0, '1.0\n')
        mock_system_class.System.BIOS.vendor.return_value = (0, 'Test Vendor\n')
        mock_system_class.System.Hardware.BaseBoard.manufacturer.return_value = (0, 'Test Manufacturer\n')
        mock_system_class.System.Hardware.BaseBoard.version.return_value = (0, '1.0\n')
        mock_system_class.System.Hardware.BaseBoard.asset_tag.return_value = (0, 'TAG123\n')
        mock_system_class.System.Hardware.BaseBoard.product_name.return_value = (0, 'Test Product\n')
        mock_system_class.System.Hardware.BaseBoard.serial_number.return_value = (0, 'SN123456\n')
        mock_util_class.Util.get_agent_version.return_value = '1.0.0'
        # Fix: DiskInfo.get_all_disks() should return a tuple of two lists
        mock_disk_info_class.DiskInfo.get_all_disks.return_value = ([], [])
        
        registration = Registration.__new__(Registration)
        registration.util = MagicMock()
        
        # Create proper System mock with all required attributes
        mock_system = MagicMock()
        mock_system.Hardware.Disk.partitions.return_value = [('/dev/sda1',), ('/dev/sda2',)]
        mock_system.Hardware.Network.ip_addresses.return_value = ['192.168.1.1']
        mock_system.Hardware.Network.mac_addresses.return_value = ['00:11:22:33:44:55']
        mock_system.Os.hostname.return_value = 'test-hostname'
        mock_system.Os.name.return_value = 'Linux'
        mock_system.Os.version.return_value = '5.15.0'
        mock_system.Os.kernel_release.return_value = '5.15.0-139-generic'
        mock_system.Os.distribution_name.return_value = 'Ubuntu'
        mock_system.Os.distribution_id.return_value = 'ubuntu'
        mock_system.Os.distribution_version.return_value = '22.04'
        mock_system.Os.architecture.return_value = 'x86_64'
        mock_system.Hardware.Cpu.architecture.return_value = 'x86_64'
        mock_system.Hardware.Cpu.logical_core_count.return_value = 4
        mock_system.Hardware.Cpu.physical_core_count.return_value = 2
        mock_system.Hardware.Cpu.brand.return_value = 'Intel Core i5'
        mock_system.Hardware.Disk.total.return_value = 1000000000
        mock_system.Hardware.Disk.used.return_value = 500000000
        mock_system.Hardware.Disk.free.return_value = 500000000
        mock_system.Hardware.monitors.return_value = []
        mock_system.Hardware.screens.return_value = []
        mock_system.Hardware.usb_devices.return_value = []
        mock_system.Hardware.printers.return_value = []
        mock_system.Hardware.system_definitions.return_value = {}
        mock_system.Hardware.machine_model.return_value = 'Test Model'
        mock_system.Hardware.Memory.total.return_value = 8000000000
        mock_system.Sessions.user_name.return_value = ['user1']
        mock_system.BIOS.release_date.return_value = (0, '01/01/2020\n')
        mock_system.BIOS.version.return_value = (0, '1.0\n')
        mock_system.BIOS.vendor.return_value = (0, 'Test Vendor\n')
        mock_system.Hardware.BaseBoard.manufacturer.return_value = (0, 'Test Manufacturer\n')
        mock_system.Hardware.BaseBoard.version.return_value = (0, '1.0\n')
        mock_system.Hardware.BaseBoard.asset_tag.return_value = (0, 'TAG123\n')
        mock_system.Hardware.BaseBoard.product_name.return_value = (0, 'Test Product\n')
        mock_system.Hardware.BaseBoard.serial_number.return_value = (0, 'SN123456\n')
        
        # Fix: DiskInfo.get_all_disks() should return a tuple of two lists
        mock_disk_info = MagicMock()
        mock_disk_info.get_all_disks.return_value = ([], [])
        
        # Mock Util.get_agent_version as a static method
        mock_util = MagicMock()
        mock_util.get_agent_version.return_value = '1.0.0'
        
        # Patch System, DiskInfo, and Util in the registration module
        with patch('base.registration.registration.System', mock_system):
            with patch('base.registration.registration.DiskInfo', mock_disk_info):
                with patch('base.registration.registration.Util', mock_util):
                    result = registration.get_registration_params()
        
        # Should return JSON string
        assert isinstance(result, str)
        params = json.loads(result)
        
        # Verify some key parameters
        assert 'hostname' in params
        assert 'os.name' in params
        assert 'agentVersion' in params
        assert params['agentVersion'] == '1.0.0'
    
    def test_update_registration_attrs(self, mock_scope):
        """Test update_registration_attrs method"""
        mock_db = MagicMock()
        mock_db.select_one_result.side_effect = ['test_jid', 'test_password']
        mock_conf = MagicMock()
        mock_conf.has_section.return_value = True
        mock_logger = MagicMock()
        
        registration = Registration.__new__(Registration)
        registration.db_service = mock_db
        registration.conf_manager = mock_conf
        registration.logger = mock_logger
        registration.host = 'test-host'
        registration.servicename = 'test-service'
        
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            registration.update_registration_attrs('cn=test,dc=example,dc=com')
            
            # Verify database update
            mock_db.update.assert_called_once_with('registration', ['dn', 'registered'], 
                                                   ['cn=test,dc=example,dc=com', 1], ' registered = 0')
            
            # Verify config updates
            mock_conf.set.assert_any_call('CONNECTION', 'uid', 'test_jid')
            mock_conf.set.assert_any_call('CONNECTION', 'password', 'test_password')
            mock_conf.set.assert_any_call('CONNECTION', 'host', 'test-host')
            mock_conf.set.assert_any_call('CONNECTION', 'servicename', 'test-service')
            
            # Verify file write
            mock_conf.write.assert_called_once()
            mock_logger.debug.assert_called_with('Registration configuration file is updated')
    
    def test_ldap_registration_request(self, mock_scope):
        """Test ldap_registration_request method"""
        mock_messenger = MagicMock()
        mock_message_manager = MagicMock()
        mock_message_manager.ldap_registration_msg.return_value = 'test_message'
        mock_logger = MagicMock()
        
        registration = Registration.__new__(Registration)
        registration.messenger = mock_messenger
        registration.message_manager = mock_message_manager
        registration.logger = mock_logger
        
        registration.ldap_registration_request()
        
        mock_message_manager.ldap_registration_msg.assert_called_once()
        mock_messenger.send_Direct_message.assert_called_once_with('test_message')
        mock_logger.info.assert_called_with('Requesting LDAP registration')
    
    def test_registration_error(self, mock_scope):
        """Test registration_error method"""
        mock_logger = MagicMock()
        registration = Registration.__new__(Registration)
        registration.logger = mock_logger
        
        with patch.object(Registration, 're_register') as mock_re_register:
            registration.registration_error({'error': 'test'})
            
            mock_re_register.assert_called_once()
    
    @patch('base.registration.registration.os')
    @patch('base.registration.registration.Util')
    @patch('base.registration.registration.System')
    def test_registration_timeout(self, mock_system_class, mock_util_class, mock_os_module, mock_scope):
        """Test registration_timeout method"""
        mock_os_module.getlogin.return_value = 'testuser'
        
        # Setup System mocks
        mock_ahenk = MagicMock()
        mock_ahenk.get_pid_number.return_value = '12345'
        mock_process = MagicMock()
        mock_process.kill_by_pid = MagicMock()
        mock_system = MagicMock()
        mock_system.Ahenk = mock_ahenk
        mock_system.Process = mock_process
        mock_system_class.System = mock_system
        
        # Mock Util.show_message as a static method - patch it directly
        with patch('base.registration.registration.Util.show_message') as mock_show_message:
            with patch('base.registration.registration.System', mock_system):
                mock_logger = MagicMock()
                registration = Registration.__new__(Registration)
                registration.logger = mock_logger
                
                registration.registration_timeout()
                
                # Verify error logging
                error_calls = [str(call) for call in mock_logger.error.call_args_list]
                assert any('Could not reach registration response' in str(call) for call in error_calls)
                assert any('Ahenk is shutting down' in str(call) for call in error_calls)
                
                # Verify show_message was called
                mock_show_message.assert_called_once_with('testuser', ':0', 
                                                          "Lider MYS sistemine ulaşılamadı. Lütfen sunucu adresini kontrol ediniz....", 
                                                          "HATA")
                
                # Verify kill process
                mock_process.kill_by_pid.assert_called_once_with(12345)
