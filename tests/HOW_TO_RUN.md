# Testleri Nasıl Çalıştırılır?

## 📊 Mevcut Durum

- **Toplam Test**: 41 test
- **Başarı Oranı**: %100 (41/41 test başarılı)
- **Genel Coverage**: %6 (245/4130 satır)
- **Test Edilen Modüller**: 
  - ConfigManager: %100 coverage (7 test)
  - Messenger: %89 coverage (34 test)

## Hızlı Başlangıç

### 1. Test Bağımlılıklarını Yükle

```bash
cd /home/agah/Masaüstü/DEVELOPMENT/Ahenk/ahenk
pip3 install -r requirements-test.txt
```

### 2. Testleri Çalıştır

#### Tüm testleri çalıştır:
```bash
pytest
```

#### Verbose mod (detaylı çıktı):
```bash
pytest -v
```

#### Sadece ConfigManager testleri:
```bash
pytest tests/base/config/ -v
```

#### Sadece Messenger testleri:
```bash
pytest tests/base/messaging/ -v
```

#### Belirli bir test dosyası:
```bash
pytest tests/base/config/test_config_manager.py -v
pytest tests/base/messaging/test_messenger.py -v
```

#### Belirli bir test fonksiyonu:
```bash
pytest tests/base/config/test_config_manager.py::TestConfigManager::test_init_with_file_path -v
```

## Test Komutları

### Temel Komutlar

```bash
# Verbose mod (detaylı çıktı)
pytest -v

# Sadece başarısız testleri göster
pytest --tb=short

# Coverage raporu ile (HTML)
pytest --cov=src --cov-report=html

# Coverage raporunu terminalde göster (eksik satırları göster)
pytest --cov=src --cov-report=term-missing

# Hızlı coverage özeti
pytest --cov=src --cov-report=term

# Sadece belirli marker ile işaretlenmiş testler
pytest -m unit

# Test çıktısını bir dosyaya kaydet
pytest -v > test_results.txt
```

### Coverage Komutları (Hızlı Erişim)

#### 🎯 En Çok Kullanılan Coverage Komutları

```bash
# 1. Hızlı coverage özeti (terminalde)
pytest --cov=src --cov-report=term

# 2. Detaylı coverage (hangi satırlar test edilmemiş gösterir)
pytest --cov=src --cov-report=term-missing

# 3. HTML raporu oluştur (tarayıcıda görüntülemek için)
pytest --cov=src --cov-report=html

# 4. JSON raporu oluştur (programatik kullanım için)
pytest --cov=src --cov-report=json

# 5. XML raporu oluştur (CI/CD için)
pytest --cov=src --cov-report=xml

# 6. Sadece coverage göster (test detayları olmadan)
pytest --cov=src --cov-report=term -q

# 7. Belirli bir modül için coverage
pytest tests/base/config/ --cov=src/base/config --cov-report=term-missing

# 8. Coverage minimum eşik kontrolü (örn: %50 altında hata ver)
pytest --cov=src --cov-report=term --cov-fail-under=50
```

#### 📊 Coverage Raporlarını Görüntüleme

```bash
# HTML raporu oluştur ve aç
pytest --cov=src --cov-report=html
xdg-open htmlcov/index.html
# veya
firefox htmlcov/index.html
# veya
google-chrome htmlcov/index.html

# JSON raporundan coverage yüzdesini göster
python3 -c "import json; data = json.load(open('coverage.json')); print(f\"Coverage: {data['totals']['percent_covered']:.2f}%\")"

# XML raporundan coverage yüzdesini göster
python3 -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(f\"Coverage: {root.attrib['line-rate']}\")"
```

#### 🔍 Detaylı Coverage Analizi

```bash
# Tüm modüller için coverage (eksik satırları göster)
pytest --cov=src --cov-report=term-missing

# Sadece coverage özeti (hızlı bakış)
pytest --cov=src --cov-report=term -q

# Coverage + test sonuçları (verbose)
pytest --cov=src --cov-report=term-missing -v

# Belirli bir dosya için coverage
pytest tests/base/config/test_config_manager.py --cov=src/base/config/config_manager --cov-report=term-missing
```

#### 📈 Coverage Karşılaştırma

```bash
# Coverage'ı JSON'a kaydet
pytest --cov=src --cov-report=json

# Coverage'ı XML'e kaydet
pytest --cov=src --cov-report=xml

# Coverage'ı HTML'e kaydet
pytest --cov=src --cov-report=html
```

