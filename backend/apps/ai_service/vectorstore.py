"""
向量数据库封装 - ChromaDB（多数据源知识库）

数据源类型 (source_type):
  - func_case:  功能测试用例
  - api:        接口文档
  - defect:     已解决/已关闭的缺陷

支持:
  1. 多数据源分块存储（metadata + 详情分块）
  2. CRUD同步（增删改自动同步向量库）
  3. 混合检索（跨数据源加权去重）
  4. 全量/按类型重建
"""
import json
import os
import logging
from typing import List, Optional, Dict, Any

from django.conf import settings

# 禁用 ChromaDB 遥测（避免 posthog 版本不兼容导致 capture() 报错）
os.environ["ANONYMIZED_TELEMETRY"] = "False"
# 不设置 HF_ENDPOINT：模型已固化进镜像，运行时离线加载。

from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchAny, MatchValue,
)
import hashlib
import threading
import uuid

logger = logging.getLogger('ai_service')

# Docker 部署用 Qdrant，本地开发用 chromadb
def _is_docker() -> bool:
    return os.environ.get('RUN_ENV') == 'docker'

# 全局单例
_embedding_function = None
_embedding_lock = threading.Lock()
_clients = {}
_clients_lock = threading.Lock()

# 数据源类型常量
SOURCE_FUNC_CASE = "func_case"
SOURCE_API = "api"
SOURCE_DEFECT = "defect"
SOURCE_ELEMENT = "element"

# 缺陷有效状态（已解决/已关闭）
DEFECT_VALID_STATUSES = [3, 4]

# 接口有效状态（已发布/测试/完成/异常/维护）
API_VALID_STATUSES = [1, 6, 7, 8, 9]


# ==================== 基础设施 ====================

def get_embedding_function():
    """获取Embedding函数（线程安全单例）"""
    global _embedding_function
    if _embedding_function is not None:
        return _embedding_function
    with _embedding_lock:
        if _embedding_function is None:
            logger.info("首次加载Embedding模型（仅执行一次）...")
            _embedding_function = SentenceTransformerEmbeddingFunction(
                model_name=settings.AI_EMBEDDING_MODEL
            )
            logger.info("Embedding模型加载完成")
    return _embedding_function


def get_client():
    """获取向量库客户端（线程安全单例）：Docker=Qdrant，本地=Chromadb"""
    with _clients_lock:
        if 'client' not in _clients:
            if _is_docker():
                host = os.environ.get('QDRANT_HOST', 'localhost')
                _clients['client'] = QdrantClient(host=host, port=6333, timeout=30)
                logger.info("向量库后端：Qdrant (%s:6333)", host)
            else:
                os.makedirs(settings.CHROMA_DIR, exist_ok=True)
                _clients['client'] = PersistentClient(
                    path=settings.CHROMA_DIR,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                logger.info("向量库后端：Chromadb (%s)", settings.CHROMA_DIR)
    return _clients['client']


class QdrantCollection:
    """Qdrant 后端的统一集合封装，仿真 chroma 的 collection 常用接口。

    对外保持与 chroma 一致的方法与返回形状：
      - upsert(ids, documents, metadatas)
      - get(ids=None, where=None)         -> {'ids','documents','metadatas'}
      - delete(ids=None, where=None)
      - update(ids, metadatas=None, documents=None)
      - query(query_texts, n_results, include, where) -> {'ids','documents','metadatas','distances'}（嵌套列表）
      - count()
    """
    def __init__(self, name: str, client, embedding_function=None):
        self.name = name
        self.client = client
        self.ef = embedding_function
        self._dim = None

    @staticmethod
    def _point_id(collection_name: str, doc_id: str) -> uuid.UUID:
        h = hashlib.md5(f"{collection_name}\x00{doc_id}".encode("utf-8")).hexdigest()
        return uuid.UUID(h)

    @staticmethod
    def _payload_to_meta(payload: dict) -> dict:
        return {k: v for k, v in payload.items() if k not in ('__id__', 'document')}

    def _exists(self) -> bool:
        try:
            cols = self.client.get_collections().collections
            return any(c.name == self.name for c in cols)
        except Exception:
            return False

    def _ensure_collection(self):
        if not self._exists():
            if self._dim is None:
                raise RuntimeError("qdrant collection 未初始化（缺少向量维度）")
            self.client.recreate_collection(
                collection_name=self.name,
                vectors_config=VectorParams(size=self._dim, distance=Distance.COSINE),
                timeout=30,
            )
        elif self._dim is None:
            self._dim = self.client.get_collection(self.name).config.params.vectors.size

    def _embed(self, documents):
        if self.ef is None:
            raise RuntimeError("当前操作需要 embedding 模型，但未加载")
        return self.ef(documents)

    def _filter_ids(self, ids):
        return Filter(must=[FieldCondition(key='__id__', match=MatchAny(any=[str(i) for i in ids]))])

    def _filter_where(self, where):
        return Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in where.items()])

    def upsert(self, ids, documents, metadatas=None):
        if not ids:
            return
        vectors = self._embed(documents)
        if self._dim is None or not self._exists():
            self._dim = len(vectors[0])
            self._ensure_collection()
        points = []
        for i, doc_id in enumerate(ids):
            payload = {'__id__': str(doc_id), 'document': documents[i]}
            if metadatas and i < len(metadatas):
                for k, v in (metadatas[i] or {}).items():
                    payload[k] = v
            points.append(PointStruct(
                # qdrant-client 1.13 的 PointId 仅接受 int/str，传 UUID 对象会抛 ValidationError
                # （1.19 的 PointId 含 UUID 类型才接受 uuid 对象），需转为字符串 UUID。
                id=str(self._point_id(self.name, str(doc_id))),
                vector=vectors[i],
                payload=payload,
            ))
        self.client.upsert(collection_name=self.name, points=points, wait=True)

    def get(self, ids=None, where=None):
        filters = []
        if ids:
            filters.append(FieldCondition(key='__id__', match=MatchAny(any=[str(i) for i in ids])))
        if where:
            for k, v in where.items():
                filters.append(FieldCondition(key=k, match=MatchValue(value=v)))
        if not self._exists():
            return {'ids': [], 'documents': [], 'metadatas': []}
        f = Filter(must=filters) if filters else None
        out_ids, out_meta, out_doc = [], [], []
        offset = None
        while True:
            points, offset = self.client.scroll(
                collection_name=self.name, limit=1000, with_payload=True,
                with_vectors=False, scroll_filter=f, offset=offset,
            )
            for p in points:
                out_ids.append(p.payload.get('__id__', str(p.id)))
                out_doc.append(p.payload.get('document', ''))
                out_meta.append(self._payload_to_meta(p.payload))
            if not offset:
                break
        return {'ids': out_ids, 'documents': out_doc, 'metadatas': out_meta}

    def delete(self, ids=None, where=None):
        if not ids and not where:
            return
        filters = []
        if ids:
            filters.append(FieldCondition(key='__id__', match=MatchAny(any=[str(i) for i in ids])))
        if where:
            for k, v in where.items():
                filters.append(FieldCondition(key=k, match=MatchValue(value=v)))
        if self._exists():
            self.client.delete(
                collection_name=self.name,
                points_selector=Filter(must=filters) if filters else None,
                wait=True,
            )

    def update(self, ids, metadatas=None, documents=None):
        if not ids:
            return
        if documents:
            self.upsert(ids=ids, documents=documents, metadatas=metadatas)
            return
        # 仅更新 payload，保持原有向量
        if not self._exists():
            return
        for i, doc_id in enumerate(ids):
            meta = (metadatas[i] if metadatas and i < len(metadatas) else {}) or {}
            self.client.set_payload(
                collection_name=self.name,
                payload=meta,
                points=self._filter_ids([doc_id]),
                wait=True,
            )

    def query(self, query_texts=None, n_results=4, include=None, where=None):
        if not query_texts:
            return {'ids': [], 'documents': [], 'metadatas': [], 'distances': []}
        if not self._exists():
            return {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
        qf = self._filter_where(where) if where else None
        outer_ids, outer_doc, outer_meta, outer_dist = [], [], [], []
        for qt in query_texts:
            v = self._embed([qt])[0]
            res = self.client.query_points(
                collection_name=self.name, query=v, limit=n_results,
                with_payload=True, with_vectors=False, query_filter=qf,
            )
            ids, docs, metas, dists = [], [], [], []
            for sp in res.points:
                payload = sp.payload
                ids.append(payload.get('__id__', str(sp.id)))
                docs.append(payload.get('document', ''))
                metas.append(self._payload_to_meta(payload))
                dists.append(1.0 - sp.score)  # 转成 chroma 的 cosine 距离约定（similarity = 1 - distance）
            outer_ids.append(ids); outer_doc.append(docs)
            outer_meta.append(metas); outer_dist.append(dists)
        return {'ids': outer_ids, 'documents': outer_doc, 'metadatas': outer_meta, 'distances': outer_dist}

    def count(self):
        if not self._exists():
            return 0
        return self.client.count(collection_name=self.name).count


def get_collection(project_id: int, with_embedding: bool = True):
    """获取项目对应的collection

    with_embedding=False 时用于纯读取/删除（list/get/delete/stats），
    不初始化 embedding 模型，避免加载/联网下载模型导致 SSLSocket 等报错。
    """
    collection_name = f"project_{project_id}_func_cases"
    if _is_docker():
        ef = get_embedding_function() if with_embedding else None
        return QdrantCollection(collection_name, get_client(), ef)
    client = get_client()
    ef = get_embedding_function() if with_embedding else None
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


# ==================== 功能用例 ====================

def add_case_to_vectorstore(project_id: int, case_id: int, case_name: str,
                            step_text: str = "", step_table: list = None,
                            module_id: Optional[int] = None,
                            create_time: str = None, create_by_name: str = None,
                            update_time: str = None, update_by_name: str = None):
    """将功能用例添加到向量库（分块存储）"""
    try:
        collection = get_collection(project_id)
        chunks = _build_case_chunks(case_id, case_name, step_text, step_table, module_id,
                                    create_time, create_by_name, update_time, update_by_name)

        if not chunks:
            logger.warning(f"功能用例 {case_id} 无有效内容，跳过向量入库")
            return

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"功能用例 {case_id} 已添加到向量库 ({len(chunks)}块)")
    except Exception as e:
        logger.error(f"添加功能用例到向量库失败: {e}")


