# 分布式压测客户端（可选）

「测试资产 → 脚本用例 → 性能用例 → 性能压测 → 压测工具下载」提供的是 **PyQt5 打包的
Windows 桌面客户端**，用于高并发场景下的分布式压测（master / worker 模式）。

该产物体积较大（约 60MB），且依赖离线 Python 包，**不纳入版本控制、不打进后端镜像**。
需要提供下载时，把客户端可执行文件放到本目录即可（容器内路径为 `/app/client/`，只读挂载）。

## 支持的放置方式

| 文件名 | 说明 |
|---|---|
| `QM_Test.exe` | **当前约定名**，接口优先级最高 |
| `QMTestPlatform.exe` | 过渡期命名，兼容保留 |

## 部署步骤

```bash
# 1. 放置客户端（示例）
mkdir -p /opt/qm-platform/client
cp <客户端打包产物>.exe /opt/qm-platform/client/QM_Test.exe

# 2. 让容器挂载生效（docker-compose.yml 已含 ./client:/app/client:ro）
cd /opt/qm-platform && docker compose up -d backend

# 3. 验证
curl -s http://localhost:8000/test/download/available
# -> {"code":200,"msg":"ok","result":{"available":true,"windows":true,"file":"QM_Test.exe","size":62096880}}
```

> **关于产物名**：`client/` 目录只存放打包产物，不含独立工程。产物名统一为 `QM_Test.exe`。
> 若手上是早期构建的 exe，**直接重命名为 `QM_Test.exe` 即可**——
> 它们内容一致，产品名只体现在文件名上，不影响功能。
> 需要真·新产品名的安装包时，在**已装好 PyQt5 的 Windows 环境**用源码重新打包：
> ```bash
> cd backend && pyinstaller -F --icon=./core/locust/locust.ico --name QM_Test main.py
> ```
> （客户端源码 = `backend/main.py` + `backend/core/`，打包工具链 `pyinstaller` / `locust` 已在
> `backend/requirements.txt` 中，仅 PyQt5 需另行安装。）

未放置任何文件时，接口返回 404 并给出可读提示，前端会弹「客户端未随本部署提供」的说明，
不会再把用户带到 404 空白页；此时仍可直接使用「压测配置 → 执行」进行在线压测（无需客户端）。
