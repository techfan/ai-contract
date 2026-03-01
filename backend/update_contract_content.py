#!/usr/bin/env python3
"""
更新合同版本内容
从实际文件中提取内容并更新到contract_versions表中
"""

import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Contract, ContractVersion
from PyPDF2 import PdfReader
from docx import Document

# 数据库连接信息
DATABASE_URL = "postgresql://postgres:xcb123#@localhost:5432/ai_contract2"

# 合同文件目录
UPLOADS_DIR = "uploads"

# 提取文件内容的函数
def extract_text_from_file(file_path, file_type):
    """从不同类型的文件中提取文本内容"""
    try:
        if file_type == "text/plain" or file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif file_type == "application/pdf" or file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"] or file_path.endswith(".docx") or file_path.endswith(".doc"):
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            return f"不支持的文件类型: {file_type}"
    except Exception as e:
        print(f"提取文件内容失败: {str(e)}")
        return f"提取文件内容失败: {str(e)}"

print(f"连接数据库: {DATABASE_URL}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("开始更新合同版本内容...")
    
    # 获取所有合同版本
    versions = db.query(ContractVersion).all()
    print(f"找到 {len(versions)} 个合同版本")
    
    # 遍历上传目录中的实际文件
    for contract_dir in os.listdir(UPLOADS_DIR):
        contract_path = os.path.join(UPLOADS_DIR, contract_dir)
        if not os.path.isdir(contract_path):
            continue
        
        print(f"处理合同: {contract_dir}")
        
        # 遍历版本目录
        for version_dir in os.listdir(contract_path):
            if not version_dir.startswith("v"):
                continue
            
            version_path = os.path.join(contract_path, version_dir)
            if not os.path.isdir(version_path):
                continue
            
            version_num = int(version_dir[1:])
            print(f"  处理版本: v{version_num}")
            
            # 遍历文件
            for file_name in os.listdir(version_path):
                file_path = os.path.join(version_path, file_name)
                if not os.path.isfile(file_path):
                    continue
                
                print(f"    处理文件: {file_name}")
                
                # 确定文件类型
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext == '.pdf':
                    file_type = 'application/pdf'
                elif file_ext == '.docx':
                    file_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif file_ext == '.doc':
                    file_type = 'application/msword'
                else:
                    file_type = 'application/octet-stream'
                
                # 查找对应的合同
                contract = db.query(Contract).filter(Contract.title == contract_dir).first()
                if not contract:
                    print(f"    未找到对应的合同记录: {contract_dir}")
                    continue
                
                # 查找对应的版本
                version = db.query(ContractVersion).filter(
                    ContractVersion.contract_id == contract.id,
                    ContractVersion.version == version_num
                ).first()
                
                if not version:
                    print(f"    未找到对应的版本记录: v{version_num}")
                    continue
                
                # 提取文件内容
                content = extract_text_from_file(file_path, file_type)
                
                # 更新版本信息
                version.content = content
                version.file_path = file_path
                version.file_type = file_type
                db.commit()
                print(f"    更新版本内容成功: v{version_num}")
    
    print("合同版本内容更新完成！")
    
finally:
    db.close()
    print("数据库连接已关闭")