def delete_case_from_vectorstore(project_id: int, case_id: int):
    """从向量库删除功能用例的所有分块"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get()
        if not existing or not existing.get('ids'):
            return

        ids_to_delete = [
            id for id in existing['ids']
            if id.startswith(f"{SOURCE_FUNC_CASE}_{case_id}_")
        ]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"功能用例 {case_id} 已从向量库删除 ({len(ids_to_delete)}块)")
    except Exception as e:
        logger.error(f"删除功能用例向量失败: {e}")


def update_case_in_vectorstore(project_id: int, case_id: int, case_name: str,
                                step_text: str = "", step_table: list = None,
                                module_id: Optional[int] = None,
                                create_time: str = None, create_by_name: str = None,
                                update_time: str = None, update_by_name: str = None):
    """更新功能用例的向量（先删后加）"""
    delete_case_from_vectorstore(project_id, case_id)
    add_case_to_vectorstore(project_id, case_id, case_name, step_text, step_table, module_id,
                            create_time, create_by_name, update_time, update_by_name)


def _build_case_chunks(case_id: int, case_name: str, step_text: str,
                       step_table: list, module_id: int,
                       create_time: str = None, create_by_name: str = None,
                       update_time: str = None, update_by_name: str = None) -> List[Dict[str, Any]]:
    """将功能用例拆分为向量分块"""
    chunks = []

    # 公共元数据
    common_metadata = {
        "create_time": create_time or "",
        "create_by_name": create_by_name or "",
        "update_time": update_time or "",
        "update_by_name": update_by_name or "",
    }

    # 块1：元信息块
    meta_text = f"功能用例: {case_name}"
    meta_metadata = {
        "source_type": SOURCE_FUNC_CASE,
        "source_id": case_id,
        "source_name": case_name,
        "chunk_type": "meta",
        "project_id": 0,  # 由upsert前填充
        "module_id": module_id or 0,
    }
    meta_metadata.update(common_metadata)
    chunks.append({
        "id": f"{SOURCE_FUNC_CASE}_{case_id}_chunk_meta",
        "text": meta_text,
        "metadata": meta_metadata,
    })

    # 块2：文本步骤
    if step_text:
        text_metadata = {
            "source_type": SOURCE_FUNC_CASE,
            "source_id": case_id,
            "source_name": case_name,
            "chunk_type": "text_step",
            "project_id": 0,
            "module_id": module_id or 0,
        }
        text_metadata.update(common_metadata)
        chunks.append({
            "id": f"{SOURCE_FUNC_CASE}_{case_id}_chunk_text",
            "text": f"用例步骤: {step_text[:500]}",
            "metadata": text_metadata,
        })

    # 块3+：每个表格步骤单独分块
    if step_table:
        for i, row in enumerate(step_table):
            if not isinstance(row, dict):
                continue
            desc = row.get('step_desc', '')
            exp = row.get('step_exp', '')
            if not desc and not exp:
                continue
            chunk_text = f"步骤{i + 1}: {desc} → 预期: {exp}"
            step_metadata = {
                "source_type": SOURCE_FUNC_CASE,
                "source_id": case_id,
                "source_name": case_name,
                "chunk_type": "step",
                "chunk_index": i,
                "project_id": 0,
                "module_id": module_id or 0,
            }
            step_metadata.update(common_metadata)
            chunks.append({
                "id": f"{SOURCE_FUNC_CASE}_{case_id}_chunk_step_{i}",
                "text": chunk_text,
                "metadata": step_metadata,
            })

    return chunks


# ==================== 接口文档 ====================

def add_api_to_vectorstore(project_id: int, api_id: int):
    """将接口文档添加到向量库"""
    try:
        from apps.interfaces.models import Api
        api = Api.objects.get(id=api_id, is_delete=False)

        # 只入库有效状态的接口
        if api.status not in API_VALID_STATUSES:
            logger.info(f"接口 {api_id} 状态={api.status} 不在有效状态列表，跳过")
            return

        # 提取用户和时间信息
        create_time = str(api.create_time) if api.create_time else ""
        update_time = str(api.update_time) if api.update_time else ""
        create_by_name = api.create_by.username if api.create_by else ""
        update_by_name = api.update_by.username if api.update_by else ""

        collection = get_collection(project_id)
        chunks = _build_api_chunks(api, project_id, create_time, create_by_name, update_time, update_by_name)

        if not chunks:
            logger.warning(f"接口 {api_id} 无有效内容，跳过")
            return

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"接口 {api_id} ({api.method} {api.url}) 已添加到向量库 ({len(chunks)}块)")
    except Exception as e:
        logger.error(f"添加接口文档到向量库失败: {e}")


def delete_api_from_vectorstore(project_id: int, api_id: int):
    """从向量库删除接口文档的所有分块"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get()
        if not existing or not existing.get('ids'):
            return

        ids_to_delete = [
            id for id in existing['ids']
            if id.startswith(f"{SOURCE_API}_{api_id}_")
        ]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"接口 {api_id} 已从向量库删除 ({len(ids_to_delete)}块)")
    except Exception as e:
        logger.error(f"删除接口文档向量失败: {e}")


