"""
文件/图片/文档处理器
功能：将粘贴的图片、文档转换为文本内容，供AI用例生成使用
支持格式：
  - 图片: PNG/JPG/JPEG/GIF/BMP (OCR识别)
  - 文档: PDF, DOCX, XLSX, MD, TXT, CSV (文本提取)
策略：OCR为主 + 文档解析 + LLM多模态兜底
"""
import base64
import io
import logging

logger = logging.getLogger('ai_service')

# OCR质量阈值：提取字符数低于此值视为质量差
MIN_OCR_CHARS = 10

# 文档支持的扩展名
DOC_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'xls', 'md', 'txt', 'csv', 'doc'}


def decode_base64_image(base64_str: str) -> bytes:
    """将base64字符串解码为图片二进制"""
    try:
        # 处理可能的data URI前缀
        if base64_str.startswith('data:'):
            base64_str = base64_str.split(',', 1)[1]
        return base64.b64decode(base64_str)
    except Exception as e:
        logger.error(f"Base64解码失败: {str(e)}")
        return None


def decode_base64_file(base64_str: str) -> bytes:
    """将base64字符串解码为文件二进制"""
    return decode_base64_image(base64_str)  # 复用同一逻辑


def ocr_image(image_bytes: bytes) -> str:
    """
    OCR识别图片文字
    使用 rapidocr-onnxruntime 纯Python方案，支持中英文混合识别
    Returns: 识别出的文字内容，识别失败返回空字符串
    """
    try:
        from rapidocr_onnxruntime import RapidOCR
        
        # 初始化OCR引擎（首次调用会加载模型）
        ocr = RapidOCR()
        
        # 直接传入二进制进行识别
        result, _ = ocr(image_bytes)
        
        if not result:
            logger.warning("OCR未识别到任何文字")
            return ""
        
        # 合并所有识别到的文本行
        texts = [item[1] for item in result if item[1]]
        full_text = "\n".join(texts)
        
        logger.info(f"OCR识别成功，共{len(texts)}行，{len(full_text)}个字符")
        return full_text
        
    except ImportError:
        logger.warning("rapidocr-onnxruntime 未安装，跳过OCR识别")
        return ""
    except Exception as e:
        logger.warning(f"OCR识别异常: {type(e).__name__}: {str(e)}")
        return ""


def process_images(images: list) -> list:
    """
    批量处理图片列表
    Args: images: 前端传来的图片列表，每项为 {base64, type}
    Returns: 图片识别结果列表 [{index, text, quality}]
    """
    results = []
    
    for i, img in enumerate(images):
        base64_str = img.get('base64', '')
        img_type = img.get('type', 'unknown')
        
        if not base64_str:
            results.append({
                'index': i,
                'text': '',
                'quality': 'empty',
                'error': '缺少base64数据'
            })
            continue
        
        # 解码图片
        img_bytes = decode_base64_image(base64_str)
        if not img_bytes:
            results.append({
                'index': i,
                'text': '',
                'quality': 'decode_error',
                'error': 'base64解码失败'
            })
            continue
        
        # OCR识别
        text = ocr_image(img_bytes)
        
        # 质量评估
        if not text or len(text.strip()) < MIN_OCR_CHARS:
            quality = 'poor'
            logger.warning(f"图片{i+1} OCR识别文字较少({len(text.strip())}字符)，建议使用LLM视觉兜底")
        else:
            quality = 'good'
        
        results.append({
            'index': i,
            'text': text,
            'quality': quality,
            'image_type': img_type
        })
        
        logger.info(f"图片{i+1}处理完成: quality={quality}, 字数={len(text)}")
    
    return results


# ===== 文档解析 =====

def parse_pdf(file_bytes: bytes) -> str:
    """解析PDF文件，提取文本"""
    try:
        import fitz  # PyMuPDF
        
        doc = None
        
        # 方式1: 临时文件（最稳定）
        import tempfile
        import os
        tmp_path = None
        try:
            tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(file_bytes)
            doc = fitz.open(tmp_path)
        except Exception:
            # 方式2: 直接从bytes打开（PyMuPDF 1.24+）
            try:
                if doc:
                    doc.close()
                doc = fitz.open(file_bytes)
            except Exception:
                # 方式3: BytesIO流
                try:
                    if doc:
                        doc.close()
                        doc = None
                    bio = io.BytesIO(file_bytes)
                    doc = fitz.open(stream=bio, filetype="pdf")
                except Exception as e3:
                    raise Exception(f"所有PDF打开方式都失败: {e3}")
        
        if doc is None:
            return ""
            
        texts = []
        page_count = doc.page_count
        for page in doc:
            text = page.get_text()
            if text.strip():
                texts.append(text.strip())
        doc.close()
        
        full_text = "\n\n".join(texts)
        logger.info(f"PDF解析成功，共{page_count}页，{len(full_text)}字")
        
        # 清理临时文件
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        
        return full_text
    except ImportError:
        logger.warning("PyMuPDF(fitz) 未安装，跳过PDF解析")
        return ""
    except Exception as e:
        logger.warning(f"PDF解析异常: {type(e).__name__}: {str(e)}")
        return ""


