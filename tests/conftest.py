#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for Ahenk tests
"""
import sys
import os
from unittest.mock import MagicMock, Mock

# Add src directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest


@pytest.fixture
def mock_scope():
    """Mock Scope instance for testing"""
    from base.scope import Scope
    
    scope = Scope()
    
    # Mock configuration manager
    mock_config = MagicMock()
    mock_config.get.return_value = 'test_value'
    scope.set_configuration_manager(mock_config)
    
    # Mock logger
    mock_logger = MagicMock()
    scope.set_logger(mock_logger)
    
    # Mock event manager
    mock_event_manager = MagicMock()
    scope.set_event_manager(mock_event_manager)
    
    # Mock execution manager
    mock_execution_manager = MagicMock()
    scope.set_execution_manager(mock_execution_manager)
    
    # Set as instance
    Scope.set_instance(scope)
    
    return scope


@pytest.fixture
def mock_config_manager():
    """Mock ConfigManager for testing"""
    mock_config = MagicMock()
    mock_config.get.return_value = 'test_value'
    return mock_config


@pytest.fixture
def mock_logger():
    """Mock Logger for testing"""
    mock_logger = MagicMock()
    return mock_logger


@pytest.fixture
def mock_event_manager():
    """Mock EventManager for testing"""
    mock_event_manager = MagicMock()
    return mock_event_manager

