"""
全面配置管理API模块
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from .auth import get_current_user
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger("config_api")

router = APIRouter(prefix="/api/config", tags=["配置管理"])

# 配置文件路径
CONFIG_DIR = settings.PROJECT_ROOT / "config"
HOLIDAYS_FILE = settings.DATA_DIR / "holidays.json"
ENV_FILE = settings.PROJECT_ROOT / ".env"
DYNAMIC_CONFIG_FILE = CONFIG_DIR / "dynamic_config.json"
PROJECT_CONFIG_FILE = CONFIG_DIR / "project_config.json"


class HolidayUpdate(BaseModel):
    year: int
    dates: list


class EnvConfig(BaseModel):
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: Optional[str] = None
    DEEPSEEK_MODEL: Optional[str] = None
    TUSHARE_TOKEN: Optional[str] = None
    QQ_EMAIL: Optional[str] = None
    QQ_EMAIL_AUTH_CODE: Optional[str] = None
    RECEIVER_EMAIL: Optional[str] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    LOG_LEVEL: Optional[str] = None
    LOG_ROTATION: Optional[str] = None
    LOG_RETENTION: Optional[str] = None
    BASE_URL: Optional[str] = None


class StarStock(BaseModel):
    code: str
    name: str


class ThresholdConfig(BaseModel):
    hot_stock_threshold: Optional[float] = None
    limit_up_down_threshold: Optional[float] = None


class SchedulerConfig(BaseModel):
    us_stock_time: Optional[str] = None
    a_share_time: Optional[str] = None
    hot_stock_time: Optional[str] = None
    ipo_time: Optional[str] = None


class DistributionConfig(BaseModel):
    wechat_app_id: Optional[str] = None
    wechat_app_secret: Optional[str] = None
    toutiao_access_token: Optional[str] = None
    wxpusher_app_token: Optional[str] = None


class ProjectConfig(BaseModel):
    project_name: Optional[str] = None
    project_name_en: Optional[str] = None
    project_version: Optional[str] = None
    project_description: Optional[str] = None
    project_logo: Optional[str] = None
    project_slogan: Optional[str] = None


class BatchConfigUpdate(BaseModel):
    configs: Dict[str, Any]


# ============================================================================
# 配置分类接口
# ============================================================================


@router.get("/categories")
async def get_config_categories(current_user: str = Depends(get_current_user)):
    """获取所有配置分类"""
    return {
        "categories": [
            {
                "id": "ai",
                "name": "AI配置",
                "icon": "Cpu",
                "description": "DeepSeek AI 配置",
            },
            {
                "id": "datasource",
                "name": "数据源配置",
                "icon": "DataLine",
                "description": "Tushare 数据源配置",
            },
            {
                "id": "email",
                "name": "邮件配置",
                "icon": "Message",
                "description": "QQ邮箱配置",
            },
            {
                "id": "app",
                "name": "应用配置",
                "icon": "Setting",
                "description": "应用基本配置",
            },
            {
                "id": "star_stocks",
                "name": "明星股配置",
                "icon": "Star",
                "description": "明星股列表配置",
            },
            {
                "id": "thresholds",
                "name": "业务阈值配置",
                "icon": "Odometer",
                "description": "涨跌幅阈值配置",
            },
            {
                "id": "scheduler",
                "name": "定时任务配置",
                "icon": "Timer",
                "description": "定时任务时间配置",
            },
            {
                "id": "project",
                "name": "项目信息配置",
                "icon": "InfoFilled",
                "description": "项目基本信息配置",
            },
            {
                "id": "holidays",
                "name": "节假日配置",
                "icon": "Calendar",
                "description": "节假日日期配置",
            },
            {
                "id": "distribution",
                "name": "分发平台配置",
                "icon": "Share",
                "description": "分发平台配置",
            },
        ]
    }


@router.get("/category/{category}")
async def get_category_config(
    category: str, current_user: str = Depends(get_current_user)
):
    """获取指定分类的配置"""
    try:
        if category == "ai":
            return _get_ai_config()
        elif category == "datasource":
            return _get_datasource_config()
        elif category == "email":
            return _get_email_config()
        elif category == "app":
            return _get_app_config()
        elif category == "star_stocks":
            return _get_star_stocks_config()
        elif category == "thresholds":
            return _get_thresholds_config()
        elif category == "scheduler":
            return _get_scheduler_config()
        elif category == "project":
            return _get_project_config()
        elif category == "holidays":
            return _get_holidays_config()
        elif category == "distribution":
            return _get_distribution_config()
        else:
            raise HTTPException(status_code=404, detail=f"配置分类不存在: {category}")
    except Exception as e:
        logger.error(f"获取配置分类失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/category/{category}")
async def update_category_config(
    category: str, config: Dict[str, Any], current_user: str = Depends(get_current_user)
):
    """更新指定分类的配置"""
    try:
        if category == "ai":
            return _update_ai_config(config)
        elif category == "datasource":
            return _update_datasource_config(config)
        elif category == "email":
            return _update_email_config(config)
        elif category == "app":
            return _update_app_config(config)
        elif category == "star_stocks":
            return _update_star_stocks_config(config)
        elif category == "thresholds":
            return _update_thresholds_config(config)
        elif category == "scheduler":
            return _update_scheduler_config(config)
        elif category == "project":
            return _update_project_config(config)
        elif category == "holidays":
            return _update_holidays_config(config)
        elif category == "distribution":
            return _update_distribution_config(config)
        else:
            raise HTTPException(status_code=404, detail=f"配置分类不存在: {category}")
    except Exception as e:
        logger.error(f"更新配置分类失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 全量配置接口
# ============================================================================


@router.get("/all")
async def get_all_config(current_user: str = Depends(get_current_user)):
    """获取所有配置"""
    try:
        return {
            "ai": _get_ai_config(),
            "datasource": _get_datasource_config(),
            "email": _get_email_config(),
            "app": _get_app_config(),
            "star_stocks": _get_star_stocks_config(),
            "thresholds": _get_thresholds_config(),
            "scheduler": _get_scheduler_config(),
            "project": _get_project_config(),
            "holidays": _get_holidays_config(),
            "distribution": _get_distribution_config(),
        }
    except Exception as e:
        logger.error(f"获取所有配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/batch")
async def batch_update_config(
    batch: BatchConfigUpdate, current_user: str = Depends(get_current_user)
):
    """批量更新配置"""
    try:
        results = {}
        for category, config in batch.configs.items():
            try:
                result = await update_category_config(category, config, current_user)
                results[category] = {
                    "success": True,
                    "message": result.get("message", "更新成功"),
                }
            except Exception as e:
                results[category] = {"success": False, "message": str(e)}

        logger.info(f"管理员 {current_user} 批量更新配置")
        return {"results": results}
    except Exception as e:
        logger.error(f"批量更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 单项配置接口
# ============================================================================


@router.get("/item/{key}")
async def get_config_item(key: str, current_user: str = Depends(get_current_user)):
    """获取指定配置项"""
    try:
        # 从环境变量配置获取
        env_keys = [
            "DEEPSEEK_API_KEY",
            "DEEPSEEK_BASE_URL",
            "DEEPSEEK_MODEL",
            "TUSHARE_TOKEN",
            "QQ_EMAIL",
            "QQ_EMAIL_AUTH_CODE",
            "RECEIVER_EMAIL",
            "SMTP_SERVER",
            "SMTP_PORT",
            "LOG_LEVEL",
            "LOG_ROTATION",
            "LOG_RETENTION",
            "BASE_URL",
        ]
        if key in env_keys:
            value = getattr(settings, key, None)
            if key in ["DEEPSEEK_API_KEY", "TUSHARE_TOKEN", "QQ_EMAIL_AUTH_CODE"]:
                value = _mask_value(value)
            return {"key": key, "value": value, "category": "env"}

        # 从动态配置获取
        dynamic_config = _load_dynamic_config()
        if key in dynamic_config.get("thresholds", {}):
            return {
                "key": key,
                "value": dynamic_config["thresholds"][key],
                "category": "thresholds",
            }
        if key in dynamic_config.get("scheduler", {}):
            return {
                "key": key,
                "value": dynamic_config["scheduler"][key],
                "category": "scheduler",
            }
        if key in dynamic_config.get("distribution", {}):
            value = dynamic_config["distribution"][key]
            if (
                "secret" in key.lower()
                or "token" in key.lower()
                or "key" in key.lower()
            ):
                value = _mask_value(value)
            return {"key": key, "value": value, "category": "distribution"}

        # 从项目配置获取
        project_config = _load_project_config()
        if key in project_config:
            return {"key": key, "value": project_config[key], "category": "project"}

        raise HTTPException(status_code=404, detail=f"配置项不存在: {key}")
    except Exception as e:
        logger.error(f"获取配置项失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/item/{key}")
async def update_config_item(
    key: str, value: Any, current_user: str = Depends(get_current_user)
):
    """更新指定配置项"""
    try:
        # 更新环境变量配置
        env_keys = [
            "DEEPSEEK_API_KEY",
            "DEEPSEEK_BASE_URL",
            "DEEPSEEK_MODEL",
            "TUSHARE_TOKEN",
            "QQ_EMAIL",
            "QQ_EMAIL_AUTH_CODE",
            "RECEIVER_EMAIL",
            "SMTP_SERVER",
            "SMTP_PORT",
            "LOG_LEVEL",
            "LOG_ROTATION",
            "LOG_RETENTION",
            "BASE_URL",
        ]
        if key in env_keys:
            _update_env_file(key, value)
            logger.info(f"管理员 {current_user} 更新环境配置: {key}")
            return {"message": f"配置 {key} 已更新，需要重启服务生效"}

        # 更新动态配置
        dynamic_config = _load_dynamic_config()
        if key in dynamic_config.get("thresholds", {}):
            dynamic_config["thresholds"][key] = value
            _save_dynamic_config(dynamic_config)
            logger.info(f"管理员 {current_user} 更新阈值配置: {key}")
            return {"message": f"配置 {key} 已更新"}
        if key in dynamic_config.get("scheduler", {}):
            dynamic_config["scheduler"][key] = value
            _save_dynamic_config(dynamic_config)
            logger.info(f"管理员 {current_user} 更新调度配置: {key}")
            return {"message": f"配置 {key} 已更新"}
        if key in dynamic_config.get("distribution", {}):
            dynamic_config["distribution"][key] = value
            _save_dynamic_config(dynamic_config)
            logger.info(f"管理员 {current_user} 更新分发配置: {key}")
            return {"message": f"配置 {key} 已更新"}

        # 更新项目配置
        project_config = _load_project_config()
        if key in project_config:
            project_config[key] = value
            _save_project_config(project_config)
            logger.info(f"管理员 {current_user} 更新项目配置: {key}")
            return {"message": f"配置 {key} 已更新"}

        raise HTTPException(status_code=404, detail=f"配置项不存在: {key}")
    except Exception as e:
        logger.error(f"更新配置项失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 配置验证接口
# ============================================================================


@router.post("/validate")
async def validate_config(
    config: Dict[str, Any], current_user: str = Depends(get_current_user)
):
    """验证配置"""
    try:
        errors = []

        # 验证邮箱格式
        if "QQ_EMAIL" in config:
            email = config["QQ_EMAIL"]
            if email and "@" not in email:
                errors.append("QQ_EMAIL 格式不正确")

        if "RECEIVER_EMAIL" in config:
            email = config["RECEIVER_EMAIL"]
            if email and "@" not in email:
                errors.append("RECEIVER_EMAIL 格式不正确")

        # 验证阈值范围
        if "hot_stock_threshold" in config:
            threshold = config["hot_stock_threshold"]
            if threshold is not None and (threshold < 0 or threshold > 100):
                errors.append("hot_stock_threshold 必须在 0-100 之间")

        if "limit_up_down_threshold" in config:
            threshold = config["limit_up_down_threshold"]
            if threshold is not None and (threshold < 0 or threshold > 100):
                errors.append("limit_up_down_threshold 必须在 0-100 之间")

        # 验证时间格式
        for time_key in ["us_stock_time", "a_share_time", "hot_stock_time", "ipo_time"]:
            if time_key in config:
                time_value = config[time_key]
                if time_value and ":" not in time_value:
                    errors.append(f"{time_key} 格式不正确，应为 HH:MM")

        # 验证端口范围
        if "SMTP_PORT" in config:
            port = config["SMTP_PORT"]
            if port is not None and (port < 1 or port > 65535):
                errors.append("SMTP_PORT 必须在 1-65535 之间")

        if errors:
            return {"valid": False, "errors": errors}

        return {"valid": True, "errors": []}
    except Exception as e:
        logger.error(f"验证配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{test_type}")
async def test_config(test_type: str, current_user: str = Depends(get_current_user)):
    """测试配置"""
    try:
        if test_type == "email":
            # 测试邮件发送
            from ..notification_sender.email_sender import EmailSender

            try:
                notifier = EmailSender()
                notifier.send(
                    "这是一封测试邮件，用于验证邮件配置是否正确。",
                    subject="【FinanceSail】配置测试邮件",
                )
                return {"success": True, "message": "测试邮件发送成功"}
            except Exception as e:
                return {"success": False, "message": f"测试邮件发送失败: {str(e)}"}

        elif test_type == "deepseek":
            # 测试 DeepSeek API
            import requests

            try:
                response = requests.post(
                    f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
                    json={
                        "model": settings.DEEPSEEK_MODEL,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10,
                    },
                    timeout=10,
                )
                if response.status_code == 200:
                    return {"success": True, "message": "DeepSeek API 连接成功"}
                else:
                    return {
                        "success": False,
                        "message": f"DeepSeek API 连接失败: {response.status_code}",
                    }
            except Exception as e:
                return {"success": False, "message": f"DeepSeek API 连接失败: {str(e)}"}

        elif test_type == "tushare":
            # 测试 Tushare API
            import tushare as ts

            try:
                pro = ts.pro_api(settings.TUSHARE_TOKEN)
                df = pro.trade_cal(
                    exchange="SSE", start_date="20260101", end_date="20260101"
                )
                if df is not None and not df.empty:
                    return {"success": True, "message": "Tushare API 连接成功"}
                else:
                    return {"success": False, "message": "Tushare API 返回数据为空"}
            except Exception as e:
                return {"success": False, "message": f"Tushare API 连接失败: {str(e)}"}

        else:
            raise HTTPException(
                status_code=400, detail=f"不支持的测试类型: {test_type}"
            )
    except Exception as e:
        logger.error(f"测试配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 配置备份与恢复
# ============================================================================


@router.get("/backup")
async def backup_config(current_user: str = Depends(get_current_user)):
    """备份配置"""
    try:
        backup_data = {
            "env": _get_env_config_raw(),
            "dynamic": _load_dynamic_config(),
            "project": _load_project_config(),
            "holidays": _get_holidays_config(),
        }

        # 保存备份文件
        backup_dir = settings.DATA_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"config_backup_{timestamp}.json"

        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        logger.info(f"管理员 {current_user} 备份配置到: {backup_file}")

        return {
            "success": True,
            "message": "配置备份成功",
            "backup_file": str(backup_file),
            "backup_data": backup_data,
        }
    except Exception as e:
        logger.error(f"备份配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
async def restore_config(
    backup_data: Dict[str, Any], current_user: str = Depends(get_current_user)
):
    """恢复配置"""
    try:
        # 恢复环境变量配置
        if "env" in backup_data:
            for key, value in backup_data["env"].items():
                _update_env_file(key, value)

        # 恢复动态配置
        if "dynamic" in backup_data:
            _save_dynamic_config(backup_data["dynamic"])

        # 恢复项目配置
        if "project" in backup_data:
            _save_project_config(backup_data["project"])

        # 恢复节假日配置
        if "holidays" in backup_data:
            with open(HOLIDAYS_FILE, "w", encoding="utf-8") as f:
                json.dump(backup_data["holidays"], f, ensure_ascii=False, indent=2)

        logger.info(f"管理员 {current_user} 恢复配置")

        return {"success": True, "message": "配置恢复成功，需要重启服务生效"}
    except Exception as e:
        logger.error(f"恢复配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 私有辅助函数
# ============================================================================


def _load_dynamic_config() -> Dict[str, Any]:
    """加载动态配置"""
    try:
        if DYNAMIC_CONFIG_FILE.exists():
            with open(DYNAMIC_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载动态配置失败: {e}")
    return {}


def _save_dynamic_config(config: Dict[str, Any]):
    """保存动态配置"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(DYNAMIC_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存动态配置失败: {e}")
        raise