def parse_docx(file_bytes: bytes) -> str:
    """解析Word文档(.docx)"""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        texts = []
        for para in doc.paragraphs:
            if para.text.strip():
                texts.append(para.text.strip())
        # 也提取表格内容
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        texts.append(cell.text.strip())
        full_text = "\n".join(texts)
        logger.info(f"DOCX解析成功，{len(full_text)}字")
        return full_text
    except ImportError:
        logger.warning("python-docx 未安装，跳过DOCX解析")
        # 降级：尝试用docx2txt
        try:
            import docx2txt
            text = docx2txt.process(io.BytesIO(file_bytes))
            if text:
                logger.info(f"DOCX2TXT解析成功，{len(text)}字")
                return text
        except ImportError:
            logger.warning("docx2txt 也未安装")
        except Exception as e:
            logger.warning(f"DOCX2TXT异常: {e}")
        return ""
    except Exception as e:
        logger.warning(f"DOCX解析异常: {type(e).__name__}: {str(e)}")
        return ""


def parse_xlsx(file_bytes: bytes) -> str:
    """解析Excel文件(.xlsx/.xls)"""
    try:
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
        texts = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            texts.append(f"=== Sheet: {sheet_name} ===")
            for row in ws.iter_rows(values_only=True):
                row_vals = [str(c) if c is not None else '' for c in row]
                row_text = '\t'.join(row_vals).strip()
                if row_text:
                    texts.append(row_text)
        wb.close()
        full_text = "\n".join(texts)
        logger.info(f"Excel解析成功，{len(full_text)}字")
        return full_text
    except ImportError:
        logger.warning("openpyxl 未安装，跳过Excel解析")
        return ""
    except Exception as e:
        logger.warning(f"Excel解析异常: {type(e).__name__}: {str(e)}")
        return ""


def parse_text(file_bytes: bytes, ext: str) -> str:
    """解析纯文本类文件(.md/.txt/.csv)"""
    try:
        # 尝试UTF-8，失败则用gbk
        try:
            text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            text = file_bytes.decode('gbk', errors='ignore')
        logger.info(f"{ext.upper()}解析成功，{len(text)}字")
        return text
    except Exception as e:
        logger.warning(f"{ext.upper()}解析异常: {str(e)}")
        return ""


def parse_document(file_bytes: bytes, ext: str) -> str:
    """
    根据扩展名分派文档解析
    Args:
        file_bytes: 文件二进制
        ext: 文件扩展名（不含点）
    Returns: 提取的文本内容
    """
    ext = ext.lower()
    parsers = {
        'pdf': parse_pdf,
        'docx': parse_docx,
        'doc': parse_docx,  # .doc 也尝试用 python-docx（可能失败）
        'xlsx': parse_xlsx,
        'xls': parse_xlsx,
        'md': lambda b: parse_text(b, 'md'),
        'txt': lambda b: parse_text(b, 'txt'),
        'csv': lambda b: parse_text(b, 'csv'),
    }
    parser = parsers.get(ext)
    if not parser:
        logger.warning(f"不支持的文档类型: .{ext}")
        return ""
    return parser(file_bytes)


def process_documents(documents: list) -> list:
    """
    批量处理文档列表
    Args: documents: 前端传来的文档列表 [{base64, name, ext, type, size}]
    Returns: 文档解析结果列表 [{index, name, ext, text, quality}]
    """
    results = []
    
    for i, doc in enumerate(documents):
        base64_str = doc.get('base64', '')
        name = doc.get('name', f'doc_{i}')
        ext = doc.get('ext', '').lower()
        size = doc.get('size', 0)
        
        if not base64_str:
            results.append({'index': i, 'name': name, 'text': '', 'quality': 'empty'})
            continue
        
        # 解码
        file_bytes = decode_base64_file(base64_str)
        if not file_bytes:
            results.append({'index': i, 'name': name, 'text': '', 'quality': 'decode_error'})
            continue
        
        # 检查扩展名
        if ext not in DOC_EXTENSIONS:
            logger.warning(f"不支持的文档类型 .{ext}: {name}")
            results.append({'index': i, 'name': name, 'text': '', 'quality': 'unsupported', 'ext': ext})
            continue
        
        # 解析
        text = parse_document(file_bytes, ext)
        
        if not text or len(text.strip()) < 5:
            quality = 'poor'
        else:
            quality = 'good'
        
        results.append({
            'index': i,
            'name': name,
            'ext': ext,
            'size': size,
            'text': text,
            'quality': quality,
        })
        logger.info(f"文档{i+1}({name})处理完成: quality={quality}, 字数={len(text)}")
    
    return results


