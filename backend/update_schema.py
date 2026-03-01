#!/usr/bin/env python3
"""
更新数据库表结构
修改contract_versions表的file_type字段长度
"""

from sqlalchemy import create_engine, text

# 数据库连接信息
DATABASE_URL = "postgresql://postgres:xcb123#@localhost:5432/ai_contract2"

print(f"连接数据库: {DATABASE_URL}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 连接数据库
with engine.connect() as conn:
    try:
        # 修改contract_versions表的file_type字段长度
        print("修改contract_versions表的file_type字段长度...")
        conn.execute(text("ALTER TABLE contract_versions ALTER COLUMN file_type TYPE VARCHAR(200);"))
        conn.commit()
        print("字段长度修改成功！")
    except Exception as e:
        print(f"修改字段长度时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

print("数据库表结构更新完成！")
