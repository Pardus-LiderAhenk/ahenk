#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for ConfigManager class
"""
import pytest
import os
import tempfile
from unittest.mock import patch, mock_open
from configparser import ConfigParser

from base.config.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class"""
    
    def test_init_with_file_path(self):
        """Test ConfigManager initialization with file path"""
        config_manager = ConfigManager(configuration_file_path='/etc/ahenk/ahenk.conf')
        
        assert config_manager.configurationFilePath == '/etc/ahenk/ahenk.conf'
        assert config_manager.configurationFolderPath is None
    
    def test_init_with_folder_path(self):
        """Test ConfigManager initialization with folder path"""
        config_manager = ConfigManager(configuration_folder_path='/etc/ahenk/config.d/')
        
        assert config_manager.configurationFilePath is None
        assert config_manager.configurationFolderPath == '/etc/ahenk/config.d/'
    
    def test_init_with_both_paths(self):
        """Test ConfigManager initialization with both paths"""
        config_manager = ConfigManager(
            configuration_file_path='/etc/ahenk/ahenk.conf',
            configuration_folder_path='/etc/ahenk/config.d/'
        )
        
        assert config_manager.configurationFilePath == '/etc/ahenk/ahenk.conf'
        assert config_manager.configurationFolderPath == '/etc/ahenk/config.d/'
    
    def test_read_with_existing_file(self):
        """Test reading from existing configuration file"""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write('[SECTION1]\n')
            f.write('key1 = value1\n')
            f.write('key2 = value2\n')
            temp_file = f.name
        
        try:
            config_manager = ConfigManager(configuration_file_path=temp_file)
            parser = config_manager.read()
            
            assert isinstance(parser, ConfigParser)
            assert parser.get('SECTION1', 'key1') == 'value1'
            assert parser.get('SECTION1', 'key2') == 'value2'
        finally:
            os.unlink(temp_file)
    
    def test_read_with_nonexistent_file(self):
        """Test reading from non-existent file"""
        config_manager = ConfigManager(configuration_file_path='/nonexistent/file.conf')
        parser = config_manager.read()
        
        # Should return empty ConfigParser
        assert isinstance(parser, ConfigParser)
        assert len(parser.sections()) == 0
    
    def test_read_with_existing_folder(self):
        """Test reading from folder with config files"""
        # Create temporary directory with config files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first config file
            file1 = os.path.join(temp_dir, 'config1.conf')
            with open(file1, 'w') as f:
                f.write('[SECTION1]\n')
                f.write('key1 = value1\n')
            
            # Create second config file
            file2 = os.path.join(temp_dir, 'config2.conf')
            with open(file2, 'w') as f:
                f.write('[SECTION2]\n')
                f.write('key2 = value2\n')
            
            config_manager = ConfigManager(configuration_folder_path=temp_dir)
            parser = config_manager.read()
            
            assert isinstance(parser, ConfigParser)
            assert parser.get('SECTION1', 'key1') == 'value1'
            assert parser.get('SECTION2', 'key2') == 'value2'
    
    def test_read_with_nonexistent_folder(self):
        """Test reading from non-existent folder"""
        config_manager = ConfigManager(configuration_folder_path='/nonexistent/folder/')
        parser = config_manager.read()
        
        # Should return empty ConfigParser
        assert isinstance(parser, ConfigParser)
        assert len(parser.sections()) == 0

