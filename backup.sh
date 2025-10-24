#!/bin/bash

#########################################
# 数据备份脚本 - 抗衰老专家咨询系统
# 用途：备份 Milvus 数据和知识库
#########################################

set -e

# 配置
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="anti-aging-backup-$DATE"
KEEP_DAYS=7  # 保留最近7天的备份

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========== 开始备份 ==========${NC}"

# 创建备份目录
mkdir -p $BACKUP_DIR/$BACKUP_NAME

# 备份 Milvus 数据
echo "备份 Milvus 数据..."
cp -r volumes/milvus $BACKUP_DIR/$BACKUP_NAME/
cp -r volumes/etcd $BACKUP_DIR/$BACKUP_NAME/
cp -r volumes/minio $BACKUP_DIR/$BACKUP_NAME/

# 备份后端数据
echo "备份后端数据..."
cp -r backend/data $BACKUP_DIR/$BACKUP_NAME/

# 备份环境配置
echo "备份环境配置..."
cp .env $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || echo "无 .env 文件"

# 压缩备份
echo "压缩备份文件..."
cd $BACKUP_DIR
tar -czf $BACKUP_NAME.tar.gz $BACKUP_NAME
rm -rf $BACKUP_NAME

# 删除旧备份
echo "清理旧备份..."
find $BACKUP_DIR -name "anti-aging-backup-*.tar.gz" -mtime +$KEEP_DAYS -delete

echo -e "${GREEN}✓ 备份完成: $BACKUP_DIR/$BACKUP_NAME.tar.gz${NC}"
echo "备份大小: $(du -h $BACKUP_DIR/$BACKUP_NAME.tar.gz | cut -f1)"

