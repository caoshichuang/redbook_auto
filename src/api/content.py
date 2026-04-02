"""
内容管理API模块
"""

import asyncio
import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..config.settings import settings
from ..models.db import Content, get_session
from ..scheduler.jobs import a_share_job, hot_stock_job, ipo_job, us_stock_job
from ..utils.logger import get_logger
from .auth import get_current_user

logger = get_logger("content_api")

router = APIRouter(prefix="/api/content", tags=["内容管理"])
preview_router = APIRouter(tags=["内容预览"])


# ─────────────────────────────────────────
# 任务进度追踪
# ─────────────────────────────────────────


@dataclass
class TaskStatus:
    task_id: str
    job_type: str
    status: str  # pending / running / completed / failed
    progress: int  # 0-100
    message: str
    created_at: str
    updated_at: str


# 内存任务状态字典（无需持久化）
task_store: Dict[str, TaskStatus] = {}


def _update_task(task_id: str, status: str, progress: int, message: str) -> None:
    """更新任务进度"""
    if task_id in task_store:
        task = task_store[task_id]
        task.status = status
        task.progress = progress
        task.message = message
        task.updated_at = datetime.now().isoformat()


async def _run_job_with_progress(task_id: str, job_func, job_name: str) -> None:
    """
    包裹 job 函数执行，并在关键节点更新任务进度。
    使用后台定时器模拟中间进度，使进度条有连续动画效果。
    """
    # 启动进度ticker：在job完成前每隔几秒缓慢递增进度
    job_done = asyncio.Event()

    async def _progress_ticker() -> None:
        checkpoints = [
            (5, 30, "正在采集数据..."),
            (15, 60, "数据采集完成，正在生成内容..."),
            (30, 80, "内容生成完成，正在渲染图片..."),
            (50, 90, "渲染完成，正在发送通知..."),
        ]
        for wait_seconds, progress, message in checkpoints:
            try:
                await asyncio.wait_for(
                    asyncio.shield(job_done.wait()), timeout=wait_seconds
                )
                # job 已结束，退出 ticker
                return
            except asyncio.TimeoutError:
                if not job_done.is_set():
                    _update_task(task_id, "running", progress, message)

    _update_task(task_id, "running", 10, f"{job_name}任务已启动，正在初始化...")
    ticker_task = asyncio.create_task(_progress_ticker())

    try:
        await job_func()
        job_done.set()
        await ticker_task
        _update_task(task_id, "completed", 100, f"{job_name}任务已完成")
        logger.info(f"任务 {task_id} ({job_name}) 完成")
    except Exception as e:
        job_done.set()
        await ticker_task
        error_msg = f"{job_name}任务失败: {str(e)}"
        _update_task(task_id, "failed", 0, error_msg)
        logger.error(f"任务 {task_id} ({job_name}) 失败: {e}")


def _create_task(job_type: str) -> str:
    """创建新任务并返回 task_id"""
    task_id = str(uuid.uuid4())
    task_store[task_id] = TaskStatus(
        task_id=task_id,
        job_type=job_type,
        status="pending",
        progress=0,
        message="任务等待执行...",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
    )
    return task_id


# ─────────────────────────────────────────
# 内容模型
# ─────────────────────────────────────────


class ContentResponse(BaseModel):
    id: int
    market: str
    content_type: str
    title: str
    content: str
    tags: str
    status: str
    created_at: str


# ─────────────────────────────────────────
# 内容列表 / 详情 / 删除
# ─────────────────────────────────────────


@router.get("/", response_model=List[ContentResponse])
async def list_content(
    market: Optional[str] = None,
    content_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    current_user: str = Depends(get_current_user),
):
    """获取内容列表"""
    session = get_session()
    try:
        query = session.query(Content)

        if market:
            query = query.filter(Content.market == market)
        if content_type:
            query = query.filter(Content.content_type == content_type)
        if date_from:
            query = query.filter(Content.created_at >= date_from)
        if date_to:
            query = query.filter(Content.created_at <= date_to)

        contents = query.order_by(Content.created_at.desc()).limit(limit).all()

        return [
            ContentResponse(
                id=c.id,
                market=c.market,
                content_type=c.content_type,
                title=c.title,
                content=c.content,
                tags=c.tags or "",
                status=c.status,
                created_at=c.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if c.created_at
                else "",
            )
            for c in contents
        ]
    finally:
        session.close()


@router.get("/stats/summary")
async def get_content_stats(current_user: str = Depends(get_current_user)):
    """获取内容统计"""
    session = get_session()
    try:
        today = date.today().strftime("%Y-%m-%d")
        today_count = session.query(Content).filter(Content.created_at >= today).count()
        total_count = session.query(Content).count()
        return {"today_count": today_count, "total_count": total_count}
    finally:
        session.close()


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, current_user: str = Depends(get_current_user)):
    """获取内容详情"""
    session = get_session()
    try:
        content = session.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="内容不存在")

        return ContentResponse(
            id=content.id,
            market=content.market,
            content_type=content.content_type,
            title=content.title,
            content=content.content,
            tags=content.tags or "",
            status=content.status,
            created_at=content.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if content.created_at
            else "",
        )
    finally:
        session.close()