def update_api_in_vectorstore(project_id: int, api_id: int):
    """更新接口文档的向量（先删后加）"""
    delete_api_from_vectorstore(project_id, api_id)
    add_api_to_vectorstore(project_id, api_id)


def _build_api_chunks(api, project_id: int,
                      create_time: str = None, create_by_name: str = None,
                      update_time: str = None, update_by_name: str = None) -> List[Dict[str, Any]]:
    """将接口文档拆分为向量分块"""
    chunks = []
    service_name = api.service.name if api.service else ''
    module_name = api.module.name if api.module else ''

    # 公共元数据
    common_metadata = {
        "create_time": create_time or "",
        "create_by_name": create_by_name or "",
        "update_time": update_time or "",
        "update_by_name": update_by_name or "",
    }

    # 块1：基础信息
    core_text = (
        f"接口: {api.name}\n"
        f"方法: {api.method} {api.url}\n"
        f"所属服务: {service_name}\n"
        f"所属模块: {module_name}\n"
        f"状态: {api.get_status_display()}"
    )
    core_metadata = {
        "source_type": SOURCE_API,
        "source_id": api.id,
        "source_name": api.name,
        "source_method": api.method,
        "source_url": api.url,
        "chunk_type": "core",
        "project_id": project_id,
        "module_id": api.module_id or 0,
    }
    core_metadata.update(common_metadata)
    chunks.append({
        "id": f"{SOURCE_API}_{api.id}_chunk_core",
        "text": core_text,
        "metadata": core_metadata,
    })

    # 块2：请求参数
    request_parts = []
    if api.params:
        try:
            params_text = json.dumps(api.params, ensure_ascii=False)
            request_parts.append(f"查询参数: {params_text}")
        except Exception:
            pass
    if api.json:
        try:
            json_text = json.dumps(api.json, ensure_ascii=False)
            request_parts.append(f"请求体JSON: {json_text}")
        except Exception:
            pass
    if api.data:
        try:
            data_text = json.dumps(api.data, ensure_ascii=False)
            request_parts.append(f"请求体FormData: {data_text}")
        except Exception:
            pass

    if request_parts:
        request_text = f"接口【{api.name}】请求参数:\n" + "\n".join(request_parts)
        # 限制单块长度
        if len(request_text) > 2000:
            request_text = request_text[:2000] + "..."
        request_metadata = {
            "source_type": SOURCE_API,
            "source_id": api.id,
            "source_name": api.name,
            "source_method": api.method,
            "source_url": api.url,
            "chunk_type": "request",
            "project_id": project_id,
            "module_id": api.module_id or 0,
        }
        request_metadata.update(common_metadata)
        chunks.append({
            "id": f"{SOURCE_API}_{api.id}_chunk_request",
            "text": request_text,
            "metadata": request_metadata,
        })

    # 块3：响应结构
    if api.response:
        try:
            response_text = json.dumps(api.response, ensure_ascii=False)
        except Exception:
            response_text = str(api.response)
        response_block = f"接口【{api.name}】响应结构:\n{response_text}"
        if len(response_block) > 2000:
            response_block = response_block[:2000] + "..."
        response_metadata = {
            "source_type": SOURCE_API,
            "source_id": api.id,
            "source_name": api.name,
            "source_method": api.method,
            "source_url": api.url,
            "chunk_type": "response",
            "project_id": project_id,
            "module_id": api.module_id or 0,
        }
        response_metadata.update(common_metadata)
        chunks.append({
            "id": f"{SOURCE_API}_{api.id}_chunk_response",
            "text": response_block,
            "metadata": response_metadata,
        })

    return chunks


# ==================== 元素 ====================

def add_element_to_vectorstore(project_id: int, element_id: int):
    """将元素库的元素添加到向量库（一个元素一个分块）"""
    try:
        from apps.elements.models import Element
        element = Element.objects.get(id=element_id, is_delete=False)

        collection = get_collection(project_id)
        chunk = _build_element_chunk(element, project_id)

        if not chunk:
            logger.warning(f"元素 {element_id} 无有效内容，跳过")
            return

        collection.upsert(ids=[chunk["id"]], documents=[chunk["text"]], metadatas=[chunk["metadata"]])
        logger.info(f"元素 {element_id} ({element.name}) 已添加到向量库")
    except Exception as e:
        logger.error(f"添加元素到向量库失败: {e}")


def delete_element_from_vectorstore(project_id: int, element_id: int):
    """从向量库删除元素的向量分块"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get()
        if not existing or not existing.get('ids'):
            return
        ids_to_delete = [
            id for id in existing['ids']
            if id.startswith(f"{SOURCE_ELEMENT}_{element_id}_")
        ]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"元素 {element_id} 已从向量库删除 ({len(ids_to_delete)}块)")
    except Exception as e:
        logger.error(f"删除元素向量失败: {e}")


def update_element_in_vectorstore(project_id: int, element_id: int):
    """更新元素的向量（先删后加）"""
    delete_element_from_vectorstore(project_id, element_id)
    add_element_to_vectorstore(project_id, element_id)


def _format_element_locations(loc):
    """将元素定位（单对象 {by,value,opts}，兼容旧版列表数据）格式化为可读文本"""
    if not loc:
        return ""
    # 兼容旧版本：曾用列表存储多条定位
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    if not isinstance(loc, dict):
        return ""
    by = loc.get('by', '')
    value = loc.get('value', '')
    if by or value:
        return f"{by}={value}"
    return ""


def _build_element_chunk(element, project_id: int) -> Optional[Dict[str, Any]]:
    """将单个元素构建为向量分块（合并多平台、多重定位描述）"""
    module_name = element.module.name if getattr(element, 'module_id', None) else ''

    text_parts = [
        f"元素: {element.name}",
        f"元素类型: {element.type}",
        f"所属模块: {module_name}",
    ]
    if element.type == 'web':
        loc = _format_element_locations(element.web or [])
        if loc:
            text_parts.append(f"Web元素定位: {loc}")
    else:
        android_loc = _format_element_locations(element.android or [])
        if android_loc:
            text_parts.append(f"Android元素定位: {android_loc}")
        ios_loc = _format_element_locations(element.ios or [])
        if ios_loc:
            text_parts.append(f"IOS元素定位: {ios_loc}")

    document = "\n".join(text_parts)

    metadata = {
        "source_type": SOURCE_ELEMENT,
        "source_id": element.id,
        "source_name": element.name,
        "chunk_type": "element_meta",
        "project_id": project_id,
        "module_id": element.module_id or 0,
        "create_time": str(element.create_time) if element.create_time else "",
        "create_by_name": element.create_by.username if element.create_by else "",
        "update_time": str(element.update_time) if element.update_time else "",
        "update_by_name": element.update_by.username if element.update_by else "",
    }

    return {
        "id": f"{SOURCE_ELEMENT}_{element.id}_chunk_element_meta",
        "text": document,
        "metadata": metadata,
    }


# ==================== 缺陷 ====================

def add_defect_to_vectorstore(project_id: int, defect_id: int):
    """将已解决/已关闭的缺陷添加到向量库"""
    try:
        from apps.defects.models import Defect
        defect = Defect.objects.get(id=defect_id, is_delete=False)

        # 只入库已解决/已关闭的缺陷
        if defect.status not in DEFECT_VALID_STATUSES:
            logger.info(f"缺陷 {defect_id} 状态={defect.status} 非已解决/已关闭，跳过")
            return

        # 跳过无意义的缺陷类型
        if defect.defect_type in [3, 4, 5]:  # BY_DESIGN, DUPLICATE, REQUIREMENT_CHANGE
            logger.info(f"缺陷 {defect_id} 类型={defect.defect_type} 无知识价值，跳过")
            return

        # 提取用户和时间信息
        create_time = str(defect.create_time) if defect.create_time else ""
        update_time = str(defect.update_time) if defect.update_time else ""
        create_by_name = defect.create_by.username if defect.create_by else ""
        update_by_name = defect.update_by.username if defect.update_by else ""

        collection = get_collection(project_id)
        chunks = _build_defect_chunks(defect, project_id, create_time, create_by_name, update_time, update_by_name)

        if not chunks:
            return

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"缺陷 {defect_id} ({defect.title[:30]}) 已添加到向量库 ({len(chunks)}块)")
    except Exception as e:
        logger.error(f"添加缺陷到向量库失败: {e}")


def delete_defect_from_vectorstore(project_id: int, defect_id: int):
    """从向量库删除缺陷的所有分块"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get()
        if not existing or not existing.get('ids'):
            return

        ids_to_delete = [
            id for id in existing['ids']
            if id.startswith(f"{SOURCE_DEFECT}_{defect_id}_")
        ]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"缺陷 {defect_id} 已从向量库删除 ({len(ids_to_delete)}块)")
    except Exception as e:
        logger.error(f"删除缺陷向量失败: {e}")


