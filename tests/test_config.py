"""
配置管理测试
"""

import pytest
import json
from pathlib import Path
from src.config.settings import Settings


@pytest.fixture
def settings():
    """创建 Settings 实例"""
    return Settings()


@pytest.fixture
def dynamic_config_path(tmp_path):
    """创建临时动态配置文件"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "dynamic_config.json"
    return config_file


class TestSettingsBasic:
    """测试基本配置读取"""

    def test_project_root_exists(self, settings):
        """测试项目根目录存在"""
        assert settings.PROJECT_ROOT.exists()

    def test_dirs_exist(self, settings):
        """测试必要目录存在"""
        assert settings.DATA_DIR.exists()
        assert settings.IMAGE_DIR.exists()
        assert settings.LOG_DIR.exists()

    def test_ai_config(self, settings):
        """测试 AI 配置"""
        assert settings.DEEPSEEK_API_KEY is not None
        assert settings.DEEPSEEK_BASE_URL == "https://api.deepseek.com"
        assert settings.DEEPSEEK_MODEL == "deepseek-chat"

    def test_email_config(self, settings):
        """测试邮件配置"""
        assert settings.QQ_EMAIL is not None
        assert settings.QQ_EMAIL_AUTH_CODE is not None
        assert settings.RECEIVER_EMAIL is not None
        assert settings.SMTP_SERVER == "smtp.qq.com"
        assert settings.SMTP_PORT == 465

    def test_default_star_stocks(self, settings):
        """测试默认明星股配置"""
        assert len(settings.A_SHARE_STAR_STOCKS) > 0
        assert len(settings.HK_STAR_STOCKS) > 0
        assert len(settings.US_STAR_STOCKS) > 0

        # 验证格式
        for stock in settings.A_SHARE_STAR_STOCKS:
            assert "code" in stock
            assert "name" in stock

    def test_default_thresholds(self, settings):
        """测试默认阈值配置"""
        assert settings.HOT_STOCK_THRESHOLD == 3.0
        assert settings.LIMIT_UP_DOWN_THRESHOLD == 9.9


class TestDynamicConfigLoading:
    """测试动态配置加载"""

    def test_load_dynamic_config_from_file(self, settings, tmp_path):
        """测试从文件加载动态配置"""
        # 创建临时配置目录
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "dynamic_config.json"

        # 写入测试配置
        test_config = {
            "star_stocks": {
                "A股": [{"code": "000001", "name": "平安银行"}],
                "港股": [{"code": "00001", "name": "长和"}],
                "美股": [{"code": "TEST", "name": "测试股票"}],
            },
            "thresholds": {"hot_stock_threshold": 5.0, "limit_up_down_threshold": 10.0},
            "scheduler": {
                "us_stock_time": "10:00",
                "a_share_time": "18:00",
                "hot_stock_time": "18:30",
                "ipo_time": "21:00",
            },
        }

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)

        # 模拟加载
        settings.PROJECT_ROOT = tmp_path
        settings.load_dynamic_config()

        # 验证配置已更新
        assert settings.A_SHARE_STAR_STOCKS == [{"code": "000001", "name": "平安银行"}]
        assert settings.HK_STAR_STOCKS == [{"code": "00001", "name": "长和"}]
        assert settings.US_STAR_STOCKS == [{"code": "TEST", "name": "测试股票"}]
        assert settings.HOT_STOCK_THRESHOLD == 5.0
        assert settings.LIMIT_UP_DOWN_THRESHOLD == 10.0
        assert settings.US_STOCK_TIME == "10:00"
        assert settings.A_SHARE_TIME == "18:00"
        assert settings.HOT_STOCK_TIME == "18:30"
        assert settings.IPO_TIME == "21:00"

    def test_load_dynamic_config_missing_file(self, settings, tmp_path):
        """测试加载不存在的配置文件"""
        settings.PROJECT_ROOT = tmp_path
        # 应该不会报错，使用默认配置
        settings.load_dynamic_config()

        # 验证默认配置仍然存在
        assert len(settings.A_SHARE_STAR_STOCKS) > 0
        assert settings.HOT_STOCK_THRESHOLD == 3.0

    def test_load_dynamic_config_partial_update(self, settings, tmp_path):
        """测试部分更新动态配置"""
        # 只更新阈值，不更新明星股
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "dynamic_config.json"

        test_config = {"thresholds": {"hot_stock_threshold": 7.0}}

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)

        settings.PROJECT_ROOT = tmp_path
        settings.load_dynamic_config()

        # 验证阈值已更新，但明星股仍然是默认值
        assert settings.HOT_STOCK_THRESHOLD == 7.0
        assert len(settings.A_SHARE_STAR_STOCKS) > 0


class TestConfigValidation:
    """测试配置验证"""

    def test_star_stock_format(self, settings):
        """测试明星股格式"""
        for stock in settings.A_SHARE_STAR_STOCKS:
            assert isinstance(stock, dict)
            assert "code" in stock
            assert "name" in stock
            assert isinstance(stock["code"], str)
            assert isinstance(stock["name"], str)

    def test_threshold_types(self, settings):
        """测试阈值类型"""
        assert isinstance(settings.HOT_STOCK_THRESHOLD, (int, float))
        assert isinstance(settings.LIMIT_UP_DOWN_THRESHOLD, (int, float))

    def test_time_format(self, settings):
        """测试时间格式"""
        # 默认时间应该符合 HH:MM 格式
        import re

        time_pattern = r"^\d{2}:\d{2}$"
        assert re.match(time_pattern, settings.US_STOCK_TIME)
        assert re.match(time_pattern, settings.A_SHARE_TIME)
        assert re.match(time_pattern, settings.HOT_STOCK_TIME)
        assert re.match(time_pattern, settings.IPO_TIME)


class TestConfigIntegration:
    """测试配置集成"""

    def test_settings_singleton(self):
        """测试 settings 是单例"""
        from src.config.settings import settings as settings1
        from src.config.settings import settings as settings2

        assert settings1 is settings2

    def test_config_reload(self, settings, tmp_path):
        """测试配置重新加载"""
        # 创建初始配置
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "dynamic_config.json"

        initial_config = {"thresholds": {"hot_stock_threshold": 5.0}}

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(initial_config, f, ensure_ascii=False, indent=2)

        settings.PROJECT_ROOT = tmp_path
        settings.load_dynamic_config()
        assert settings.HOT_STOCK_THRESHOLD == 5.0

        # 更新配置
        updated_config = {"thresholds": {"hot_stock_threshold": 8.0}}

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(updated_config, f, ensure_ascii=False, indent=2)

        # 重新加载
        settings.load_dynamic_config()
        assert settings.HOT_STOCK_THRESHOLD == 8.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
