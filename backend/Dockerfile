# 公共基础镜像（glibc，兼容 chromadb / sentence-transformers / playwright 等 manylinux wheel）
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    RUN_ENV=docker \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    ANONYMIZED_TELEMETRY=False

# 自由猫代理（Windows 宿主 192.168.2.244:7892）。仅用于海外下载步骤：
# pip 的 pytorch 源、Playwright 浏览器二进制。实测直连海外 ~0.8MB/s，走代理 ~4.7MB/s（约快 6 倍）。
# 国内源（清华 pip/apt、hf-mirror）直连更快，不走代理。
# 构建时可用 --build-arg PROXY=http://<host>:<port> 覆盖。
ARG PROXY=http://192.168.2.244:7892

WORKDIR /app

# 系统依赖：构建工具 + 运行时库（OpenMP 用于 onnxruntime，SSL/ffi 用于编译型包）
# 切换国内镜像源，避免 deb.debian.org 网络不稳定导致构建失败
# 同时保留多源 retry，避免单个镜像临时故障导致构建失败
RUN set -eux; \
    printf 'Types: deb\nURIs: https://mirrors.tuna.tsinghua.edu.cn/debian\nSuites: trixie trixie-updates\nComponents: main contrib non-free non-free-firmware\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\n\nTypes: deb\nURIs: https://mirrors.tuna.tsinghua.edu.cn/debian-security\nSuites: trixie-security\nComponents: main contrib non-free non-free-firmware\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\n' > /etc/apt/sources.list.d/debian.sources; \
    (apt-get update || apt-get update || apt-get update) && \
    (apt-get install -y --no-install-recommends --fix-missing \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        libffi-dev \
        libssl-dev \
        libgomp1 \
        libgl1 \
        libsndfile1 \
        git \
        curl \
        tzdata \
        tesseract-ocr \
        tesseract-ocr-chi-sim || \
     apt-get install -y --no-install-recommends --fix-missing \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        libffi-dev \
        libssl-dev \
        libgomp1 \
        libgl1 \
        libsndfile1 \
        git \
        curl \
        tzdata \
        tesseract-ocr \
        tesseract-ocr-chi-sim) && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# torch(+cpu) 来自海外 pytorch.org，走代理加速；清华主源在 NO_PROXY 里保持直连
RUN HTTP_PROXY=${PROXY} HTTPS_PROXY=${PROXY} NO_PROXY=pypi.tuna.tsinghua.edu.cn,127.0.0.1,localhost pip install --no-cache-dir -r requirements.txt

# 预下载 embedding 模型固化进镜像（HF_ENDPOINT 不设置，改用 huggingface.co 直连）。
# 不要用 hf-mirror.com：其对模型文件的 308 重定向会让 huggingface_hub 报
# "Distant resource does not seem to be on huggingface.co"，导致模型加载失败、向量库写不进去。
# huggingface.co 在海外，走自由猫代理加速（HTTP_PROXY/HTTPS_PROXY）。
# 模型固化后运行时离线加载，避免每次部署都联网下载。
RUN HTTP_PROXY=${PROXY} HTTPS_PROXY=${PROXY} python -c "import os; os.environ.pop('HF_ENDPOINT', None); from huggingface_hub import snapshot_download; snapshot_download('BAAI/bge-small-zh-v1.5')"

# Playwright 浏览器本体（pip 只装了 Python 客户端，浏览器二进制需单独下载）
# + --with-deps 自动安装浏览器运行所需的系统库
# Chromium 二进制在海外 CDN，走自由猫代理加速（实测直连 ~0.8MB/s 需 40 分钟，走代理 ~40 秒）。
# 设空的小写 http_proxy/https_proxy 让 --with-deps 的 apt 仍走清华源直连（apt 只认小写）。
RUN HTTP_PROXY=${PROXY} HTTPS_PROXY=${PROXY} http_proxy= https_proxy= NO_PROXY=127.0.0.1,localhost playwright install --with-deps chromium

COPY . .

# Windows 下 entrypoint.sh 可能是 CRLF 行尾，转为 LF 并赋予执行权限，
# 否则内核解析 shebang 时找不到 /bin/sh\r 会报 "no such file or directory"
RUN sed -i 's/\r$//' ./entrypoint.sh && chmod +x ./entrypoint.sh

# 运行时数据持久化挂载点
VOLUME ["/app/logs", "/app/chroma_db", "/app/upload_files"]

EXPOSE 8000

ENTRYPOINT ["sh", "./entrypoint.sh"]
