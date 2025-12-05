#!/bin/bash

# Photo Clean 一键启动脚本
# 适用于 Synology NAS 和 Linux 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="Photo Clean"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
DATA_DIR="$PROJECT_DIR/data"
ENV_FILE="$PROJECT_DIR/backend/.env"
ENV_EXAMPLE="$PROJECT_DIR/backend/.env.example"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印分隔线
print_separator() {
    echo "=================================================="
}

# 显示欢迎信息
show_welcome() {
    clear
    print_separator
    echo -e "${GREEN}        $PROJECT_NAME - 一键启动脚本${NC}"
    print_separator
    echo ""
}

# 检查 Docker 是否安装
check_docker() {
    print_info "检查 Docker 环境..."

    if ! command -v docker &> /dev/null; then
        print_error "未检测到 Docker，请先安装 Docker"
        exit 1
    fi

    if ! docker ps &> /dev/null; then
        print_error "Docker 未运行或权限不足，请检查 Docker 服务"
        exit 1
    fi

    print_success "Docker 环境检查通过"
}

# 检查 Docker Compose 是否安装
check_docker_compose() {
    print_info "检查 Docker Compose..."

    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        print_error "未检测到 Docker Compose，请先安装"
        exit 1
    fi

    print_success "Docker Compose 检查通过"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."

    mkdir -p "$DATA_DIR/trash"
    mkdir -p "$DATA_DIR/db"

    print_success "目录创建完成"
}

# 配置环境变量
setup_env() {
    print_info "检查环境配置..."

    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            print_warning "未找到 .env 文件，正在从 .env.example 创建..."
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_success "环境配置文件已创建"
            print_warning "请检查 backend/.env 文件并根据需要修改配置"
        else
            print_error "未找到 .env.example 文件"
            exit 1
        fi
    else
        print_success "环境配置已存在"
    fi
}

# 检查照片目录配置
check_photo_dir() {
    print_info "检查照片目录配置..."

    PHOTO_MOUNT=$(grep -E "^\s*-\s*/.*:/data/photo" "$COMPOSE_FILE" | head -1 | sed 's/.*- \(.*\):.*/\1/')

    if [ -z "$PHOTO_MOUNT" ]; then
        print_warning "未在 docker-compose.yml 中找到照片目录挂载配置"
        print_warning "请编辑 docker-compose.yml 文件，配置照片目录路径"
    else
        # 移除 :ro 后缀
        PHOTO_MOUNT=$(echo "$PHOTO_MOUNT" | sed 's/:ro$//')

        if [ ! -d "$PHOTO_MOUNT" ]; then
            print_warning "照片目录不存在: $PHOTO_MOUNT"
            print_warning "请确保目录存在或修改 docker-compose.yml 中的配置"
        else
            print_success "照片目录配置正确: $PHOTO_MOUNT"
        fi
    fi
}

# 停止并清理旧容器
cleanup_old_containers() {
    print_info "检查是否存在运行中的容器..."

    if $DOCKER_COMPOSE -f "$COMPOSE_FILE" ps -q 2>/dev/null | grep -q .; then
        print_warning "发现运行中的容器，正在停止..."
        $DOCKER_COMPOSE -f "$COMPOSE_FILE" down
        print_success "旧容器已停止"
    else
        print_info "没有需要清理的容器"
    fi
}

# 构建并启动服务
start_services() {
    print_info "开始构建并启动服务..."
    print_separator

    cd "$PROJECT_DIR"

    # 构建镜像
    print_info "正在构建 Docker 镜像（首次运行可能需要较长时间）..."
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" build

    echo ""
    print_separator

    # 启动服务
    print_info "正在启动服务..."
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d

    print_success "服务启动成功"
}

# 等待服务就绪
wait_for_services() {
    print_info "等待服务就绪..."

    local max_wait=60
    local count=0

    while [ $count -lt $max_wait ]; do
        if docker ps | grep -q "photo-clean-backend" && \
           docker ps | grep -q "photo-clean-frontend"; then
            if curl -s http://localhost:8080 > /dev/null 2>&1; then
                print_success "服务已就绪"
                return 0
            fi
        fi

        sleep 2
        count=$((count + 2))
        echo -n "."
    done

    echo ""
    print_warning "服务启动超时，请检查容器日志"
}

# 显示服务状态
show_status() {
    print_separator
    print_info "服务状态:"
    print_separator

    $DOCKER_COMPOSE -f "$COMPOSE_FILE" ps

    print_separator
}

# 显示访问信息
show_access_info() {
    print_separator
    echo -e "${GREEN}服务已成功启动！${NC}"
    print_separator

    # 获取本机 IP
    if command -v hostname &> /dev/null; then
        LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
        if [ -z "$LOCAL_IP" ]; then
            LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "your-ip")
        fi
    else
        LOCAL_IP="your-ip"
    fi

    echo ""
    echo -e "${BLUE}访问地址:${NC}"
    echo -e "  本地访问: ${GREEN}http://localhost:8080${NC}"
    echo -e "  网络访问: ${GREEN}http://$LOCAL_IP:8080${NC}"
    echo ""
    echo -e "${BLUE}常用命令:${NC}"
    echo -e "  查看日志: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  停止服务: ${YELLOW}docker-compose down${NC}"
    echo -e "  重启服务: ${YELLOW}docker-compose restart${NC}"
    echo -e "  查看状态: ${YELLOW}docker-compose ps${NC}"
    echo ""
    echo -e "${BLUE}数据目录:${NC}"
    echo -e "  回收站: ${YELLOW}$DATA_DIR/trash${NC}"
    echo -e "  数据库: ${YELLOW}$DATA_DIR/db${NC}"
    echo ""
    print_separator
}

# 主函数
main() {
    show_welcome

    # 环境检查
    check_docker
    check_docker_compose

    echo ""

    # 准备工作
    create_directories
    setup_env
    check_photo_dir

    echo ""

    # 清理旧容器
    cleanup_old_containers

    echo ""

    # 启动服务
    start_services

    echo ""

    # 等待服务就绪
    wait_for_services

    echo ""

    # 显示状态
    show_status

    echo ""

    # 显示访问信息
    show_access_info
}

# 执行主函数
main
