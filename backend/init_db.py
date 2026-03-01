#!/usr/bin/env python3
"""
初始化数据库表结构和数据
直接连接数据库并建表初始化数据
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Conversation, Message, ReviewRule

# 直接使用用户提供的数据库连接信息
DATABASE_URL = "postgresql://postgres:xcb123#@localhost:5432/ai_contract2"

print(f"连接数据库: {DATABASE_URL}")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建所有表
print("创建数据库表结构...")
Base.metadata.create_all(bind=engine)
print("表结构创建完成！")

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("开始初始化数据...")
    
    # 检查审核规则表是否为空，如果为空则添加默认规则
    review_rule_count = db.query(ReviewRule).count()
    print(f"审核规则表当前数据量: {review_rule_count}")
    
    if review_rule_count == 0:
        print("添加默认审核规则...")
        default_rules = [
            {
                "name": "付款期限检查",
                "description": "付款期限应在收到货物后7个工作日内",
                "rule_type": "付款条款",
                "pattern": "付款期限|付款时间|支付期限",
                "severity": "warning"
            },
            {
                "name": "违约金比例检查",
                "description": "违约金比例不应超过每日0.05%",
                "rule_type": "违约条款",
                "pattern": "违约金|违约比例|违约金额",
                "severity": "error"
            },
            {
                "name": "合同有效期检查",
                "description": "合同有效期不应超过3年",
                "rule_type": "基本条款",
                "pattern": "有效期|期限|起止时间",
                "severity": "warning"
            },
            {
                "name": "争议解决方式检查",
                "description": "应明确约定争议解决方式",
                "rule_type": "争议条款",
                "pattern": "争议解决|纠纷处理|诉讼管辖",
                "severity": "info"
            },
            {
                "name": "保密条款检查",
                "description": "涉及商业秘密的合同应包含保密条款",
                "rule_type": "其他条款",
                "pattern": "保密|商业秘密|机密",
                "severity": "info"
            }
        ]
        
        for rule_data in default_rules:
            rule = ReviewRule(**rule_data)
            db.add(rule)
        
        db.commit()
        print("默认审核规则添加完成！")
    else:
        print("审核规则表已有数据，跳过初始化...")
    
    # 检查会话表是否为空，如果为空则添加一个默认会话
    conversation_count = db.query(Conversation).count()
    print(f"会话表当前数据量: {conversation_count}")
    
    if conversation_count == 0:
        print("添加默认会话...")
        default_conversation = Conversation(
            session_id="default_session",
            user_id=None
        )
        db.add(default_conversation)
        db.commit()
        
        # 添加默认欢迎消息
        welcome_message = Message(
            conversation_id=default_conversation.id,
            role="assistant",
            content="你好！我是AI合同助手，有什么可以帮你的吗？\n\n你可以：\n1. 询问合同相关的问题\n2. 上传合同文件进行分析\n3. 咨询合同审核规则\n4. 请求修改合同条款"
        )
        db.add(welcome_message)
        db.commit()
        print("默认会话添加完成！")
    else:
        print("会话表已有数据，跳过初始化...")
    
    print("数据库初始化完成！")
    
finally:
    db.close()
    print("数据库连接已关闭")