def build_requirement_with_documents(requirement: str, doc_results: list) -> str:
    """
    将文档解析结果拼接到需求描述中，并生成文档摘要
    """
    if not doc_results:
        return requirement or ''
    
    doc_texts = []
    for r in doc_results:
        text = r.get('text', '')
        name = r.get('name', '')
        ext = r.get('ext', '')
        if text:
            # 生成文档摘要
            summary = _summarize_document(text, name, ext)
            size_info = f" ({len(text)}字)" if text else ""
            doc_texts.append(f"[文档: {name}{size_info}]\n【文档摘要】\n{summary}\n\n【原文内容】\n{text}")
        else:
            doc_texts.append(f"[文档: {name} - 解析失败]")
    
    if not doc_texts:
        return requirement or ''
    
    separator = "\n\n--- 文档内容 ---\n"
    combined = (requirement or '') + separator + "\n\n".join(doc_texts)
    
    logger.info(f"文档拼接完成: {len(doc_texts)}个文档")
    return combined


def _summarize_document(text: str, name: str, ext: str) -> str:
    """
    规则式文档摘要提取：识别文档类型，提取关键内容
    """
    if not text:
        return "文档内容为空"
    
    # 文档类型识别
    doc_type = _detect_document_type(text, name)
    
    # 提取关键段落
    key_sections = _extract_key_sections(text, doc_type)
    
    if key_sections:
        summary = f"文档类型: {doc_type}\n\n"
        summary += "核心内容摘要:\n"
        for section in key_sections[:8]:  # 最多8个关键段
            summary += f"- {section[:200]}\n"
        return summary
    else:
        # 无关键段落，返回前500字
        return f"文档类型: {doc_type}\n文档前500字:\n{text[:500]}"


def _detect_document_type(text: str, name: str) -> str:
    """识别文档类型"""
    type_keywords = {
        '需求规格说明书': ['需求', '规格', '功能性', '非功能性', '需求规格'],
        '采购招标文档': ['采购', '招标', '磋商', '竞争性', '供应商', '投标'],
        '设计文档': ['设计', '架构', '模块', '接口', '数据库'],
        '测试文档': ['测试', '用例', '测试计划', '测试报告'],
        '产品介绍': ['产品', '功能介绍', '使用说明', '操作手册'],
        'API接口文档': ['API', '接口', 'endpoint', '请求', '响应', '参数'],
        '业务流程文档': ['业务流程', '流程图', '工作流', '审批'],
    }
    
    text_lower = text[:3000]  # 只检查前3000字
    scores = {}
    for dtype, keywords in type_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[dtype] = score
    
    if scores:
        return max(scores, key=scores.get)
    return '通用文档'


def _extract_key_sections(text: str, doc_type: str) -> list:
    """提取文档关键段落"""
    import re
    
    sections = []
    
    # 按段落分割
    paragraphs = re.split(r'\n\s*\n', text)
    
    # 关键信息关键词
    key_keywords = [
        '功能', '模块', '系统', '平台', '流程', '业务', '接口',
        '登录', '注册', '查询', '管理', '订单', '用户', '权限',
        '数据', '报表', '支付', '交易', '审批', '审核', '操作',
        '配置', '设置', '通知', '消息', '日志', '记录',
    ]
    
    # 重要段落开头关键词
    header_patterns = [
        r'^[0-9]+[.、]\s*[^\n]+',
        r'^[一二三四五六七八九十]+[、]\s*[^\n]+',
        r'^[#]+\s*[^\n]+',
        r'^\S+[功能|模块|流程|接口|系统][：:][^\n]+',
    ]
    
    for para in paragraphs:
        para_clean = para.strip()
        if len(para_clean) < 10:
            continue
        
        # 检查是否包含关键信息
        keyword_count = sum(1 for kw in key_keywords if kw in para_clean)
        
        # 检查是否是标题/小节开头
        is_header = any(re.match(p, para_clean) for p in header_patterns)
        
        if keyword_count >= 2 or is_header:
            # 限制段落长度
            if len(para_clean) > 300:
                para_clean = para_clean[:300] + '...'
            sections.append(para_clean)
    
    # 如果没找到关键段落，返回较长的段落
    if not sections:
        long_paras = [p.strip() for p in paragraphs if len(p.strip()) > 100]
        return long_paras[:5]
    
    return sections


def build_requirement_with_images(requirement: str, image_results: list) -> str:
    """
    将图片识别结果拼接到需求描述中
    Args: requirement: 用户输入的文字需求
    Returns: 拼接后的完整需求
    """
    if not image_results:
        return requirement or ''
    
    image_texts = []
    for r in image_results:
        text = r.get('text', '')
        if text:
            quality = r.get('quality', '')
            if quality == 'good':
                image_texts.append(f"[图片{r['index']+1} 识别结果]\n{text}")
            else:
                image_texts.append(f"[图片{r['index']+1} 内容(可能不完整)]\n{text}")
    
    if not image_texts:
        return requirement or ''
    
    separator = "\n\n--- 图片内容 ---\n"
    combined = (requirement or '') + separator + "\n\n".join(image_texts)
    
    logger.info(f"拼接需求完成: 文字{len(requirement or '')}字 + {len(image_texts)}张图片识别结果")
    return combined
