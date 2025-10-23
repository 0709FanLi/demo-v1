"""辅助工具函数模块.

提供通用的辅助函数，如文本处理、图片处理等。
"""

import base64
import hashlib
from io import BytesIO
from typing import List

from PIL import Image


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[str]:
    """将长文本分块.
    
    Args:
        text: 原始文本
        chunk_size: 每块的字符数
        chunk_overlap: 块之间的重叠字符数
        
    Returns:
        分块后的文本列表
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap
    
    return chunks


def generate_doc_id(content: str) -> str:
    """生成文档唯一ID.
    
    Args:
        content: 文档内容
        
    Returns:
        文档ID（MD5哈希）
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def resize_image(
    image_bytes: bytes,
    max_size: int = 1024,
) -> bytes:
    """压缩图片大小.
    
    Args:
        image_bytes: 图片字节数据
        max_size: 最大边长
        
    Returns:
        压缩后的图片字节数据
    """
    img = Image.open(BytesIO(image_bytes))
    
    # 计算缩放比例
    ratio = min(max_size / img.width, max_size / img.height)
    
    if ratio < 1:
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # 转换为字节
    output = BytesIO()
    img.save(output, format=img.format or 'JPEG')
    return output.getvalue()


def image_to_base64(image_bytes: bytes) -> str:
    """将图片转换为Base64编码.
    
    Args:
        image_bytes: 图片字节数据
        
    Returns:
        Base64编码字符串
    """
    return base64.b64encode(image_bytes).decode('utf-8')

