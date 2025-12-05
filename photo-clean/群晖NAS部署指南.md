# 群晖 NAS 部署指南

## 方法一：使用启动脚本（推荐）

### 1. 准备工作

确保已安装 Container Manager（套件中心搜索安装）。

### 2. 上传项目文件

通过 File Station 将整个项目文件夹上传到群晖 NAS，例如：
```
/volume1/docker/photo-clean/
```

### 3. SSH 连接到群晖

使用终端或 PuTTY 连接到群晖：
```bash
ssh admin@your-nas-ip
```

### 4. 进入项目目录

```bash
cd /volume1/docker/photo-clean
```

### 5. 赋予执行权限

```bash
chmod +x start.sh
```

### 6. 运行启动脚本

```bash
sudo ./start.sh
```

> **注意**：群晖 NAS 上需要使用 `sudo` 权限运行

### 7. 访问应用

打开浏览器访问：
```
http://your-nas-ip:8080
```

---

## 方法二：使用 Container Manager 手动部署

如果启动脚本无法运行，可以使用 Container Manager 界面手动部署。

### 步骤 1：创建必要的目录

在 File Station 中创建以下目录结构：
```
/volume1/docker/photo-clean/
├── photos/          # 放置要扫描的照片
├── data/
│   ├── trash/       # 回收站
│   └── db/          # 数据库
```

### 步骤 2：准备配置文件

1. 将 `backend/.env.example` 复制为 `backend/.env`
2. 确保 `docker-compose.yml` 中的路径正确：

```yaml
volumes:
  - ./photos:/data/photo
  - ./data/trash:/data/trash
  - ./data/db:/data/db
```

### 步骤 3：在 Container Manager 中导入

1. 打开 Container Manager
2. 点击 **项目** 标签
3. 点击 **新增**
4. 设置：
   - 项目名称：`photo-clean`
   - 路径：`/volume1/docker/photo-clean`
   - 来源：选择 **创建 docker-compose.yml**
5. 复制粘贴 `docker-compose.yml` 的内容
6. 点击 **下一步** → **完成**

### 步骤 4：启动容器

在项目列表中找到 `photo-clean`，点击启动按钮。

---

## 方法三：使用命令行直接部署

### 1. SSH 连接并进入目录

```bash
ssh admin@your-nas-ip
cd /volume1/docker/photo-clean
```

### 2. 手动运行 Docker Compose

```bash
# 尝试使用 docker compose（新版本）
sudo docker compose up -d

# 或者使用 docker-compose（旧版本）
sudo docker-compose up -d
```

### 3. 查看容器状态

```bash
sudo docker compose ps
# 或
sudo docker-compose ps
```

---

## 常见问题

### Q1: 提示 "command not found: docker"

**原因**：docker 命令不在 PATH 中。

**解决方案**：使用完整路径
```bash
# 查找 docker 位置
find /volume1 -name docker 2>/dev/null

# 使用完整路径运行
sudo /usr/local/bin/docker compose up -d
```

### Q2: 权限不足

**错误信息**：`permission denied`

**解决方案**：使用 sudo
```bash
sudo ./start.sh
```

或者添加当前用户到 docker 组：
```bash
sudo synogroup --add docker $USER
```

### Q3: 端口 8080 被占用

**解决方案**：修改 `docker-compose.yml` 中的端口映射
```yaml
ports:
  - "8081:80"  # 将 8080 改为 8081
```

### Q4: Container Manager 显示容器异常

**检查步骤**：

1. 查看容器日志：
   ```bash
   sudo docker compose logs backend
   sudo docker compose logs frontend
   ```

2. 检查目录权限：
   ```bash
   ls -la /volume1/docker/photo-clean/
   ```

3. 确保必要目录存在：
   ```bash
   mkdir -p /volume1/docker/photo-clean/data/trash
   mkdir -p /volume1/docker/photo-clean/data/db
   ```

### Q5: 无法访问 Web 界面

**检查步骤**：

1. 确认容器正在运行：
   ```bash
   sudo docker ps | grep photo-clean
   ```

2. 检查防火墙设置（控制面板 → 安全性 → 防火墙）

3. 尝试使用 NAS 的 IP 地址：
   ```
   http://192.168.x.x:8080
   ```

---

## 群晖特定配置

### 配置照片目录

如果要扫描群晖相册中的照片，修改 `docker-compose.yml`：

```yaml
volumes:
  # 扫描 Photo Station 照片
  - /volume1/photo:/data/photo

  # 或扫描 Moments 照片
  - /volume1/Moments:/data/photo

  # 或扫描 Synology Photos
  - /volume1/SynologyPhotos:/data/photo
```

### 设置任务计划自动清理回收站

1. 控制面板 → 任务计划 → 新增 → 计划的任务 → 用户定义的脚本
2. 设置：
   - 任务名称：`清理照片回收站`
   - 用户账号：`root`
   - 计划：每月 1 号执行
3. 任务设置 → 运行命令：

```bash
cd /volume1/docker/photo-clean
docker compose exec backend python -c "
from app.services.image_service import ImageService
from app.database import SessionLocal
db = SessionLocal()
service = ImageService(db)
result = service.clean_trash()
print(result)
"
```

---

## 性能优化

### 1. 使用 SSD 缓存

如果 NAS 安装了 SSD：
- 将 `data/db` 目录放在 SSD 上
- 提升数据库查询速度

### 2. 调整扫描线程数

根据 NAS 的 CPU 核心数，编辑 `backend/.env`：

```bash
# 双核 CPU
SCAN_WORKERS=2

# 四核 CPU
SCAN_WORKERS=4

# 八核 CPU
SCAN_WORKERS=6
```

### 3. 限制内存使用

如果 NAS 内存较小，在 `docker-compose.yml` 中添加：

```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
frontend:
  deploy:
    resources:
      limits:
        memory: 512M
```

---

## 备份与恢复

### 备份数据

```bash
# 备份数据库和回收站
cd /volume1/docker/photo-clean
tar -czf photo-clean-backup-$(date +%Y%m%d).tar.gz data/
```

### 恢复数据

```bash
# 解压备份
tar -xzf photo-clean-backup-20251205.tar.gz
```

---

## 卸载

### 停止并删除容器

```bash
cd /volume1/docker/photo-clean
sudo docker compose down

# 删除镜像
sudo docker rmi photo-clean-backend photo-clean-frontend
```

### 删除数据（可选）

```bash
# 删除整个项目
rm -rf /volume1/docker/photo-clean
```

---

## 故障排查命令

```bash
# 查看所有容器
sudo docker ps -a

# 查看容器日志
sudo docker logs photo-clean-backend
sudo docker logs photo-clean-frontend

# 重启容器
sudo docker restart photo-clean-backend
sudo docker restart photo-clean-frontend

# 进入容器内部
sudo docker exec -it photo-clean-backend bash

# 检查网络
sudo docker network ls
sudo docker network inspect photo-clean_photo-clean-network
```

---

## 技术支持

如果遇到问题：

1. 查看容器日志
2. 检查目录权限
3. 确认 Container Manager 正常运行
4. 提交 Issue 并附上：
   - 群晖型号和 DSM 版本
   - Container Manager 版本
   - 错误日志

---

**部署时间**：约 10-15 分钟
**推荐配置**：2GB+ RAM，双核+ CPU
**支持版本**：DSM 6.0+, DSM 7.0+