def _load_project_config() -> Dict[str, Any]:
    """加载项目配置"""
    try:
        if PROJECT_CONFIG_FILE.exists():
            with open(PROJECT_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载项目配置失败: {e}")
    return {}


def _save_project_config(config: Dict[str, Any]):
    """保存项目配置"""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(PROJECT_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存项目配置失败: {e}")
        raise


def _get_env_config_raw() -> Dict[str, Any]:
    """获取原始环境变量配置"""
    return {
        "DEEPSEEK_API_KEY": settings.DEEPSEEK_API_KEY,
        "DEEPSEEK_BASE_URL": settings.DEEPSEEK_BASE_URL,
        "DEEPSEEK_MODEL": settings.DEEPSEEK_MODEL,
        "TUSHARE_TOKEN": settings.TUSHARE_TOKEN,
        "QQ_EMAIL": settings.QQ_EMAIL,
        "QQ_EMAIL_AUTH_CODE": settings.QQ_EMAIL_AUTH_CODE,
        "RECEIVER_EMAIL": settings.RECEIVER_EMAIL,
        "SMTP_SERVER": settings.SMTP_SERVER,
        "SMTP_PORT": settings.SMTP_PORT,
        "LOG_LEVEL": settings.LOG_LEVEL,
        "LOG_ROTATION": settings.LOG_ROTATION,
        "LOG_RETENTION": settings.LOG_RETENTION,
        "BASE_URL": settings.BASE_URL,
    }


def _mask_value(value: str) -> str:
    """脱敏显示"""
    if not value or len(value) < 8:
        return "****"
    return value[:4] + "****" + value[-4:]


def _update_env_file(key: str, value: Any):
    """更新 .env 文件"""
    try:
        env_content = ""
        if ENV_FILE.exists():
            env_content = ENV_FILE.read_text(encoding="utf-8")

        # 查找并替换
        pattern = f"{key}="
        if pattern in env_content:
            lines = env_content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith(pattern):
                    lines[i] = f"{key}={value}"
                    break
            env_content = "\n".join(lines)
        else:
            env_content += f"\n{key}={value}"

        # 保存
        ENV_FILE.write_text(env_content, encoding="utf-8")
    except Exception as e:
        logger.error(f"更新环境配置失败: {e}")
        raise


# ============================================================================
# 各分类配置获取和更新函数
# ============================================================================


def _get_ai_config() -> Dict[str, Any]:
    """获取 AI 配置"""
    return {
        "DEEPSEEK_API_KEY": _mask_value(settings.DEEPSEEK_API_KEY),
        "DEEPSEEK_BASE_URL": settings.DEEPSEEK_BASE_URL,
        "DEEPSEEK_MODEL": settings.DEEPSEEK_MODEL,
    }


def _update_ai_config(config: Dict[str, Any]):
    """更新 AI 配置"""
    for key, value in config.items():
        if value is not None:
            _update_env_file(key, value)
    return {"message": "AI 配置已更新，需要重启服务生效"}


def _get_datasource_config() -> Dict[str, Any]:
    """获取数据源配置"""
    return {"TUSHARE_TOKEN": _mask_value(settings.TUSHARE_TOKEN)}


def _update_datasource_config(config: Dict[str, Any]):
    """更新数据源配置"""
    for key, value in config.items():
        if value is not None:
            _update_env_file(key, value)
    return {"message": "数据源配置已更新，需要重启服务生效"}


def _get_email_config() -> Dict[str, Any]:
    """获取邮件配置"""
    return {
        "QQ_EMAIL": settings.QQ_EMAIL,
        "QQ_EMAIL_AUTH_CODE": _mask_value(settings.QQ_EMAIL_AUTH_CODE),
        "RECEIVER_EMAIL": settings.RECEIVER_EMAIL,
        "SMTP_SERVER": settings.SMTP_SERVER,
        "SMTP_PORT": settings.SMTP_PORT,
    }


def _update_email_config(config: Dict[str, Any]):
    """更新邮件配置"""
    for key, value in config.items():
        if value is not None:
            _update_env_file(key, value)
    return {"message": "邮件配置已更新，需要重启服务生效"}


def _get_app_config() -> Dict[str, Any]:
    """获取应用配置"""
    return {
        "BASE_URL": settings.BASE_URL,
        "LOG_LEVEL": settings.LOG_LEVEL,
        "LOG_ROTATION": settings.LOG_ROTATION,
        "LOG_RETENTION": settings.LOG_RETENTION,
    }


def _update_app_config(config: Dict[str, Any]):
    """更新应用配置"""
    for key, value in config.items():
        if value is not None:
            _update_env_file(key, value)
    return {"message": "应用配置已更新，需要重启服务生效"}


def _get_star_stocks_config() -> Dict[str, Any]:
    """获取明星股配置"""
    dynamic_config = _load_dynamic_config()
    return dynamic_config.get(
        "star_stocks",
        {
            "A股": settings.A_SHARE_STAR_STOCKS,
            "港股": settings.HK_STAR_STOCKS,
            "美股": settings.US_STAR_STOCKS,
        },
    )


def _update_star_stocks_config(config: Dict[str, Any]):
    """更新明星股配置"""
    dynamic_config = _load_dynamic_config()
    dynamic_config["star_stocks"] = config
    _save_dynamic_config(dynamic_config)
    return {"message": "明星股配置已更新"}


def _get_thresholds_config() -> Dict[str, Any]:
    """获取阈值配置"""
    dynamic_config = _load_dynamic_config()
    return dynamic_config.get(
        "thresholds",
        {
            "hot_stock_threshold": settings.HOT_STOCK_THRESHOLD,
            "limit_up_down_threshold": settings.LIMIT_UP_DOWN_THRESHOLD,
        },
    )


def _update_thresholds_config(config: Dict[str, Any]):
    """更新阈值配置"""
    dynamic_config = _load_dynamic_config()
    if "thresholds" not in dynamic_config:
        dynamic_config["thresholds"] = {}
    dynamic_config["thresholds"].update(config)
    _save_dynamic_config(dynamic_config)
    return {"message": "阈值配置已更新"}


def _get_scheduler_config() -> Dict[str, Any]:
    """获取定时任务配置"""
    dynamic_config = _load_dynamic_config()
    return dynamic_config.get(
        "scheduler",
        {
            "us_stock_time": "09:00",
            "a_share_time": "17:00",
            "hot_stock_time": "17:30",
            "ipo_time": "20:00",
        },
    )


def _update_scheduler_config(config: Dict[str, Any]):
    """更新定时任务配置"""
    dynamic_config = _load_dynamic_config()
    if "scheduler" not in dynamic_config:
        dynamic_config["scheduler"] = {}
    dynamic_config["scheduler"].update(config)
    _save_dynamic_config(dynamic_config)
    return {"message": "定时任务配置已更新，需要重启服务生效"}


def _get_project_config() -> Dict[str, Any]:
    """获取项目配置"""
    return _load_project_config() or {
        "project_name": "FinanceSail",
        "project_name_en": "FinanceSail",
        "project_version": "1.0.0",
        "project_description": "Automated Financial Content Distribution System",
        "project_logo": "⛵",
        "project_slogan": "Empowering Financial Content Distribution",
    }


def _update_project_config(config: Dict[str, Any]):
    """更新项目配置"""
    project_config = _load_project_config()
    project_config.update(config)
    _save_project_config(project_config)
    return {"message": "项目配置已更新"}


def _get_holidays_config() -> Dict[str, Any]:
    """获取节假日配置"""
    try:
        if HOLIDAYS_FILE.exists():
            with open(HOLIDAYS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"读取节假日配置失败: {e}")
    return {}


def _update_holidays_config(config: Dict[str, Any]):
    """更新节假日配置"""
    try:
        with open(HOLIDAYS_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return {"message": "节假日配置已更新"}
    except Exception as e:
        logger.error(f"更新节假日配置失败: {e}")
        raise


def _get_distribution_config() -> Dict[str, Any]:
    """获取分发配置"""
    dynamic_config = _load_dynamic_config()
    dist_config = dynamic_config.get("distribution", {})
    return {
        "wechat_app_id": _mask_value(dist_config.get("wechat_app_id", "")),
        "wechat_app_secret": _mask_value(dist_config.get("wechat_app_secret", "")),
        "toutiao_access_token": _mask_value(
            dist_config.get("toutiao_access_token", "")
        ),
        "wxpusher_app_token": _mask_value(dist_config.get("wxpusher_app_token", "")),
    }


def _update_distribution_config(config: Dict[str, Any]):
    """更新分发配置"""
    dynamic_config = _load_dynamic_config()
    if "distribution" not in dynamic_config:
        dynamic_config["distribution"] = {}
    dynamic_config["distribution"].update(config)
    _save_dynamic_config(dynamic_config)
    return {"message": "分发配置已更新"}


# ============================================================================
# 兼容旧接口
# ============================================================================


@router.get("/env")
async def get_env_config(current_user: str = Depends(get_current_user)):
    """获取环境变量配置（脱敏）- 兼容旧接口"""
    return (
        _get_ai_config()
        | _get_datasource_config()
        | _get_email_config()
        | _get_app_config()
    )


@router.put("/env")
async def update_env_config(
    config: EnvConfig, current_user: str = Depends(get_current_user)
):
    """更新环境变量配置 - 兼容旧接口"""
    updates = config.dict(exclude_unset=True)
    for key, value in updates.items():
        if value is not None:
            _update_env_file(key, value)

    logger.info(f"管理员 {current_user} 更新环境配置")
    return {"message": "配置已保存，请重启服务生效"}


@router.get("/holidays")
async def get_holidays(current_user: str = Depends(get_current_user)):
    """获取节假日配置 - 兼容旧接口"""
    return _get_holidays_config()


@router.put("/holidays")
async def update_holidays(
    data: HolidayUpdate, current_user: str = Depends(get_current_user)
):
    """更新节假日配置 - 兼容旧接口"""
    holidays = _get_holidays_config()
    holidays[str(data.year)] = data.dates

    with open(HOLIDAYS_FILE, "w", encoding="utf-8") as f:
        json.dump(holidays, f, ensure_ascii=False, indent=2)

    logger.info(f"管理员 {current_user} 更新{data.year}年节假日")
    return {"message": "节假日配置已更新"}


@router.get("/star-stocks")
async def get_star_stocks(current_user: str = Depends(get_current_user)):
    """获取明星股配置 - 兼容旧接口"""
    return _get_star_stocks_config()


@router.get("/scheduler")
async def get_scheduler_config(current_user: str = Depends(get_current_user)):
    """获取定时任务配置 - 兼容旧接口"""
    return _get_scheduler_config()