def update_defect_in_vectorstore(project_id: int, defect_id: int):
    """更新缺陷的向量（先删后加）"""
    delete_defect_from_vectorstore(project_id, defect_id)
    # 如果状态变为非有效状态，delete后不再add
    try:
        from apps.defects.models import Defect
        defect = Defect.objects.filter(id=defect_id, is_delete=False).first()
        if defect and defect.status in DEFECT_VALID_STATUSES:
            add_defect_to_vectorstore(project_id, defect_id)
    except Exception as e:
        logger.error(f"更新缺陷向量失败: {e}")


def _build_defect_chunks(defect, project_id: int,
                         create_time: str = None, create_by_name: str = None,
                         update_time: str = None, update_by_name: str = None) -> List[Dict[str, Any]]:
    """将缺陷拆分为向量分块"""
    chunks = []
    module_name = defect.module.name if defect.module else '未分配'

    # 公共元数据
    common_metadata = {
        "create_time": create_time or "",
        "create_by_name": create_by_name or "",
        "update_time": update_time or "",
        "update_by_name": update_by_name or "",
    }

    # 块1：基础信息（仅元数据，用于快速定位缺陷）
    core_text = (
        f"缺陷标题: {defect.title}\n"
        f"严重程度: {defect.get_severity_display()}\n"
        f"BUG类型: {defect.get_defect_type_display()}\n"
        f"状态: {defect.get_status_display()}\n"
        f"所属模块: {module_name}"
    )
    core_metadata = {
        "source_type": SOURCE_DEFECT,
        "source_id": defect.id,
        "source_name": defect.title[:50],
        "source_severity": defect.severity,
        "source_defect_type": defect.defect_type,
        "source_status": defect.status,
        "chunk_type": "defect_core",
        "project_id": project_id,
        "module_id": defect.module_id or 0,
    }
    core_metadata.update(common_metadata)
    chunks.append({
        "id": f"{SOURCE_DEFECT}_{defect.id}_chunk_core",
        "text": core_text,
        "metadata": core_metadata,
    })

    # 块2：详细描述（描述 + 预期结果 + 实际结果）
    detail_parts = []
    if defect.description:
        detail_parts.append(f"缺陷描述: {defect.description[:800]}")
    if defect.expected_result:
        detail_parts.append(f"预期结果: {defect.expected_result[:500]}")
    if defect.actual_result:
        detail_parts.append(f"实际结果: {defect.actual_result[:500]}")
    
    if detail_parts:
        detail_metadata = {
            "source_type": SOURCE_DEFECT,
            "source_id": defect.id,
            "source_name": defect.title[:50],
            "chunk_type": "detail",
            "project_id": project_id,
            "module_id": defect.module_id or 0,
        }
        detail_metadata.update(common_metadata)
        chunks.append({
            "id": f"{SOURCE_DEFECT}_{defect.id}_chunk_detail",
            "text": "\n".join(detail_parts),
            "metadata": detail_metadata,
        })

    return chunks


# ==================== 混合检索 ====================

def hybrid_search(project_id: int, query: str,
                   source_types: List[str] = None,
                   module_id: Optional[int] = None,
                   top_k: int = 5,
                   min_similarity: float = 0.3) -> List[Dict[str, Any]]:
    """
    跨数据源混合检索

    Args:
        project_id: 项目ID
        query: 查询文本
        source_types: 要检索的数据源类型列表，默认全部
        module_id: 模块ID过滤
        top_k: 返回结果数
        min_similarity: 最低相似度阈值（0-1，越大越严格）

    Returns:
        按相似度排序的结果列表
    """
    if source_types is None:
        source_types = [SOURCE_FUNC_CASE, SOURCE_API, SOURCE_DEFECT, SOURCE_ELEMENT]

    try:
        collection = get_collection(project_id)
        results = collection.query(
            query_texts=[query],
            n_results=top_k * 3,  # 多取，后续过滤
            include=["documents", "metadatas", "distances"],
        )

        if not results or not results.get('documents') or not results['documents'][0]:
            return []

        raw_docs = results['documents'][0]
        raw_metadatas = results['metadatas'][0] if results.get('metadatas') else []
        raw_distances = results['distances'][0] if results.get('distances') else []
        raw_ids = results['ids'][0] if results.get('ids') else []

        candidates = []
        for i in range(len(raw_docs)):
            metadata = raw_metadatas[i] if raw_metadatas else {}
            similarity = 1 - raw_distances[i] if raw_distances else 0

            # 数据源类型过滤
            source_type = metadata.get('source_type', SOURCE_FUNC_CASE)
            if source_type not in source_types:
                continue

            # 模块过滤
            if module_id and metadata.get('module_id') and metadata['module_id'] != module_id:
                continue

            # 相似度阈值过滤
            if similarity < min_similarity:
                continue

            candidates.append({
                'id': raw_ids[i] if raw_ids else '',
                'document': raw_docs[i],
                'metadata': metadata,
                'distance': raw_distances[i] if raw_distances else 0,
                'similarity': similarity,
            })

        # 按相似度降序排序
        candidates.sort(key=lambda x: x['similarity'], reverse=True)

        # 按source_id去重（同一用例/接口/缺陷只取相关性最高的分块）
        seen_ids = set()
        deduped = []
        for c in candidates:
            source_id = (c['metadata'].get('source_type'), c['metadata'].get('source_id'))
            if source_id not in seen_ids:
                seen_ids.add(source_id)
                deduped.append(c)

        return deduped[:top_k]
    except Exception as e:
        logger.error(f"混合检索失败: {e}")
        return []


def search_similar_cases(project_id: int, query: str,
                         module_id: Optional[int] = None,
                         top_k: int = 5) -> List[Dict[str, Any]]:
    """
    搜索相似用例（兼容旧接口，内部走混合检索）
    只检索功能用例类型
    """
    return hybrid_search(
        project_id=project_id,
        query=query,
        source_types=[SOURCE_FUNC_CASE],
        module_id=module_id,
        top_k=top_k,
        min_similarity=0.2,
    )


