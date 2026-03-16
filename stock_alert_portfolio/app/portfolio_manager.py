"""
投资组合管理模块
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager, StockHolding
from app.data_service import StockDataService


class PortfolioManager:
    """投资组合管理器"""
    
    def __init__(self, db_manager: DatabaseManager, data_service: StockDataService):
        self.db = db_manager
        self.data_service = data_service
    
    def get_portfolio_summary(self) -> Dict:
        """
        获取投资组合摘要
        
        Returns:
            包含持仓统计的字典
        """
        holdings = self.db.get_holdings()
        
        if not holdings:
            return {
                'total_holdings': 0,
                'total_invested': 0,
                'total_market_value': 0,
                'total_profit_loss': 0,
                'profit_loss_rate': 0,
                'positions': []
            }
        
        total_invested = 0
        total_market_value = 0
        positions = []
        
        for holding in holdings:
            current_price = self.data_service.get_current_price(holding.stock_code)
            
            if current_price is None:
                continue
            
            market_value = holding.shares * current_price
            invested = holding.shares * holding.avg_cost
            profit_loss = market_value - invested
            profit_loss_rate = (profit_loss / invested * 100) if invested > 0 else 0
            
            total_invested += invested
            total_market_value += market_value
            
            positions.append({
                'id': holding.id,
                'stock_code': holding.stock_code,
                'stock_name': holding.stock_name or self._get_stock_name(holding.stock_code),
                'shares': holding.shares,
                'avg_cost': holding.avg_cost,
                'current_price': current_price,
                'market_value': market_value,
                'invested': invested,
                'profit_loss': profit_loss,
                'profit_loss_rate': profit_loss_rate,
                'buy_date': holding.buy_date.strftime('%Y-%m-%d') if holding.buy_date else '',
                'notes': holding.notes
            })
        
        total_profit_loss = total_market_value - total_invested
        profit_loss_rate = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'total_holdings': len(positions),
            'total_invested': total_invested,
            'total_market_value': total_market_value,
            'total_profit_loss': total_profit_loss,
            'profit_loss_rate': profit_loss_rate,
            'positions': positions
        }
    
    def _get_stock_name(self, stock_code: str) -> str:
        """获取股票名称"""
        info = self.data_service.get_stock_info(stock_code)
        return info.get('name', stock_code)
    
    def add_position(self, stock_code: str, stock_name: str, shares: float, 
                     avg_cost: float, notes: str = '') -> int:
        """
        添加持仓
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            shares: 持仓数量
            avg_cost: 平均成本
            notes: 备注
            
        Returns:
            持仓 ID
        """
        return self.db.add_holding(stock_code, stock_name, shares, avg_cost, notes)
    
    def update_position(self, holding_id: int, **kwargs) -> bool:
        """更新持仓"""
        return self.db.update_holding(holding_id, **kwargs)
    
    def delete_position(self, holding_id: int) -> bool:
        """删除持仓"""
        return self.db.delete_holding(holding_id)
    
    def get_portfolio_analysis(self) -> Dict:
        """
        获取投资组合分析
        
        Returns:
            包含分析结果的字典
        """
        summary = self.get_portfolio_summary()
        
        if summary['total_holdings'] == 0:
            return {
                'diversification': {},
                'risk_metrics': {},
                'performance': {}
            }
        
        positions = summary['positions']
        
        # 持仓分布分析
        total_value = summary['total_market_value']
        diversification = {
            'position_weights': [
                {
                    'stock_code': p['stock_code'],
                    'weight': (p['market_value'] / total_value * 100) if total_value > 0 else 0
                }
                for p in positions
            ],
            'largest_position': max(positions, key=lambda x: x['market_value'])['stock_code'] if positions else None,
            'concentration_rate': max(
                [(p['market_value'] / total_value * 100) for p in positions]
            ) if total_value > 0 else 0
        }
        
        # 风险指标
        profitable = [p for p in positions if p['profit_loss'] > 0]
        losing = [p for p in positions if p['profit_loss'] <= 0]
        
        risk_metrics = {
            'profitable_positions': len(profitable),
            'losing_positions': len(losing),
            'win_rate': (len(profitable) / len(positions) * 100) if positions else 0,
            'best_performer': max(positions, key=lambda x: x['profit_loss_rate']) if positions else None,
            'worst_performer': min(positions, key=lambda x: x['profit_loss_rate']) if positions else None
        }
        
        # 业绩指标
        performance = {
            'total_return': summary['profit_loss_rate'],
            'avg_position_return': sum([p['profit_loss_rate'] for p in positions]) / len(positions) if positions else 0,
            'total_profit': sum([p['profit_loss'] for p in profitable]) if profitable else 0,
            'total_loss': abs(sum([p['profit_loss'] for p in losing])) if losing else 0,
            'profit_factor': (
                sum([p['profit_loss'] for p in profitable]) / 
                abs(sum([p['profit_loss'] for p in losing]))
            ) if losing and sum([p['profit_loss'] for p in losing]) != 0 else float('inf')
        }
        
        return {
            'diversification': diversification,
            'risk_metrics': risk_metrics,
            'performance': performance
        }
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        导出持仓到 DataFrame
        
        Returns:
            持仓 DataFrame
        """
        summary = self.get_portfolio_summary()
        
        if not summary['positions']:
            return pd.DataFrame()
        
        df = pd.DataFrame(summary['positions'])
        return df
    
    def get_portfolio_chart_data(self) -> Dict:
        """
        获取用于图表的数据
        
        Returns:
            包含图表数据的字典
        """
        summary = self.get_portfolio_summary()
        
        if summary['total_holdings'] == 0:
            return {}
        
        # 持仓分布数据 (用于饼图)
        pie_data = {
            'labels': [f"{p['stock_code']}" for p in summary['positions']],
            'values': [p['market_value'] for p in summary['positions']],
            'names': [p['stock_name'] for p in summary['positions']]
        }
        
        # 盈亏数据 (用于柱状图)
        bar_data = {
            'labels': [f"{p['stock_code']}" for p in summary['positions']],
            'profit_loss': [p['profit_loss'] for p in summary['positions']],
            'colors': ['green' if p['profit_loss'] > 0 else 'red' for p in summary['positions']]
        }
        
        # 收益率数据 (用于热力图)
        heatmap_data = {
            'labels': [f"{p['stock_code']}" for p in summary['positions']],
            'returns': [p['profit_loss_rate'] for p in summary['positions']]
        }
        
        return {
            'pie': pie_data,
            'bar': bar_data,
            'heatmap': heatmap_data
        }
