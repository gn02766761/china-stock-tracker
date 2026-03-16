"""
数据库管理模块
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()


class StockHolding(Base):
    """股票持仓表"""
    __tablename__ = 'stock_holdings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)  # 股票代码
    stock_name = Column(String(50))  # 股票名称
    shares = Column(Float, default=0)  # 持仓数量
    avg_cost = Column(Float, default=0)  # 平均成本
    buy_date = Column(DateTime, default=datetime.now)  # 买入日期
    notes = Column(Text, default='')  # 备注
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PriceAlert(Base):
    """价格预警配置表"""
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)  # 股票代码
    stock_name = Column(String(50))  # 股票名称
    alert_type = Column(String(20), nullable=False)  # 预警类型：price_above, price_below, change_above, change_below
    threshold_value = Column(Float, nullable=False)  # 阈值
    is_active = Column(Boolean, default=True)  # 是否激活
    last_triggered = Column(DateTime, nullable=True)  # 上次触发时间
    trigger_count = Column(Integer, default=0)  # 触发次数
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<PriceAlert(stock={self.stock_code}, type={self.alert_type}, threshold={self.threshold_value})>"


class TechnicalAlert(Base):
    """技术指标预警配置表"""
    __tablename__ = 'technical_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)  # 股票代码
    stock_name = Column(String(50))  # 股票名称
    indicator = Column(String(50), nullable=False)  # 指标名称：RSI, MACD, MA, etc.
    condition = Column(String(20), nullable=False)  # 条件：cross_above, cross_below, above, below
    threshold_value = Column(Float, nullable=False)  # 阈值
    is_active = Column(Boolean, default=True)  # 是否激活
    last_triggered = Column(DateTime, nullable=True)  # 上次触发时间
    created_at = Column(DateTime, default=datetime.now)


class AlertLog(Base):
    """预警触发日志表"""
    __tablename__ = 'alert_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, nullable=False)  # 预警配置 ID
    alert_type = Column(String(50), nullable=False)  # 预警类型：price, technical
    stock_code = Column(String(20), nullable=False)  # 股票代码
    stock_name = Column(String(50))  # 股票名称
    trigger_value = Column(Float)  # 触发时的值
    message = Column(Text)  # 预警消息
    notified = Column(Boolean, default=False)  # 是否已通知
    created_at = Column(DateTime, default=datetime.now)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url):
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def add_holding(self, stock_code, stock_name, shares, avg_cost, notes=''):
        """添加持仓记录"""
        session = self.get_session()
        try:
            holding = StockHolding(
                stock_code=stock_code,
                stock_name=stock_name,
                shares=shares,
                avg_cost=avg_cost,
                notes=notes
            )
            session.add(holding)
            session.commit()
            return holding.id
        finally:
            session.close()
    
    def update_holding(self, holding_id, **kwargs):
        """更新持仓记录"""
        session = self.get_session()
        try:
            holding = session.query(StockHolding).filter_by(id=holding_id).first()
            if holding:
                for key, value in kwargs.items():
                    if hasattr(holding, key):
                        setattr(holding, key, value)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def delete_holding(self, holding_id):
        """删除持仓记录"""
        session = self.get_session()
        try:
            holding = session.query(StockHolding).filter_by(id=holding_id).first()
            if holding:
                session.delete(holding)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_holdings(self):
        """获取所有持仓"""
        session = self.get_session()
        try:
            return session.query(StockHolding).all()
        finally:
            session.close()
    
    def get_holding_by_code(self, stock_code):
        """获取指定股票的持仓"""
        session = self.get_session()
        try:
            return session.query(StockHolding).filter_by(stock_code=stock_code).all()
        finally:
            session.close()
    
    def add_price_alert(self, stock_code, stock_name, alert_type, threshold_value):
        """添加价格预警"""
        session = self.get_session()
        try:
            alert = PriceAlert(
                stock_code=stock_code,
                stock_name=stock_name,
                alert_type=alert_type,
                threshold_value=threshold_value
            )
            session.add(alert)
            session.commit()
            return alert.id
        finally:
            session.close()
    
    def add_technical_alert(self, stock_code, stock_name, indicator, condition, threshold_value):
        """添加技术指标预警"""
        session = self.get_session()
        try:
            alert = TechnicalAlert(
                stock_code=stock_code,
                stock_name=stock_name,
                indicator=indicator,
                condition=condition,
                threshold_value=threshold_value
            )
            session.add(alert)
            session.commit()
            return alert.id
        finally:
            session.close()
    
    def get_active_price_alerts(self):
        """获取所有激活的价格预警"""
        session = self.get_session()
        try:
            return session.query(PriceAlert).filter_by(is_active=True).all()
        finally:
            session.close()
    
    def get_active_technical_alerts(self):
        """获取所有激活的技术指标预警"""
        session = self.get_session()
        try:
            return session.query(TechnicalAlert).filter_by(is_active=True).all()
        finally:
            session.close()
    
    def toggle_alert(self, alert_id, alert_type='price'):
        """切换预警状态"""
        session = self.get_session()
        try:
            if alert_type == 'price':
                alert = session.query(PriceAlert).filter_by(id=alert_id).first()
            else:
                alert = session.query(TechnicalAlert).filter_by(id=alert_id).first()
            
            if alert:
                alert.is_active = not alert.is_active
                session.commit()
                return alert.is_active
            return None
        finally:
            session.close()
    
    def delete_alert(self, alert_id, alert_type='price'):
        """删除预警配置"""
        session = self.get_session()
        try:
            if alert_type == 'price':
                alert = session.query(PriceAlert).filter_by(id=alert_id).first()
            else:
                alert = session.query(TechnicalAlert).filter_by(id=alert_id).first()
            
            if alert:
                session.delete(alert)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def log_alert(self, alert_id, alert_type, stock_code, stock_name, trigger_value, message):
        """记录预警触发日志"""
        session = self.get_session()
        try:
            log = AlertLog(
                alert_id=alert_id,
                alert_type=alert_type,
                stock_code=stock_code,
                stock_name=stock_name,
                trigger_value=trigger_value,
                message=message
            )
            session.add(log)
            
            # 更新预警配置的触发时间和次数
            if alert_type == 'price':
                alert = session.query(PriceAlert).filter_by(id=alert_id).first()
            else:
                alert = session.query(TechnicalAlert).filter_by(id=alert_id).first()
            
            if alert:
                alert.last_triggered = datetime.now()
                alert.trigger_count += 1
            
            session.commit()
            return log.id
        finally:
            session.close()
    
    def get_alert_logs(self, limit=100):
        """获取预警日志"""
        session = self.get_session()
        try:
            return session.query(AlertLog).order_by(AlertLog.created_at.desc()).limit(limit).all()
        finally:
            session.close()