def search_knowledge_base(project_id: int, query: str,
                          module_id: Optional[int] = None,
                          top_k: int = 5) -> List[Dict[str, Any]]:
    """
    搜索全部知识库（功能用例 + 接口文档 + 缺陷）
    用于AI助手回答和RAG增强生成
    """
    return hybrid_search(
        project_id=project_id,
        query=query,
        source_types=[SOURCE_FUNC_CASE, SOURCE_API, SOURCE_DEFECT, SOURCE_ELEMENT],
        module_id=module_id,
        top_k=top_k,
        min_similarity=0.3,
    )


def build_rag_context(similar_items: List[Dict[str, Any]], max_items: int = 5) -> str:
    """将检索结果构建为LLM可用的RAG上下文"""
    if not similar_items:
        return "暂无相似用例参考"

    source_labels = {
        SOURCE_FUNC_CASE: "功能用例",
        SOURCE_API: "接口文档",
        SOURCE_DEFECT: "历史缺陷",
    }

    parts = []
    for i, item in enumerate(similar_items[:max_items], 1):
        metadata = item.get('metadata', {})
        source_type = metadata.get('source_type', 'unknown')
        label = source_labels.get(source_type, '未知')
        name = metadata.get('source_name', '未知')
        doc_text = item.get('document', '')

        # 截断过长的文档
        if len(doc_text) > 300:
            doc_text = doc_text[:300] + '...'

        parts.append(f"{i}. [{label}] {name}\n{doc_text}")

    return "以下是项目知识库中检索到的相关内容，供参考：\n\n" + "\n\n".join(parts) + "\n\n请在生成时参考上述内容。"


# ==================== 重建 ====================

def rebuild_vectorstore(project_id: int) -> Dict[str, Any]:
    """全量重建项目的向量库（所有数据源）"""
    try:
        client = get_client()
        collection_name = f"project_{project_id}_func_cases"

        # 删除旧collection
        try:
            client.delete_collection(collection_name)
            logger.info(f"已删除旧collection: {collection_name}")
        except Exception:
            pass

        # 重新创建
        get_collection(project_id)

        stats = {'func_cases': 0, 'apis': 0, 'defects': 0, 'elements': 0}

        # 1. 重建功能用例
        from apps.tests.models import FuncCase
        cases = FuncCase.objects.filter(project_id=project_id, is_delete=False)
        for case in cases:
            # 提取用户和时间信息
            create_time = str(case.create_time) if case.create_time else None
            update_time = str(case.update_time) if case.update_time else None
            create_by_name = case.create_by.username if case.create_by else None
            update_by_name = case.update_by.username if case.update_by else None
            
            add_case_to_vectorstore(
                project_id=project_id,
                case_id=case.id,
                case_name=case.name,
                step_text=case.step_text or "",
                step_table=case.step_table or [],
                module_id=case.module_id if case.module_id else None,
                create_time=create_time,
                create_by_name=create_by_name,
                update_time=update_time,
                update_by_name=update_by_name,
            )
            stats['func_cases'] += 1

        # 2. 重建接口文档
        from apps.interfaces.models import Api
        apis = Api.objects.filter(
            module__project_id=project_id,
            is_delete=False,
            status__in=API_VALID_STATUSES,
        )
        for api in apis:
            add_api_to_vectorstore(project_id, api.id)
            stats['apis'] += 1

        # 3. 重建缺陷
        from apps.defects.models import Defect
        defects = Defect.objects.filter(
            project_id=project_id,
            is_delete=False,
            status__in=DEFECT_VALID_STATUSES,
        ).exclude(defect_type__in=[3, 4, 5])

        for defect in defects:
            add_defect_to_vectorstore(project_id, defect.id)
            stats['defects'] += 1

        # 4. 重建元素
        from apps.elements.models import Element
        elements = Element.objects.filter(project_id=project_id, is_delete=False)
        for element in elements:
            add_element_to_vectorstore(project_id, element.id)
            stats['elements'] += 1

        total = stats['func_cases'] + stats['apis'] + stats['defects'] + stats['elements']
        logger.info(
            f"项目 {project_id} 向量库重建完成，共 {total} 条数据"
            f"(用例{stats['func_cases']}, 接口{stats['apis']}, 缺陷{stats['defects']}, 元素{stats['elements']})"
        )
        return {"success": True, "total": total, "stats": stats}
    except Exception as e:
        logger.error(f"重建向量库失败: {e}")
        return {"success": False, "error": str(e)}


def rebuild_source(project_id: int, source_type: str) -> Dict[str, Any]:
    """按数据源类型单独重建"""
    try:
        if source_type == SOURCE_FUNC_CASE:
            from apps.tests.models import FuncCase
            # 先清除所有func_case类型
            _clear_source_in_collection(project_id, SOURCE_FUNC_CASE)
            count = 0
            for case in FuncCase.objects.filter(project_id=project_id, is_delete=False):
                add_case_to_vectorstore(
                    project_id, case.id, case.name,
                    case.step_text or "", case.step_table or [],
                    case.module_id if case.module_id else None,
                    create_time=case.create_time,
                    create_by_name=case.create_by.username if case.create_by else None,
                    update_time=case.update_time,
                    update_by_name=case.update_by.username if case.update_by else None,
                )
                count += 1
            return {"success": True, "count": count, "source": source_type}

        elif source_type == SOURCE_API:
            from apps.interfaces.models import Api
            _clear_source_in_collection(project_id, SOURCE_API)
            count = 0
            for api in Api.objects.filter(
                module__project_id=project_id, is_delete=False,
                status__in=API_VALID_STATUSES,
            ):
                add_api_to_vectorstore(project_id, api.id)
                count += 1
            return {"success": True, "count": count, "source": source_type}

        elif source_type == SOURCE_DEFECT:
            from apps.defects.models import Defect
            _clear_source_in_collection(project_id, SOURCE_DEFECT)
            count = 0
            for defect in Defect.objects.filter(
                project_id=project_id, is_delete=False,
                status__in=DEFECT_VALID_STATUSES,
            ).exclude(defect_type__in=[3, 4, 5]):
                add_defect_to_vectorstore(project_id, defect.id)
                count += 1
            return {"success": True, "count": count, "source": source_type}

        elif source_type == SOURCE_ELEMENT:
            from apps.elements.models import Element
            _clear_source_in_collection(project_id, SOURCE_ELEMENT)
            count = 0
            for element in Element.objects.filter(project_id=project_id, is_delete=False):
                add_element_to_vectorstore(project_id, element.id)
                count += 1
            return {"success": True, "count": count, "source": source_type}

        else:
            return {"success": False, "error": f"未知的数据源类型: {source_type}"}
    except Exception as e:
        logger.error(f"重建数据源 {source_type} 失败: {e}")
        return {"success": False, "error": str(e)}


