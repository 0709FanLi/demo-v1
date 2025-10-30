"""知识库管理API路由.

提供知识库的增删改查接口。
遵守RESTful规范和企业级最佳实践。
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form

from ...models.schemas import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeResponse,
    KnowledgeSearchResult,
    KnowledgeDetail,
    ImportResult,
    ImportErrorDetail,
)
from ...services import KnowledgeService, ImportExportService
from ...utils import logger
from ..dependencies import get_knowledge_service, get_import_export_service


router = APIRouter(
    prefix='/api/v1/knowledge',
    tags=['知识库管理'],
)


@router.post(
    '/add',
    response_model=KnowledgeResponse,
    status_code=status.HTTP_201_CREATED,
    summary='添加知识条目',
    description='向知识库添加新的知识条目，支持自定义分类和元数据',
)
async def add_knowledge(
    knowledge: KnowledgeCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeResponse:
    """添加知识条目.
    
    Args:
        knowledge: 知识条目数据
        service: 知识库服务（依赖注入）
        
    Returns:
        操作结果
    """
    try:
        doc_id = await service.add_knowledge(knowledge)
        
        return KnowledgeResponse(
            success=True,
            message='知识条目添加成功',
            doc_id=doc_id,
            data={
                'category': knowledge.category,
                'content_length': len(knowledge.content),
            },
        )
        
    except Exception as e:
        logger.error(f'添加知识条目失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'添加失败: {str(e)}',
        )


@router.post(
    '/add-batch',
    response_model=KnowledgeResponse,
    status_code=status.HTTP_201_CREATED,
    summary='批量添加知识',
    description='批量添加多个知识条目',
)
async def add_knowledge_batch(
    knowledge_list: List[KnowledgeCreate],
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeResponse:
    """批量添加知识条目.
    
    Args:
        knowledge_list: 知识条目列表
        service: 知识库服务
        
    Returns:
        操作结果
    """
    try:
        doc_ids = []
        for knowledge in knowledge_list:
            doc_id = await service.add_knowledge(knowledge)
            doc_ids.append(doc_id)
        
        return KnowledgeResponse(
            success=True,
            message=f'成功添加 {len(doc_ids)} 条知识',
            data={'doc_ids': doc_ids},
        )
        
    except Exception as e:
        logger.error(f'批量添加知识失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'批量添加失败: {str(e)}',
        )


@router.get(
    '/search',
    response_model=List[KnowledgeSearchResult],
    summary='检索知识',
    description='根据查询文本检索相关知识',
)
async def search_knowledge(
    query: str,
    top_k: int = 3,
    category: Optional[str] = None,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> List[KnowledgeSearchResult]:
    """检索知识.
    
    Args:
        query: 查询文本
        top_k: 返回结果数量
        category: 过滤分类
        service: 知识库服务
        
    Returns:
        检索结果列表
    """
    try:
        results = await service.search_knowledge(
            query=query,
            top_k=top_k,
            category=category,
        )
        return results
        
    except Exception as e:
        logger.error(f'检索知识失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'检索失败: {str(e)}',
        )


@router.delete(
    '/delete/{doc_id}',
    response_model=KnowledgeResponse,
    summary='删除知识',
    description='根据文档ID删除知识条目',
)
async def delete_knowledge(
    doc_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeResponse:
    """删除知识条目.
    
    Args:
        doc_id: 文档ID
        service: 知识库服务
        
    Returns:
        操作结果
    """
    try:
        success = await service.delete_knowledge(doc_id)
        
        if success:
            return KnowledgeResponse(
                success=True,
                message='知识条目删除成功',
                doc_id=doc_id,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='文档不存在',
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'删除知识失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'删除失败: {str(e)}',
        )


@router.get(
    '/count',
    response_model=dict,
    summary='获取知识库统计',
    description='获取知识库的条目总数',
)
async def get_knowledge_count(
    service: KnowledgeService = Depends(get_knowledge_service),
) -> dict:
    """获取知识库统计.
    
    Args:
        service: 知识库服务
        
    Returns:
        统计信息
    """
    count = await service.get_knowledge_count()
    return {
        'total': count,
        'message': f'当前知识库共有 {count} 条记录',
    }


@router.get(
    '/list',
    response_model=List[KnowledgeSearchResult],
    summary='获取知识库列表',
    description='获取所有知识条目列表',
)
async def get_knowledge_list(
    limit: int = 100,
    offset: int = 0,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> List[KnowledgeSearchResult]:
    """获取知识库列表.
    
    Args:
        limit: 返回数量限制
        offset: 偏移量
        service: 知识库服务
        
    Returns:
        知识条目列表
    """
    try:
        results = await service.get_all_knowledge(limit=limit, offset=offset)
        return results
    except Exception as e:
        logger.error(f'获取知识列表失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'获取失败: {str(e)}',
        )


@router.get(
    '/{doc_id}',
    response_model=KnowledgeDetail,
    summary='获取知识详情',
    description='根据文档ID获取知识条目详情',
)
async def get_knowledge_detail(
    doc_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeDetail:
    """获取知识条目详情.
    
    Args:
        doc_id: 文档ID
        service: 知识库服务
        
    Returns:
        知识详情
    """
    try:
        result = await service.get_knowledge_by_id(doc_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'文档不存在: {doc_id}',
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'获取知识详情失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'获取失败: {str(e)}',
        )


@router.put(
    '/{doc_id}',
    response_model=KnowledgeResponse,
    summary='更新知识条目',
    description='根据文档ID更新知识条目',
)
async def update_knowledge(
    doc_id: str,
    update_data: KnowledgeUpdate,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeResponse:
    """更新知识条目.
    
    Args:
        doc_id: 文档ID
        update_data: 更新数据
        service: 知识库服务
        
    Returns:
        操作结果
    """
    try:
        success = await service.update_knowledge(doc_id, update_data)
        
        if success:
            return KnowledgeResponse(
                success=True,
                message='知识条目更新成功',
                doc_id=doc_id,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='文档不存在',
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'更新知识失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'更新失败: {str(e)}',
        )


@router.post(
    '/import',
    response_model=ImportResult,
    summary='导入知识库文件',
    description='从文件批量导入知识库（支持 JSON/CSV/Excel/TXT/Markdown/PDF）',
)
async def import_knowledge(
    file: UploadFile = File(..., description='上传的文件'),
    format: Optional[str] = Form(None, description='文件格式（auto/json/csv/excel/txt/markdown）'),
    default_category: str = Form('未分类', description='默认分类（用于 TXT 格式）'),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    import_service: ImportExportService = Depends(get_import_export_service),
) -> ImportResult:
    """导入知识库文件.
    
    Args:
        file: 上传的文件
        format: 文件格式（可选，自动检测）
        default_category: 默认分类
        knowledge_service: 知识库服务
        import_service: 导入导出服务
        
    Returns:
        导入结果
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='文件内容为空',
            )
        
        # 解析文件
        try:
            parsed_data = await import_service.parse_file(
                file_content=file_content,
                filename=file.filename or 'unknown',
                format=format,
                default_category=default_category,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'文件解析失败: {str(e)}',
            )
        
        if not parsed_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='文件中没有有效的数据',
            )
        
        # 预览数据（前5条）
        preview = parsed_data[:5]
        
        # 批量导入
        success_count = 0
        failed_count = 0
        errors = []
        
        for idx, item in enumerate(parsed_data):
            try:
                # 验证数据
                knowledge = KnowledgeCreate(
                    content=item['content'],
                    category=item.get('category', default_category),
                    title=item.get('title'),
                    tags=item.get('tags', []),
                )
                
                # 导入知识库
                await knowledge_service.add_knowledge(knowledge)
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(
                    ImportErrorDetail(
                        row=idx + 1,
                        error=str(e),
                    )
                )
                logger.warning(f'导入第 {idx + 1} 行失败: {e}')
        
        logger.info(
            f'文件导入完成 - 文件: {file.filename}, '
            f'总数: {len(parsed_data)}, 成功: {success_count}, 失败: {failed_count}'
        )
        
        return ImportResult(
            success_count=success_count,
            failed_count=failed_count,
            total_count=len(parsed_data),
            errors=errors,
            preview=preview,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'导入文件失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'导入失败: {str(e)}',
        )


@router.delete(
    '/clear',
    response_model=KnowledgeResponse,
    summary='清空知识库',
    description='【危险操作】清空所有知识库内容',
)
async def clear_knowledge(
    confirm: bool = False,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeResponse:
    """清空知识库.
    
    Args:
        confirm: 确认标志
        service: 知识库服务
        
    Returns:
        操作结果
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='请确认清空操作（设置 confirm=true）',
        )
    
    try:
        await service.clear_all()
        return KnowledgeResponse(
            success=True,
            message='知识库已清空',
        )
        
    except Exception as e:
        logger.error(f'清空知识库失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'清空失败: {str(e)}',
        )