## Test Durumu

### ✅ Çalışan Testler

- **ConfigManager Testleri** (`tests/base/config/test_config_manager.py`)
  - 7 test - Hepsi başarılı ✅
  - Coverage: %100

- **Messenger Testleri** (`tests/base/messaging/test_messenger.py`)
  - 34 test - Hepsi başarılı ✅
  - Coverage: %89
  - Test kategorileri:
    - Initialization (2 test)
    - Extension management (2 test)
    - Message sending (8 test)
    - Message receiving (5 test)
    - Session management (3 test)
    - Connection management (8 test)
    - Event loop (2 test)
    - Error handling (4 test)

## Yeni Test Yazma

### Örnek Test Yapısı

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock, patch

from base.your_module import YourClass

class TestYourClass:
    def test_something(self, mock_scope):
        """Test açıklaması"""
        # Arrange
        # Act
        # Assert
        assert True
```

### Test Çalıştırma

Yeni test yazdıktan sonra:

```bash
# Sadece yeni test dosyanızı çalıştırın
pytest tests/your_path/test_your_module.py -v

# Tüm testlerle birlikte çalıştırın
pytest -v
```

## Sorun Giderme

### Import Hatası

Eğer `ModuleNotFoundError` alırsanız:

1. `src` dizininin Python path'inde olduğundan emin olun
2. `conftest.py` dosyasında path ayarını kontrol edin

### Mock Hatası

Eğer mock ile ilgili hata alırsanız:

1. `conftest.py` dosyasındaki fixture'ları kontrol edin
2. Test dosyanızda doğru fixture'ları kullandığınızdan emin olun

### Coverage Düşük

Coverage'ı artırmak için:

1. Test yazmadığınız modülleri tespit edin
2. Önemli fonksiyonlar için test yazın
3. Edge case'ler için test ekleyin

## CI/CD Entegrasyonu

Testleri CI/CD pipeline'ında çalıştırmak için:

```bash
# XML raporu oluştur (Jenkins, GitLab CI için)
pytest --junitxml=test-results.xml --cov=src --cov-report=xml

# JSON raporu oluştur
pytest --json-report --json-report-file=test-report.json
```

## 📈 Coverage Raporları

### Terminal Raporu
```bash
pytest --cov=src --cov-report=term-missing
```

### HTML Raporu
```bash
# HTML raporu oluştur
pytest --cov=src --cov-report=html

# HTML raporunu aç
xdg-open htmlcov/index.html
# veya
firefox htmlcov/index.html
```

### XML Raporu (CI/CD için)
```bash
pytest --cov=src --cov-report=xml
# Rapor: coverage.xml
```

## 📊 Coverage Durumu

### Test Edilen Modüller

| Modül | Satır | Coverage | Test Sayısı | Durum |
|-------|-------|----------|--------------|-------|
| ConfigManager | 20 | %100 | 7 | ✅ Mükemmel |
| Messenger | 187 | %89 | 34 | ⚠️ İyi |
| Scope | 77 | %75 | - | ⚠️ İyi (fixture) |

### Genel İstatistikler
- **Toplam Kod**: 4130 satır
- **Test Edilen**: 245 satır (%6)
- **Test Edilmeyen**: 3885 satır (%94)

## İpuçları

1. **Test yazarken**: Her test bağımsız olmalı
2. **Mock kullanın**: Dış bağımlılıkları mock'layın
3. **Açıklayıcı isimler**: Test isimleri ne test ettiğini açıkça belirtmeli
4. **AAA Pattern**: Arrange, Act, Assert
5. **Coverage hedefi**: %80+ code coverage

## 🎯 Sonraki Adımlar

### Öncelikli Modüller (Test Edilmeyen)
1. **ExecutionManager** (331 satır) - Yüksek öncelik
2. **PluginManager** (245 satır) - Yüksek öncelik
3. **Registration** (453 satır) - Yüksek öncelik
4. **TaskManager** (45 satır) - Orta öncelik

## Yardım

Daha fazla bilgi için:
- `tests/README.md` dosyasına bakın
- `tests/COVERAGE_REPORT.md` dosyasına bakın (detaylı coverage raporu)
- `pytest --help` komutunu çalıştırın
- Pytest dokümantasyonu: https://docs.pytest.org/