def _clear_source_in_collection(project_id: int, source_type: str):
    """清除collection中指定数据源的所有分块"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get()
        if not existing or not existing.get('ids'):
            return

        ids_to_delete = []
        for i, id_val in enumerate(existing['ids']):
            metadata = existing['metadatas'][i] if existing.get('metadatas') and i < len(existing['metadatas']) else {}
            if metadata.get('source_type') == source_type:
                ids_to_delete.append(id_val)

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"已清除数据源 {source_type} 的 {len(ids_to_delete)} 个分块")
    except Exception as e:
        logger.error(f"清除数据源 {source_type} 失败: {e}")


# ==================== 统计 ====================

def get_vectorstore_stats(project_id: int) -> Dict[str, Any]:
    """获取向量库统计信息"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get()

        if not existing or not existing.get('ids'):
            return {
                'total_chunks': 0,
                'sources': {
                    SOURCE_FUNC_CASE: {'chunks': 0, 'items': 0},
                    SOURCE_API: {'chunks': 0, 'items': 0},
                    SOURCE_DEFECT: {'chunks': 0, 'items': 0},
                    SOURCE_ELEMENT: {'chunks': 0, 'items': 0},
                }
            }

        # 按source_type统计
        source_stats = {
            SOURCE_FUNC_CASE: {'chunks': 0, 'items': set()},
            SOURCE_API: {'chunks': 0, 'items': set()},
            SOURCE_DEFECT: {'chunks': 0, 'items': set()},
            SOURCE_ELEMENT: {'chunks': 0, 'items': set()},
        }

        metadatas = existing.get('metadatas', [])
        for i, id_val in enumerate(existing['ids']):
            if i >= len(metadatas):
                break
            metadata = metadatas[i] or {}
            st = metadata.get('source_type', '')
            if st in source_stats:
                source_stats[st]['chunks'] += 1
                source_id = metadata.get('source_id')
                if source_id:
                    source_stats[st]['items'].add(source_id)

        # 转换set为count
        for st in source_stats:
            source_stats[st]['items'] = len(source_stats[st]['items'])

        total_chunks = len(existing['ids'])
        return {
            'total_chunks': total_chunks,
            'sources': source_stats,
        }
    except Exception as e:
        logger.error(f"获取向量库统计失败: {e}")
        return {'total_chunks': 0, 'sources': {}, 'error': str(e)}


# ==================== CRUD 管理 ====================

SOURCE_TYPE_LABELS = {
    SOURCE_FUNC_CASE: '功能用例',
    SOURCE_API: '接口文档',
    SOURCE_DEFECT: '已解决缺陷',
    SOURCE_ELEMENT: '元素库',
    'custom': '自定义知识',
}

CHUNK_TYPE_LABELS = {
    'meta': '用例-基础信息',
    'text_step': '用例-文本步骤',
    'step': '用例-表格步骤',
    'core': '接口-基础信息',
    'request': '接口-请求参数',
    'response': '接口-响应结构',
    'defect_core': '缺陷-基础信息',
    'detail': '缺陷-详细描述',
    'element_meta': '元素-定位信息',
    'requirement': '需求文档',
    'other': '其它',
}


