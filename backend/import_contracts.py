#!/usr/bin/env python3
"""
导入合同文件到数据库
将backend/uploads目录中的合同文件信息插入到contracts和contract_versions表中
"""

import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Contract, ContractVersion, ContractType, ContractStatus
from datetime import datetime

# 数据库连接信息
DATABASE_URL = "postgresql://postgres:xcb123#@localhost:5432/ai_contract2"

# 合同文件目录
UPLOADS_DIR = "uploads"

print(f"连接数据库: {DATABASE_URL}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建所有表
print("确保数据库表结构存在...")
Base.metadata.create_all(bind=engine)
print("表结构检查完成！")

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("开始导入合同文件...")
    
    # 获取uploads目录中的文件
    files = os.listdir(UPLOADS_DIR)
    print(f"发现 {len(files)} 个文件")
    
    for file_name in files:
        print(f"处理文件: {file_name}")
        
        # 构建文件路径
        file_path = os.path.join(UPLOADS_DIR, file_name)
        
        # 提取合同标题（从文件名中）
        title = os.path.splitext(file_name)[0]
        
        # 提取文件类型
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext == '.pdf':
            file_type = 'application/pdf'
        elif file_ext == '.docx':
            file_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_ext == '.doc':
            file_type = 'application/msword'
        else:
            file_type = 'application/octet-stream'
        
        # 提取合同类型（基于文件名中的关键词）
        contract_type = ContractType.OTHER
        if '采购' in title:
            contract_type = ContractType.PURCHASE
        elif '销售' in title:
            contract_type = ContractType.SALE
        elif '服务' in title:
            contract_type = ContractType.SERVICE
        
        # 检查合同是否已存在
        existing_contract = db.query(Contract).filter(Contract.title == title).first()
        
        if existing_contract:
            print(f"合同 '{title}' 已存在，跳过导入")
            continue
        
        # 创建新合同
        contract = Contract(
            title=title,
            description=f"导入的合同文件: {file_name}",
            status=ContractStatus.PENDING,
            contract_type=contract_type
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)
        print(f"创建合同: {title} (ID: {contract.id})")
        
        # 创建合同版本
        version = ContractVersion(
            contract_id=contract.id,
            version=1,
            content=f"合同文件: {file_name}",
            file_path=file_path,
            file_type=file_type
        )
        db.add(version)
        db.commit()
        print(f"创建合同版本: {title} v1")
    
    print("合同文件导入完成！")
    
    # 统计导入结果
    total_contracts = db.query(Contract).count()
    total_versions = db.query(ContractVersion).count()
    print(f"数据库中共有 {total_contracts} 个合同，{total_versions} 个版本")
    
finally:
    db.close()
    print("数据库连接已关闭")
