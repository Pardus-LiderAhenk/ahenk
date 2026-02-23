# Ahenk Unit Tests

Bu dizin Ahenk projesi için unit testleri içerir.

## 📊 Mevcut Durum

- **Toplam Test**: 41 test
- **Başarı Oranı**: %100 (41/41 test başarılı)
- **Genel Coverage**: %6 (245/4130 satır)
- **Test Edilen Modüller**: 
  - ConfigManager: %100 coverage (7 test) ✅
  - Messenger: %89 coverage (34 test) ⚠️

## Kurulum

Test bağımlılıklarını yüklemek için:

```bash
pip install -r requirements-test.txt
```

## Test Çalıştırma

### Tüm testleri çalıştırma

```bash
pytest
```

### Belirli bir test dosyasını çalıştırma

```bash
pytest tests/base/messaging/test_messenger.py
pytest tests/base/config/test_config_manager.py
```

### Belirli bir test fonksiyonunu çalıştırma

```bash
pytest tests/base/messaging/test_messenger.py::TestMessenger::test_init
```

### Verbose mod (detaylı çıktı)

```bash
pytest -v
```

### Coverage raporu ile

```bash
pytest --cov=src --cov-report=html
```

HTML raporu `htmlcov/index.html` dosyasında oluşturulur.

## Test Yapısı

Test yapısı kaynak kod yapısını takip eder:

```
tests/
├── base/
│   ├── config/
│   │   └── test_config_manager.py    # 7 test - %100 coverage
│   └── messaging/
│       └── test_messenger.py         # 34 test - %89 coverage
├── conftest.py                       # Pytest fixtures ve konfigürasyon
├── README.md                         # Bu dosya
├── HOW_TO_RUN.md                     # Test çalıştırma rehberi
└── COVERAGE_REPORT.md                # Detaylı coverage raporu
```

## Test Yazma Rehberi

### 1. Test Dosyası İsimlendirme

Test dosyaları `test_` ile başlamalıdır:
- ✅ `test_messenger.py`
- ❌ `messenger_test.py`

### 2. Test Sınıfı İsimlendirme

Test sınıfları `Test` ile başlamalıdır:
```python
class TestMessenger:
    """Test cases for Messenger class"""
```

### 3. Test Fonksiyon İsimlendirme

Test fonksiyonları `test_` ile başlamalıdır:
```python
def test_init(self, mock_scope):
    """Test Messenger initialization"""
```

### 4. Mocking Kullanımı

`conftest.py` dosyasında tanımlı fixture'ları kullanın:

```python
def test_something(self, mock_scope, mock_logger):
    # Test kodunuz
```

### 5. Assertion'lar

Pytest'in assertion'larını kullanın:

```python
assert result == expected
assert mock_obj.method.called
assert mock_obj.method.call_count == 2
```

## Örnek Test

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock, patch

from base.messaging.messenger import Messenger

class TestMessenger:
    def test_init(self, mock_scope):
        """Test Messenger initialization"""
        with patch('base.messaging.messenger.ClientXMPP.__init__'):
            messenger = Messenger()
            assert messenger is not None
```

## Best Practices

1. **Her test bağımsız olmalı**: Testler birbirine bağımlı olmamalı
2. **Mock kullanın**: Dış bağımlılıkları mock'layın (database, network, file system)
3. **Açıklayıcı isimler**: Test isimleri ne test ettiğini açıkça belirtmeli
4. **AAA Pattern**: Arrange (Hazırla), Act (Çalıştır), Assert (Doğrula)
5. **Tek bir şeyi test edin**: Her test fonksiyonu tek bir senaryoyu test etmeli

## Coverage Hedefi

Hedefimiz %80+ code coverage'dır. Coverage raporunu kontrol etmek için:

```bash
pytest --cov=src --cov-report=term-missing
```

## CI/CD Entegrasyonu

Testler CI/CD pipeline'ında otomatik çalıştırılabilir:

```bash
pytest --cov=src --cov-report=xml --junitxml=test-results.xml
```