def list_items(project_id: int, source_type: str = None,
                module_id: int = None, keyword: str = None,
                chunk_type: str = None,
                page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """分页查询向量库分块列表"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get()

        if not existing or not existing.get('ids'):
            return {'count': 0, 'results': [], 'page': page, 'page_size': page_size}

        ids = existing['ids']
        documents = existing.get('documents', [])
        metadatas = existing.get('metadatas', [])

        # 构建列表
        all_items = []
        for i in range(len(ids)):
            metadata = metadatas[i] if i < len(metadatas) else {}
            doc = documents[i] if i < len(documents) else ''
            item = _format_item(ids[i], doc, metadata)

            # 过滤
            if source_type and item['source_type'] != source_type:
                continue
            if chunk_type:
                # 兼容旧数据：缺陷的核心信息旧值为'core'，新值为'defect_core'
                if source_type == 'defect' and chunk_type == 'defect_core':
                    if item.get('chunk_type') not in ('defect_core', 'core'):
                        continue
                elif item.get('chunk_type') != chunk_type:
                    continue
            if module_id and item.get('module_id') and item['module_id'] != module_id:
                continue
            if keyword and keyword.lower() not in (doc or '').lower():
                name = item.get('source_name', '')
                if keyword.lower() not in name.lower():
                    continue

            all_items.append(item)

        # 按source_type + source_id + chunk_type排序
        all_items.sort(key=lambda x: (
            x.get('source_type', ''),
            x.get('source_id', 0),
            x.get('chunk_type', ''),
        ))

        total = len(all_items)
        start = (page - 1) * page_size
        end = start + page_size
        results = all_items[start:end]

        return {
            'count': total,
            'results': results,
            'page': page,
            'page_size': page_size,
        }
    except Exception as e:
        logger.error(f"list_items 失败: {e}")
        return {'count': 0, 'results': [], 'error': str(e)}


def get_item(project_id: int, item_id: str) -> Optional[Dict[str, Any]]:
    """获取单个分块详情"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        existing = collection.get(ids=[item_id])

        if not existing or not existing.get('ids'):
            return None

        ids = existing['ids']
        documents = existing.get('documents', [])
        metadatas = existing.get('metadatas', [])

        if ids:
            return _format_item(
                ids[0],
                documents[0] if documents else '',
                metadatas[0] if metadatas else {},
            )
        return None
    except Exception as e:
        logger.error(f"get_item 失败: {e}")
        return None


def create_item(project_id: int, source_type: str, source_id: int,
                 source_name: str, document: str, module_id: int = None,
                 chunk_type: str = 'custom', extra_metadata: dict = None,
                 create_by_name: str = None) -> Dict[str, Any]:
    """手动添加一个分块到向量库（长文档自动按段落拆分）"""
    try:
        from django.utils import timezone
        collection = get_collection(project_id)
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        # 需求文档自动拆分（>500字时按结构分块）
        auto_chunk_types = ('requirement',)
        if chunk_type in auto_chunk_types and len(document) > 500:
            sub_chunks = _split_document_into_chunks(
                document, document_title=source_name,
                min_chunk=300, max_chunk=800, overlap=150
            )
            if len(sub_chunks) > 1:
                # 生成基础 source_id 用于关联同一文档的多个分块
                base_id = _random_suffix()
                ids = []
                documents = []
                metadatas = []
                
                for idx, chunk_data in enumerate(sub_chunks):
                    chunk_text = chunk_data['text']
                    chunk_section = chunk_data.get('section', '')
                    chunk_id = f"{source_type}_{base_id}_chunk_{chunk_type}_{idx}_{_random_suffix()}"
                    metadata = {
                        'source_type': source_type,
                        'source_id': source_id,
                        'source_name': source_name[:100],
                        'chunk_type': chunk_type,
                        'module_id': module_id or 0,
                        'create_time': now,
                        'create_by_name': create_by_name or '',
                        'update_time': now,
                        'update_by_name': create_by_name or '',
                        'parent_id': f"{source_type}_{base_id}",
                        'chunk_index': idx + 1,
                        'chunk_total': len(sub_chunks),
                        'section': chunk_section[:200] if chunk_section else '',
                    }
                    if extra_metadata:
                        for k, v in extra_metadata.items():
                            if k not in ('source_type', 'source_id', 'source_name', 'chunk_type', 'module_id',
                                         'create_time', 'create_by_name', 'update_time', 'update_by_name',
                                         'parent_id', 'chunk_index', 'chunk_total', 'section'):
                                metadata[k] = v
                    
                    ids.append(chunk_id)
                    documents.append(chunk_text)
                    metadatas.append(metadata)
                
                collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
                logger.info(f"需求文档智能拆分: {source_name} -> {len(sub_chunks)} 个分块")
                return {
                    'success': True, 
                    'id': ids[0],
                    'chunked': True,
                    'chunk_count': len(sub_chunks),
                }

        # 普通单分块
        item_id = f"{source_type}_{source_id}_chunk_{chunk_type}_{_random_suffix()}"
        metadata = {
            'source_type': source_type,
            'source_id': source_id,
            'source_name': source_name[:100],
            'chunk_type': chunk_type,
            'module_id': module_id or 0,
            'create_time': now,
            'create_by_name': create_by_name or '',
            'update_time': now,
            'update_by_name': create_by_name or '',
        }
        if extra_metadata:
            for k, v in extra_metadata.items():
                if k not in ('source_type', 'source_id', 'source_name', 'chunk_type', 'module_id',
                             'create_time', 'create_by_name', 'update_time', 'update_by_name'):
                    metadata[k] = v

        collection.upsert(
            ids=[item_id],
            documents=[document],
            metadatas=[metadata],
        )
        logger.info(f"手动添加分块: {item_id}")
        return {'success': True, 'id': item_id, 'chunked': False, 'chunk_count': 1}
    except Exception as e:
        logger.error(f"create_item 失败: {e}")
        return {'success': False, 'error': str(e)}


def update_item(project_id: int, item_id: str, document: str = None,
                 metadata_update: dict = None) -> Dict[str, Any]:
    """更新分块内容（自动重新嵌入向量）"""
    try:
        collection = get_collection(project_id)
        existing = collection.get(ids=[item_id])

        if not existing or not existing.get('ids'):
            return {'success': False, 'error': '分块不存在'}

        ids = existing['ids']
        metadatas = existing.get('metadatas', [])
        current_metadata = metadatas[0] if metadatas else {}

        if metadata_update:
            for k, v in metadata_update.items():
                current_metadata[k] = v

        if document:
            # 重新嵌入
            collection.upsert(
                ids=[item_id],
                documents=[document],
                metadatas=[current_metadata],
            )
        else:
            # 只更新metadata（不重新嵌入）
            collection.update(
                ids=[item_id],
                metadatas=[current_metadata],
            )

        logger.info(f"更新分块: {item_id}")
        return {'success': True}
    except Exception as e:
        logger.error(f"update_item 失败: {e}")
        return {'success': False, 'error': str(e)}


def delete_item(project_id: int, item_id: str) -> Dict[str, Any]:
    """删除单个分块（关联分块会一起删除）"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        
        # 获取分块的 parent_id，如果是自动拆分的文档，则删除所有关联分块
        item = collection.get(ids=[item_id])
        if item and item.get('metadatas') and item['metadatas'][0]:
            metadata = item['metadatas'][0]
            parent_id = metadata.get('parent_id')
            if parent_id:
                # 删除同一文档的所有分块
                all_items = collection.get(where={'parent_id': parent_id})
                if all_items and all_items.get('ids'):
                    collection.delete(ids=all_items['ids'])
                    logger.info(f"删除文档分块组: {parent_id}, 共{len(all_items['ids'])}个分块")
                    return {'success': True, 'deleted_count': len(all_items['ids'])}
        
        collection.delete(ids=[item_id])
        logger.info(f"删除分块: {item_id}")
        return {'success': True, 'deleted_count': 1}
    except Exception as e:
        logger.error(f"delete_item 失败: {e}")
        return {'success': False, 'error': str(e)}


def batch_delete(project_id: int, ids: list) -> Dict[str, Any]:
    """批量删除分块（关联分块会一起删除）"""
    try:
        collection = get_collection(project_id, with_embedding=False)
        all_ids_to_delete = set(ids)
        
        # 检查是否有 parent_id 的分块，需要删除整组
        for item_id in ids:
            item = collection.get(ids=[item_id])
            if item and item.get('metadatas') and item['metadatas'][0]:
                parent_id = item['metadatas'][0].get('parent_id')
                if parent_id:
                    # 查找同一 parent_id 的所有分块
                    parent_items = collection.get(where={'parent_id': parent_id})
                    if parent_items and parent_items.get('ids'):
                        for pid in parent_items['ids']:
                            all_ids_to_delete.add(pid)
        
        all_ids_list = list(all_ids_to_delete)
        collection.delete(ids=all_ids_list)
        logger.info(f"批量删除分块: {len(ids)}个, 实际删除{len(all_ids_list)}个")
        return {'success': True, 'deleted_count': len(all_ids_list)}
    except Exception as e:
        logger.error(f"batch_delete 失败: {e}")
        return {'success': False, 'error': str(e)}


def _format_item(item_id: str, document: str, metadata: dict) -> Dict[str, Any]:
    """将原始ChromaDB数据格式化为API响应"""
    source_type = metadata.get('source_type', '')
    # 格式化时间戳
    create_time = metadata.get('create_time', '')
    update_time = metadata.get('update_time', '')
    # 如果时间戳是字符串且包含T，尝试格式化
    if create_time and 'T' in create_time:
        create_time = create_time.replace('T', ' ')[:19]
    if update_time and 'T' in update_time:
        update_time = update_time.replace('T', ' ')[:19]
    
    return {
        'id': item_id,
        'source_type': source_type,
        'source_type_label': SOURCE_TYPE_LABELS.get(source_type, source_type),
        'source_id': metadata.get('source_id', 0),
        'source_name': metadata.get('source_name', ''),
        'chunk_type': metadata.get('chunk_type', ''),
        'chunk_type_label': CHUNK_TYPE_LABELS.get(
            metadata.get('chunk_type', ''),
            metadata.get('chunk_type', '')
        ),
        'chunk_index': metadata.get('chunk_index'),
        'chunk_total': metadata.get('chunk_total'),
        'is_chunked': bool(metadata.get('chunk_total', 0) > 1),
        'section': metadata.get('section', ''),
        'module_id': metadata.get('module_id'),
        'document': document,
        'metadata': metadata,
        'source_method': metadata.get('source_method'),
        'source_url': metadata.get('source_url'),
        'create_time': create_time,
        'create_by_name': metadata.get('create_by_name', ''),
        'update_time': update_time,
        'update_by_name': metadata.get('update_by_name', ''),
    }


def _random_suffix():
    """生成随机后缀"""
    import uuid
    return uuid.uuid4().hex[:6]


def _split_document_into_chunks(text: str, document_title: str = '', 
                                 min_chunk: int = 300, max_chunk: int = 800,
                                 overlap: int = 150) -> list:
    """
    智能文档分块 V5
    1. 结构感知：识别 Markdown 标题层级，按章节拆分
    2. 完整性保护：保持代码块不被截断
    3. 上下文前缀：每个分块添加 [文档名 > 章节名] 前缀
    4. 分块重叠：相邻分块保留 overlap 字的重叠区域
    5. 长度控制：min_chunk 到 max_chunk+200 字
    
    Returns: [{'text': str, 'section': str}, ...]
    """
    if not text:
        return []
    
    full_title = document_title or '未知文档'
    import re
    
    # Step 1: 将代码块替换为占位符（避免内部的 # 被识别为标题）
    code_placeholders = {}
    code_idx = [0]
    def replace_code(m):
        key = f'\x00CB{code_idx[0]}\x00'
        code_placeholders[key] = m.group()
        code_idx[0] += 1
        return key
    
    processed = re.sub(r'```[\s\S]*?```', replace_code, text)
    
    # Step 2: 按行扫描，提取结构段落
    lines = processed.split('\n')
    segments = []  # [(text, section_path)]
    current_section = []
    
    buffer_lines = []
    buffer_section = []
    
    def make_section_str():
        return ' > '.join(current_section) if current_section else ''
    
    def flush_buffer():
        nonlocal buffer_lines, buffer_section
        if buffer_lines:
            seg_text = '\n'.join(buffer_lines).strip()
            if seg_text:
                for key, orig in code_placeholders.items():
                    seg_text = seg_text.replace(key, orig)
                section_str = ' > '.join(buffer_section) if buffer_section else ''
                segments.append((seg_text, section_str))
            buffer_lines = []
            buffer_section = []
    
    for line in lines:
        stripped = line.strip()
        
        # 检测标题
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', stripped)
        if heading_match:
            flush_buffer()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            while len(current_section) >= level:
                current_section.pop()
            current_section.append(heading_text)
            buffer_lines = [stripped]
            buffer_section = list(current_section)
            continue
        
        # 检测代码块占位符
        if stripped in code_placeholders:
            flush_buffer()
            seg_text = code_placeholders[stripped]
            sections_str = make_section_str()
            segments.append((seg_text, sections_str))
            continue
        
        if '\x00CB' in line:
            for key, orig in code_placeholders.items():
                if key in line:
                    flush_buffer()
                    segments.append((orig, make_section_str()))
                    break
            continue
        
        # 普通行
        if not buffer_lines:
            buffer_section = list(current_section)
        buffer_lines.append(line)
    
    flush_buffer()
    
    if not segments:
        return []
    
    # Step 3: 按长度合并段落
    chunks = []
    cur_text = ''
    cur_section = ''
    
    for seg_text, seg_section in segments:
        seg_len = len(seg_text)
        
        # 段落超长：先保存当前，再拆分
        if seg_len > max_chunk + 100:
            if cur_text:
                chunks.append({'text': cur_text.strip(), 'section': cur_section})
                cur_text = ''
                cur_section = ''
            
            # 按句子拆分
            sub_sentences = []
            for sep in ['。', '！', '？', '.', '!', '?', '；', ';']:
                if sep in seg_text:
                    sub_sentences = [s.strip() + sep for s in seg_text.split(sep) if s.strip()]
                    break
            if not sub_sentences:
                sub_sentences = [seg_text[i:i+max_chunk] for i in range(0, seg_len, max_chunk)]
            
            sub_chunk = ''
            for sent in sub_sentences:
                if len(sub_chunk) + len(sent) > max_chunk and sub_chunk:
                    chunks.append({'text': sub_chunk.strip(), 'section': seg_section})
                    if overlap > 0 and len(sub_chunk) > overlap:
                        sub_chunk = sub_chunk[-overlap:] + sent
                    else:
                        sub_chunk = sent
                else:
                    sub_chunk += sent
            if sub_chunk:
                chunks.append({'text': sub_chunk.strip(), 'section': seg_section})
            continue
        
        # 正常段落：判断是否合并
        combined_len = len(cur_text) + seg_len + (2 if cur_text else 0)
        if combined_len > max_chunk and cur_text:
            chunks.append({'text': cur_text.strip(), 'section': cur_section})
            cur_text = seg_text
            cur_section = seg_section
        else:
            cur_text = (cur_text + '\n\n' + seg_text) if cur_text else seg_text
            cur_section = seg_section or cur_section
    
    if cur_text:
        chunks.append({'text': cur_text.strip(), 'section': cur_section})
    
    # Step 4: 合并过短分块
    if len(chunks) > 1:
        merged = []
        i = 0
        while i < len(chunks):
            c = chunks[i]
            if len(c['text']) < min_chunk and i + 1 < len(chunks):
                nxt = chunks[i + 1]
                merged_text = c['text'] + '\n\n' + nxt['text']
                merged_section = c.get('section') or nxt.get('section', '')
                merged.append({'text': merged_text, 'section': merged_section})
                i += 2
            else:
                merged.append(c)
                i += 1
        chunks = merged
    
    # Step 5: 添加上下文前缀
    final_chunks = []
    for chunk in chunks:
        prefix = f"[{full_title}]"
        if chunk['section']:
            prefix += f" > {chunk['section']}"
        prefix += "]\n"
        chunk['text'] = prefix + chunk['text']
        final_chunks.append(chunk)
    
    return final_chunks


# ==================== 异步同步统一入口 ====================

def sync_entity_async(entity_type: str, action: str, project_id: int,
                      entity_id: int, extra: dict = None):
    """
    后台异步同步单个实体到向量库（django-q worker 调用，不阻塞主请求）。

    用于 post_save / post_delete 信号：主请求只提交一个轻量任务，
    真实向量写入（含可能的 embedding 模型加载耗时）在后台 worker 中执行。

    entity_type:  func_case | api | defect | element
    action:       create | update | delete
    extra:        仅 func_case 需要携带 create/update 时提取的文本字段
    """
    try:
        extra = extra or {}

        if action == 'delete':
            _sync_delete(entity_type, project_id, entity_id)
            return

        if entity_type == 'func_case':
            from apps.tests.models import FuncCase
            obj = FuncCase.objects.filter(id=entity_id).first()
            if not obj or obj.is_delete:
                delete_case_from_vectorstore(project_id, entity_id)
                return
            create_time = str(obj.create_time) if obj.create_time else None
            update_time = str(obj.update_time) if obj.update_time else None
            create_by_name = obj.create_by.username if obj.create_by else None
            update_by_name = obj.update_by.username if obj.update_by else None
            if action == 'create':
                add_case_to_vectorstore(
                    project_id, obj.id, obj.name,
                    obj.step_text or "", obj.step_table or [],
                    obj.module_id if obj.module_id else None,
                    create_time=create_time, create_by_name=create_by_name,
                    update_time=update_time, update_by_name=update_by_name,
                )
            else:
                update_case_in_vectorstore(
                    project_id, obj.id, obj.name,
                    obj.step_text or "", obj.step_table or [],
                    obj.module_id if obj.module_id else None,
                    create_time=create_time, create_by_name=create_by_name,
                    update_time=update_time, update_by_name=update_by_name,
                )

        elif entity_type == 'api':
            from apps.interfaces.models import Api
            obj = Api.objects.filter(id=entity_id).first()
            if not obj or obj.is_delete or obj.status not in API_VALID_STATUSES:
                delete_api_from_vectorstore(project_id, entity_id)
                return
            if action == 'create':
                add_api_to_vectorstore(project_id, obj.id)
            else:
                update_api_in_vectorstore(project_id, obj.id)

        elif entity_type == 'defect':
            from apps.defects.models import Defect
            obj = Defect.objects.filter(id=entity_id).first()
            if (not obj or obj.is_delete
                    or obj.status not in DEFECT_VALID_STATUSES
                    or obj.defect_type in [3, 4, 5]):
                delete_defect_from_vectorstore(project_id, entity_id)
                return
            if action == 'create':
                add_defect_to_vectorstore(project_id, obj.id)
            else:
                update_defect_in_vectorstore(project_id, obj.id)

        elif entity_type == 'element':
            from apps.elements.models import Element
            obj = Element.objects.filter(id=entity_id).first()
            if not obj or obj.is_delete:
                delete_element_from_vectorstore(project_id, entity_id)
                return
            if action == 'create':
                add_element_to_vectorstore(project_id, obj.id)
            else:
                update_element_in_vectorstore(project_id, obj.id)

    except Exception as e:
        logger.error(f"[异步向量同步] {entity_type} {entity_id} {action}失败: {e}")


def _sync_delete(entity_type: str, project_id: int, entity_id: int):
    """按类型执行删除向量"""
    if entity_type == 'func_case':
        delete_case_from_vectorstore(project_id, entity_id)
    elif entity_type == 'api':
        delete_api_from_vectorstore(project_id, entity_id)
    elif entity_type == 'defect':
        delete_defect_from_vectorstore(project_id, entity_id)
    elif entity_type == 'element':
        delete_element_from_vectorstore(project_id, entity_id)