@router.delete("/{content_id}")
async def delete_content(
    content_id: int, current_user: str = Depends(get_current_user)
):
    """删除内容"""
    session = get_session()
    try:
        content = session.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="内容不存在")

        session.delete(content)
        session.commit()

        logger.info(f"管理员 {current_user} 删除内容: {content_id}")
        return {"message": "删除成功"}
    finally:
        session.close()


# ─────────────────────────────────────────
# 触发接口（改为后台异步执行，立即返回 task_id）
# ─────────────────────────────────────────


@router.post("/trigger/us")
async def trigger_us_stock(current_user: str = Depends(get_current_user)):
    """手动触发美股总结（返回 task_id，通过 SSE 追踪进度）"""
    logger.info(f"管理员 {current_user} 手动触发美股总结")
    task_id = _create_task("us_stock")
    asyncio.create_task(_run_job_with_progress(task_id, us_stock_job, "美股总结"))
    return {"task_id": task_id, "status": "pending", "message": "美股总结任务已触发"}


@router.post("/trigger/a-share")
async def trigger_a_share(current_user: str = Depends(get_current_user)):
    """手动触发A股港股总结（返回 task_id，通过 SSE 追踪进度）"""
    logger.info(f"管理员 {current_user} 手动触发A股港股总结")
    task_id = _create_task("a_share")
    asyncio.create_task(_run_job_with_progress(task_id, a_share_job, "A股港股总结"))
    return {"task_id": task_id, "status": "pending", "message": "A股港股总结任务已触发"}


@router.post("/trigger/ipo")
async def trigger_ipo(current_user: str = Depends(get_current_user)):
    """手动触发IPO分析（返回 task_id，通过 SSE 追踪进度）"""
    logger.info(f"管理员 {current_user} 手动触发IPO分析")
    task_id = _create_task("ipo")
    asyncio.create_task(_run_job_with_progress(task_id, ipo_job, "IPO分析"))
    return {"task_id": task_id, "status": "pending", "message": "IPO分析任务已触发"}


@router.post("/trigger/hot")
async def trigger_hot_stock(current_user: str = Depends(get_current_user)):
    """手动触发热点个股（返回 task_id，通过 SSE 追踪进度）"""
    logger.info(f"管理员 {current_user} 手动触发热点个股")
    task_id = _create_task("hot_stock")
    asyncio.create_task(_run_job_with_progress(task_id, hot_stock_job, "热点个股"))
    return {"task_id": task_id, "status": "pending", "message": "热点个股任务已触发"}


# ─────────────────────────────────────────
# SSE 进度接口
# ─────────────────────────────────────────


@router.get("/progress/{task_id}")
async def get_task_progress(
    task_id: str,
    current_user: str = Depends(get_current_user),
):
    """
    SSE 进度流：订阅任务进度更新。
    任务完成或失败后推送最终状态并关闭连接。
    task_id 不存在时返回 404。
    """
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_stream():
        while True:
            if task_id not in task_store:
                break

            task = task_store[task_id]
            data = json.dumps(
                {
                    "progress": task.progress,
                    "status": task.status,
                    "message": task.message,
                },
                ensure_ascii=False,
            )
            yield f"data: {data}\n\n"

            if task.status in ("completed", "failed"):
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁止 Nginx 缓冲，确保 SSE 实时推送
        },
    )


# ─────────────────────────────────────────
# 预览API（无需认证）
# ─────────────────────────────────────────


class PreviewResponse(BaseModel):
    id: int
    market: str
    content_type: str
    title: str
    content: str
    tags: str
    image_urls: List[str]
    created_at: str


@preview_router.get("/api/preview/{content_id}", response_model=PreviewResponse)
async def preview_content(content_id: int):
    """预览内容详情（无需认证）"""
    session = get_session()
    try:
        content = session.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="内容不存在")

        # 解析图片路径
        image_urls = []
        if content.image_paths:
            try:
                image_paths = json.loads(content.image_paths)
                for path in image_paths:
                    path_obj = settings.PROJECT_ROOT / path
                    if path_obj.exists():
                        relative_path = str(path_obj.relative_to(settings.IMAGE_DIR))
                        image_urls.append(f"/images/{relative_path}")
                    else:
                        logger.warning(f"图片文件不存在: {path}")
            except json.JSONDecodeError:
                logger.error(f"解析图片路径失败: {content.image_paths}")

        return PreviewResponse(
            id=content.id,
            market=content.market,
            content_type=content.content_type,
            title=content.title,
            content=content.content,
            tags=content.tags or "",
            image_urls=image_urls,
            created_at=content.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if content.created_at
            else "",
        )
    finally:
        session.close()
