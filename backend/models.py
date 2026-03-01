from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

# 合同状态枚举
class ContractStatus(str, enum.Enum):
    PENDING = "待审核"
    APPROVED = "已审核"
    MODIFIED = "已修改"

# 合同类型枚举
class ContractType(str, enum.Enum):
    PURCHASE = "采购"
    SALE = "销售"
    SERVICE = "服务"
    OTHER = "其他"

# 用户表
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    contracts = relationship("Contract", back_populates="creator")

# 合同表
class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(ContractStatus), default=ContractStatus.PENDING)
    contract_type = Column(Enum(ContractType), default=ContractType.OTHER)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = relationship("User", back_populates="contracts")
    versions = relationship("ContractVersion", back_populates="contract")

# 合同版本表
class ContractVersion(Base):
    __tablename__ = "contract_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    version = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(200), nullable=False)  # pdf, docx, doc等
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    contract = relationship("Contract", back_populates="versions")

# 审核规则表
class ReviewRule(Base):
    __tablename__ = "review_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(String(100), nullable=False)  # 条款类型
    pattern = Column(Text)  # 正则表达式或规则描述
    severity = Column(String(50), default="warning")  # error, warning, info
    created_at = Column(DateTime, default=datetime.utcnow)

# 对话历史表
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(100), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    messages = relationship("Message", back_populates="conversation")

# 消息表
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(50), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")