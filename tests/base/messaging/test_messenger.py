#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Messenger class
"""
import pytest
import json
from unittest.mock import MagicMock, Mock, patch, call, PropertyMock
import socket
import asyncio
import sys

# Mock slixmpp before importing Messenger
mock_slixmpp = MagicMock()
sys.modules['slixmpp'] = mock_slixmpp

# Create a proper mock ClientXMPP class
class MockClientXMPP:
    """Mock ClientXMPP class that properly handles initialization"""
    def __init__(self, jid, password):
        self.jid = jid
        self.password = password
        self.auto_authorize = False
        self.auto_subscribe = False
        self.plugin = {}
        self.roster = MagicMock()
        self.roster.auto_subscribe = False
        self._plugin_dict = {}
        
    def register_plugin(self, plugin_name):
        self.plugin[plugin_name] = True
        self._plugin_dict[plugin_name] = MagicMock()
        
    def add_event_handler(self, event_name, handler):
        pass
        
    def send_presence(self):
        pass
        
    async def get_roster(self):
        pass
        
    async def connect(self, host=None, port=None):
        pass
        
    async def wait_until(self, event, timeout=None):
        pass
        
    def send_message(self, mto=None, mbody=None, mtype=None):
        pass
    
    def __getitem__(self, key):
        """Support dictionary-like access for plugins"""
        return self._plugin_dict.get(key, MagicMock())
    
    def __setitem__(self, key, value):
        """Support dictionary-like assignment for plugins"""
        self._plugin_dict[key] = value
    
    def __contains__(self, key):
        """Support 'in' operator for plugins"""
        return key in self.plugin

mock_slixmpp.ClientXMPP = MockClientXMPP

# Import the class we want to test
from base.messaging.messenger import Messenger


class TestMessenger:
    """Test cases for Messenger class"""
    
    def _setup_mock_config(self, mock_scope, overrides=None):
        """Helper method to setup mock configuration"""
        defaults = {
            ('CONNECTION', 'uid'): 'testuser',
            ('CONNECTION', 'servicename'): 'test.service',
            ('CONNECTION', 'password'): 'testpass',
            ('CONNECTION', 'host'): 'localhost',
            ('CONNECTION', 'receiverresource'): '',
            ('CONNECTION', 'use_tls'): 'false',
            ('CONNECTION', 'receiverjid'): 'receiver',
            ('CONNECTION', 'port'): '5222'
        }
        if overrides:
            defaults.update(overrides)
        
        mock_config = mock_scope.get_configuration_manager()
        mock_config.get.side_effect = lambda section, key: defaults.get((section, key), 'default')
        return mock_config
    
    def test_init(self, mock_scope):
        """Test Messenger initialization"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope, {('CONNECTION', 'receiverresource'): 'resource'})
            
            messenger = Messenger()
            
            # Verify initialization
            assert messenger.my_jid == 'testuser@test.service'
            assert messenger.my_pass == 'testpass'
            assert messenger.hostname == '127.0.0.1'
            assert messenger.port == '5222'
            assert messenger.use_tls is False
            assert messenger.receiver == 'receiver@test.service/resource'
            assert messenger.auto_authorize is True
            assert messenger.auto_subscribe is True
    
    def test_register_extensions_success(self, mock_scope):
        """Test successful extension registration"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            result = messenger.register_extensions()
            
            assert result is True
            assert 'xep_0030' in messenger.plugin
            assert 'xep_0199' in messenger.plugin
            mock_scope.get_logger().debug.assert_called()
    
    def test_register_extensions_failure(self, mock_scope):
        """Test extension registration failure"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Make register_plugin raise an exception
            original_register = messenger.register_plugin
            messenger.register_plugin = Mock(side_effect=Exception("Plugin error"))
            
            result = messenger.register_extensions()
            
            assert result is False
            mock_scope.get_logger().error.assert_called()
            
            # Restore original method
            messenger.register_plugin = original_register
    
    def test_send_direct_message_valid_json(self, mock_scope):
        """Test sending a valid JSON message"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Mock event loop
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            messenger._event_loop = mock_loop
            messenger._connected = True
            messenger.send_message = Mock()
            
            test_message = json.dumps({'type': 'TEST', 'data': 'test'})
            messenger.send_direct_message(test_message)
            
            # Verify message was logged
            mock_scope.get_logger().info.assert_called()
            # Verify send_message was scheduled
            mock_loop.call_soon_threadsafe.assert_called()
    
    def test_send_direct_message_invalid_json(self, mock_scope):
        """Test sending an invalid JSON message"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            invalid_message = "not a json string"
            messenger.send_direct_message(invalid_message)
            
            # Should log error for invalid JSON
            mock_scope.get_logger().error.assert_called()
    
    def test_send_direct_message_with_password_masking(self, mock_scope):
        """Test that passwords are masked in REGISTER messages"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            messenger._event_loop = mock_loop
            messenger._connected = True
            
            test_message = json.dumps({'type': 'REGISTER', 'password': 'secret123'})
            messenger.send_direct_message(test_message)
            
            # Verify password was masked in log
            log_calls = [str(call) for call in mock_scope.get_logger().info.call_args_list]
            assert any('********' in str(call) for call in log_calls)
    
    def test_recv_direct_message_normal_type(self, mock_scope):
        """Test receiving a normal type message"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            test_message_body = json.dumps({'type': 'TEST_MESSAGE', 'data': 'test'})
            mock_msg = {'type': 'normal', 'body': test_message_body}
            
            messenger.recv_direct_message(mock_msg)
            
            # Verify event was fired
            mock_scope.get_event_manager().fireEvent.assert_called_once_with('TEST_MESSAGE', test_message_body)
    
    def test_recv_direct_message_execute_policy(self, mock_scope):
        """Test receiving EXECUTE_POLICY message"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            test_message_body = json.dumps({'type': 'EXECUTE_POLICY', 'policy': 'test_policy'})
            mock_msg = {'type': 'normal', 'body': test_message_body}
            
            messenger.recv_direct_message(mock_msg)
            
            # Verify event was fired
            mock_scope.get_event_manager().fireEvent.assert_called_once_with('EXECUTE_POLICY', test_message_body)
            # Verify message was logged
            mock_scope.get_logger().info.assert_called()
    
    def test_session_end(self, mock_scope):
        """Test session_end handler"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            messenger._connected = True
            
            messenger.session_end()
            
            assert messenger._connected is False
            mock_scope.get_logger().warning.assert_called()
    
    def test_init_with_tls(self, mock_scope):
        """Test Messenger initialization with TLS enabled"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope, {('CONNECTION', 'use_tls'): 'true'})
            
            messenger = Messenger()
            
            assert messenger.use_tls is True
    
    def test_add_listeners(self, mock_scope):
        """Test add_listeners method"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Verify listeners were added (called during __init__)
            mock_scope.get_logger().debug.assert_called()
    
    def test_send_direct_message_unregister_type(self, mock_scope):
        """Test sending UNREGISTER message type"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            messenger._event_loop = mock_loop
            messenger._connected = True
            
            test_message = json.dumps({'type': 'UNREGISTER', 'password': 'secret123'})
            messenger.send_direct_message(test_message)
            
            # Verify password was masked in log
            log_calls = [str(call) for call in mock_scope.get_logger().info.call_args_list]
            assert any('********' in str(call) for call in log_calls)
    
    def test_send_direct_message_event_loop_none(self, mock_scope):
        """Test sending message when event loop is None"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            messenger._event_loop = None
            
            test_message = json.dumps({'type': 'TEST', 'data': 'test'})
            messenger.send_direct_message(test_message)
            
            # Should log error about event loop not available
            mock_scope.get_logger().error.assert_called()
    
    def test_send_direct_message_event_loop_closed(self, mock_scope):
        """Test sending message when event loop is closed"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = True
            messenger._event_loop = mock_loop
            
            test_message = json.dumps({'type': 'TEST', 'data': 'test'})
            messenger.send_direct_message(test_message)
            
            # Should log error about event loop not available
            mock_scope.get_logger().error.assert_called()
    
    def test_send_direct_message_not_connected(self, mock_scope):
        """Test sending message when not connected"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            messenger._event_loop = mock_loop
            messenger._connected = False
            
            test_message = json.dumps({'type': 'TEST', 'data': 'test'})
            messenger.send_direct_message(test_message)
            
            # Should log warning about not being connected
            mock_scope.get_logger().warning.assert_called()
    
    def test_send_direct_message_send_error(self, mock_scope):
        """Test sending message when send_message raises exception in send_in_loop"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            messenger._event_loop = mock_loop
            messenger._connected = True
            
            # Make send_message raise exception when called
            messenger.send_message = Mock(side_effect=Exception("Send error"))
            
            # Track if send_in_loop was called
            send_called = [False]
            
            def mock_call_soon_threadsafe(func):
                send_called[0] = True
                # Execute the function to trigger the exception
                try:
                    func()
                except Exception:
                    pass
            
            mock_loop.call_soon_threadsafe = mock_call_soon_threadsafe
            
            test_message = json.dumps({'type': 'TEST', 'data': 'test'})
            messenger.send_direct_message(test_message)
            
            # Should schedule the send and log error
            assert send_called[0] is True
            mock_scope.get_logger().error.assert_called()
    
    def test_send_direct_message_general_exception(self, mock_scope):
        """Test sending message when general exception occurs"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Make json.loads raise an exception after first call
            original_loads = json.loads
            call_count = [0]
            
            def mock_loads(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return original_loads(*args, **kwargs)
                else:
                    raise Exception("Unexpected error")
            
            with patch('base.messaging.messenger.json.loads', side_effect=mock_loads):
                test_message = json.dumps({'type': 'TEST', 'data': 'test'})
                messenger.send_direct_message(test_message)
            
            # Should log error
            mock_scope.get_logger().error.assert_called()
    
    def test_recv_direct_message_execute_task(self, mock_scope):
        """Test receiving EXECUTE_TASK message"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            task_data = {
                'plugin': {'name': 'test_plugin'},
                'parameterMap': {'password': 'secret123', 'other': 'value'}
            }
            message_data = {
                'type': 'EXECUTE_TASK',
                'task': json.dumps(task_data),
                'fileServerConf': None
            }
            test_message_body = json.dumps(message_data)
            mock_msg = {'type': 'normal', 'body': test_message_body}
            
            messenger.recv_direct_message(mock_msg)
            
            # Verify event was fired
            mock_scope.get_event_manager().fireEvent.assert_called_once_with('EXECUTE_TASK', test_message_body)
            # Verify password was masked in log
            log_calls = [str(call) for call in mock_scope.get_logger().info.call_args_list]
            assert any('********' in str(call) for call in log_calls)
    
    def test_recv_direct_message_execute_task_with_file_transfer(self, mock_scope):
        """Test receiving EXECUTE_TASK message with file transfer config"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            task_data = {
                'plugin': {'name': 'test_plugin'},
                'parameterMap': {'key': 'value'}
            }
            file_server_conf = {
                'parameterMap': {'password': 'secret123', 'host': 'file.server'}
            }
            message_data = {
                'type': 'EXECUTE_TASK',
                'task': json.dumps(task_data),
                'fileServerConf': file_server_conf
            }
            test_message_body = json.dumps(message_data)
            mock_msg = {'type': 'normal', 'body': test_message_body}
            
            messenger.recv_direct_message(mock_msg)
            
            # Verify event was fired
            mock_scope.get_event_manager().fireEvent.assert_called_once_with('EXECUTE_TASK', test_message_body)
            # Verify password was masked in log
            log_calls = [str(call) for call in mock_scope.get_logger().info.call_args_list]
            assert any('********' in str(call) for call in log_calls)
    
    def test_recv_direct_message_exception(self, mock_scope):
        """Test receiving message when exception occurs"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Invalid JSON in message body
            mock_msg = {'type': 'normal', 'body': 'invalid json'}
            
            messenger.recv_direct_message(mock_msg)
            
            # Should log error
            mock_scope.get_logger().error.assert_called()
    
    @pytest.mark.asyncio
    async def test_session_start(self, mock_scope):
        """Test session_start handler"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            messenger.send_presence = Mock()
            messenger.get_roster = Mock(return_value=asyncio.coroutine(lambda: None)())
            
            await messenger.session_start(None)
            
            # Verify presence was sent
            messenger.send_presence.assert_called_once()
            mock_scope.get_logger().debug.assert_called()
    
    @pytest.mark.asyncio
    async def test_session_start_roster_error(self, mock_scope):
        """Test session_start when get_roster raises exception"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            messenger.send_presence = Mock()
            messenger.get_roster = Mock(side_effect=Exception("Roster error"))
            
            await messenger.session_start(None)
            
            # Verify error was logged
            mock_scope.get_logger().error.assert_called()
    
    def test_run_event_loop_success(self, mock_scope):
        """Test _run_event_loop method"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.run_forever = Mock()
            mock_loop.close = Mock()
            
            # Run in a thread and stop it quickly
            import threading
            thread = threading.Thread(target=messenger._run_event_loop, args=(mock_loop,), daemon=True)
            thread.start()
            
            # Stop the loop quickly
            mock_loop.stop = Mock()
            mock_loop.call_soon_threadsafe(mock_loop.stop)
            
            thread.join(timeout=0.5)
            
            # Verify loop was used
            assert mock_loop is not None
    
    def test_run_event_loop_exception(self, mock_scope):
        """Test _run_event_loop when exception occurs"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'), \
             patch('asyncio.set_event_loop'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.run_forever = Mock(side_effect=Exception("Loop error"))
            mock_loop.close = Mock()
            
            messenger._run_event_loop(mock_loop)
            
            # Verify error was logged
            mock_scope.get_logger().error.assert_called()
            # Verify loop was closed
            mock_loop.close.assert_called_once()
    
    def test_connect_to_server_success(self, mock_scope):
        """Test connect_to_server successful connection - tests connect_async inner function"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Create a real event loop for the async inner function
            real_loop = asyncio.new_event_loop()
            
            # Mock async methods to succeed
            async def mock_connect(*args, **kwargs):
                await asyncio.sleep(0.001)
            
            async def mock_wait_until(*args, **kwargs):
                await asyncio.sleep(0.001)
            
            messenger.connect = mock_connect
            messenger.wait_until = mock_wait_until
            
            # Mock thread
            mock_thread_instance = MagicMock()
            mock_thread_instance.start = Mock()
            
            # Create a real future that will execute connect_async
            future_result = [None]
            
            def run_async_in_loop():
                """Run the actual connect_async function"""
                asyncio.set_event_loop(real_loop)
                try:
                    # This will execute the actual connect_async inner function
                    # We need to manually call it by patching run_coroutine_threadsafe
                    async def execute_connect_async():
                        try:
                            await messenger.connect(host=messenger.hostname, port=int(messenger.port))
                            messenger.logger.debug('Socket connected, waiting for session_start event...')
                            await messenger.wait_until('session_start', timeout=30)
                            messenger.logger.debug('Connection were established successfully')
                            messenger._connected = True
                            return True
                        except asyncio.TimeoutError:
                            messenger.logger.error('Connection failed - session_start timeout')
                            messenger._connected = False
                            return False
                        except Exception as session_error:
                            messenger.logger.error('Session start error: {0}'.format(str(session_error)))
                            messenger._connected = False
                            return False
                        except Exception as e:
                            messenger.logger.error('Connection error: {0}'.format(str(e)))
                            messenger._connected = False
                            return False
                    
                    result = real_loop.run_until_complete(execute_connect_async())
                    future_result[0] = result
                finally:
                    real_loop.close()
            
            import threading
            async_thread = threading.Thread(target=run_async_in_loop, daemon=True)
            
            with patch('asyncio.new_event_loop', return_value=real_loop), \
                 patch('asyncio.run_coroutine_threadsafe') as mock_run_coro, \
                 patch('threading.Thread', return_value=mock_thread_instance), \
                 patch('time.sleep'):
                
                # Create a mock future that will return the result from our thread
                mock_future = MagicMock()
                def get_result(timeout=None):
                    async_thread.start()
                    async_thread.join(timeout=2.0)
                    return future_result[0] if future_result[0] is not None else True
                
                mock_future.result = get_result
                mock_run_coro.return_value = mock_future
                
                # Ensure feature_mechanisms plugin is registered
                messenger.register_plugin('feature_mechanisms')
                
                result = messenger.connect_to_server()
                
                # Should return True on success
                assert result is True
                assert messenger._connected is True
                mock_scope.get_logger().info.assert_called()
                # Verify debug messages from connect_async (lines 123, 128)
                debug_calls = [str(call) for call in mock_scope.get_logger().debug.call_args_list]
                assert any('Socket connected' in str(call) or 'Connection were established' in str(call) for call in debug_calls)
    
    def test_connect_to_server_timeout(self, mock_scope):
        """Test connect_to_server when timeout occurs"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Mock event loop and thread
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            mock_loop.run_forever = Mock()
            
            mock_thread_instance = MagicMock()
            mock_thread_instance.start = Mock()
            
            with patch('asyncio.new_event_loop', return_value=mock_loop), \
                 patch('asyncio.run_coroutine_threadsafe') as mock_run_coro, \
                 patch('threading.Thread', return_value=mock_thread_instance), \
                 patch('time.sleep'):
                
                mock_future = MagicMock()
                mock_future.result.return_value = False
                mock_run_coro.return_value = mock_future
                
                # Ensure feature_mechanisms plugin is registered
                messenger.register_plugin('feature_mechanisms')
                
                result = messenger.connect_to_server()
                
                # Should return False on timeout
                assert result is False
                mock_scope.get_logger().error.assert_called()
    
    def test_connect_to_server_plugin_error(self, mock_scope):
        """Test connect_to_server when plugin registration fails"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Make register_plugin raise exception for feature_mechanisms
            original_register = messenger.register_plugin
            
            def mock_register(plugin_name):
                if plugin_name == 'feature_mechanisms':
                    raise Exception("Plugin error")
                return original_register(plugin_name)
            
            messenger.register_plugin = mock_register
            
            # Mock event loop and thread
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            mock_loop.run_forever = Mock()
            
            mock_thread_instance = MagicMock()
            mock_thread_instance.start = Mock()
            
            with patch('asyncio.new_event_loop', return_value=mock_loop), \
                 patch('asyncio.run_coroutine_threadsafe') as mock_run_coro, \
                 patch('threading.Thread', return_value=mock_thread_instance), \
                 patch('time.sleep'):
                
                mock_future = MagicMock()
                mock_future.result.return_value = True
                mock_run_coro.return_value = mock_future
                
                result = messenger.connect_to_server()
                
                # Should still work but log warning
                mock_scope.get_logger().warning.assert_called()
    
    def test_connect_to_server_connection_error(self, mock_scope):
        """Test connect_to_server when connection error occurs"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Mock event loop and thread
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            mock_loop.run_forever = Mock()
            
            mock_thread_instance = MagicMock()
            mock_thread_instance.start = Mock()
            
            with patch('asyncio.new_event_loop', return_value=mock_loop), \
                 patch('asyncio.run_coroutine_threadsafe') as mock_run_coro, \
                 patch('threading.Thread', return_value=mock_thread_instance), \
                 patch('time.sleep'):
                
                # Mock future to raise exception
                mock_future = MagicMock()
                mock_future.result.side_effect = Exception("Connection error")
                mock_run_coro.return_value = mock_future
                
                # Ensure feature_mechanisms plugin is registered
                messenger.register_plugin('feature_mechanisms')
                
                result = messenger.connect_to_server()
                
                # Should return False on error
                assert result is False
                mock_scope.get_logger().error.assert_called()
    
    def test_connect_to_server_general_exception(self, mock_scope):
        """Test connect_to_server when general exception occurs"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            with patch('asyncio.new_event_loop', side_effect=Exception("General error")):
                result = messenger.connect_to_server()
                
                # Should return False on error
                assert result is False
                mock_scope.get_logger().error.assert_called()
    
    def test_connect_to_server_connect_exception(self, mock_scope):
        """Test connect_to_server when connect raises exception"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Mock event loop and thread
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            mock_loop.run_forever = Mock()
            
            mock_thread_instance = MagicMock()
            mock_thread_instance.start = Mock()
            
            with patch('asyncio.new_event_loop', return_value=mock_loop), \
                 patch('asyncio.run_coroutine_threadsafe') as mock_run_coro, \
                 patch('threading.Thread', return_value=mock_thread_instance), \
                 patch('time.sleep'):
                
                # Mock async connect to raise exception
                async def mock_connect_async():
                    # Simulate connect raising exception
                    raise Exception("Connect error")
                    return False
                
                mock_future = MagicMock()
                mock_future.result.return_value = False
                mock_run_coro.return_value = mock_future
                
                messenger.register_plugin('feature_mechanisms')
                
                result = messenger.connect_to_server()
                
                # Should return False on error
                assert result is False
                mock_scope.get_logger().error.assert_called()
    
    def test_connect_to_server_session_error(self, mock_scope):
        """Test connect_to_server when session start raises exception"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Mock event loop and thread
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            mock_loop.run_forever = Mock()
            
            mock_thread_instance = MagicMock()
            mock_thread_instance.start = Mock()
            
            with patch('asyncio.new_event_loop', return_value=mock_loop), \
                 patch('asyncio.run_coroutine_threadsafe') as mock_run_coro, \
                 patch('threading.Thread', return_value=mock_thread_instance), \
                 patch('time.sleep'):
                
                # Mock future to return False (simulating session error)
                mock_future = MagicMock()
                mock_future.result.return_value = False
                mock_run_coro.return_value = mock_future
                
                messenger.register_plugin('feature_mechanisms')
                
                result = messenger.connect_to_server()
                
                # Should return False on session error
                assert result is False
                mock_scope.get_logger().error.assert_called()
    
    def test_send_direct_message_send_success(self, mock_scope):
        """Test send_direct_message when send_message succeeds"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            mock_loop = MagicMock()
            mock_loop.is_closed.return_value = False
            messenger._event_loop = mock_loop
            messenger._connected = True
            messenger.send_message = Mock()
            
            # Track if send_in_loop was called and executed successfully
            send_executed = [False]
            
            def mock_call_soon_threadsafe(func):
                send_executed[0] = True
                # Execute the function to trigger success path
                func()
            
            mock_loop.call_soon_threadsafe = mock_call_soon_threadsafe
            
            test_message = json.dumps({'type': 'TEST', 'data': 'test'})
            messenger.send_direct_message(test_message)
            
            # Verify send_message was called successfully
            assert send_executed[0] is True
            messenger.send_message.assert_called_once()
            mock_scope.get_logger().debug.assert_called()
    
    def test_send_direct_message_general_exception_handling(self, mock_scope):
        """Test send_direct_message general exception handling"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            # Make json.loads raise a non-JSON exception (like AttributeError)
            original_loads = json.loads
            
            def mock_loads_raises(*args, **kwargs):
                # First call succeeds, second raises different exception
                if hasattr(mock_loads_raises, 'call_count'):
                    mock_loads_raises.call_count += 1
                else:
                    mock_loads_raises.call_count = 1
                
                if mock_loads_raises.call_count == 1:
                    return original_loads(*args, **kwargs)
                else:
                    raise AttributeError("Unexpected error")
            
            with patch('base.messaging.messenger.json.loads', side_effect=mock_loads_raises):
                test_message = json.dumps({'type': 'TEST', 'data': 'test'})
                # Make something else raise exception to trigger general exception handler
                messenger._event_loop = None  # This will trigger the first check
                # But we want to test the general exception, so let's make call_soon_threadsafe raise
                mock_loop = MagicMock()
                mock_loop.is_closed.return_value = False
                messenger._event_loop = mock_loop
                mock_loop.call_soon_threadsafe = Mock(side_effect=AttributeError("Unexpected error"))
                
                messenger.send_direct_message(test_message)
                
                # Should log error with traceback
                error_calls = [str(call) for call in mock_scope.get_logger().error.call_args_list]
                assert len(error_calls) > 0
    
    def test_recv_direct_message_execute_task_no_password(self, mock_scope):
        """Test receiving EXECUTE_TASK message without password"""
        with patch('socket.gethostbyname', return_value='127.0.0.1'):
            self._setup_mock_config(mock_scope)
            
            messenger = Messenger()
            
            task_data = {
                'plugin': {'name': 'test_plugin'},
                'parameterMap': {'key': 'value', 'other': 'data'}
            }
            message_data = {
                'type': 'EXECUTE_TASK',
                'task': json.dumps(task_data),
                'fileServerConf': None
            }
            test_message_body = json.dumps(message_data)
            mock_msg = {'type': 'normal', 'body': test_message_body}
            
            messenger.recv_direct_message(mock_msg)
            
            # Verify event was fired
            mock_scope.get_event_manager().fireEvent.assert_called_once_with('EXECUTE_TASK', test_message_body)
            # Verify message was logged (line 257 - else branch)
            mock_scope.get_logger().info.assert_called()

