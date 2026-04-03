"""
深度学习因子挖掘器

使用LSTM、Transformer、GNN等深度学习模型挖掘因子
"""

from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)


class LSTMFactorModel(nn.Module):
    """LSTM因子挖掘模型"""
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, dropout: float = 0.2):
        super(LSTMFactorModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


class TransformerFactorModel(nn.Module):
    """Transformer因子挖掘模型"""
    
    def __init__(self, input_size: int, d_model: int = 128, nhead: int = 8, 
                 num_encoder_layers: int = 3, dim_feedforward: int = 512, dropout: float = 0.1):
        super(TransformerFactorModel, self).__init__()
        
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_encoder_layers)
        
        self.fc = nn.Linear(d_model, 1)
        
    def forward(self, x):
        x = self.input_projection(x)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)
        x = self.fc(x[:, -1, :])
        return x


class PositionalEncoding(nn.Module):
    """位置编码"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        x = x + self.pe[:x.size(1)]
        return self.dropout(x)


class TimeSeriesDataset(Dataset):
    """时序数据集"""
    
    def __init__(self, data: np.ndarray, target: np.ndarray, lookback_window: int = 20):
        self.data = data
        self.target = target
        self.lookback_window = lookback_window
        
    def __len__(self):
        return len(self.data) - self.lookback_window
        
    def __getitem__(self, idx):
        x = self.data[idx:idx+self.lookback_window]
        y = self.target[idx+self.lookback_window]
        return torch.FloatTensor(x), torch.FloatTensor([y])


class DeepLearningFactorMiner:
    """深度学习因子挖掘器
    
    使用LSTM、Transformer、GNN等深度学习模型挖掘因子
    """
    
    def __init__(self, config: Dict):
        """
        初始化深度学习挖掘器
        
        Args:
            config: 配置字典
                - model_type: 'lstm' | 'transformer' | 'gnn'
                - hidden_size: 隐藏层大小
                - num_layers: 层数
                - dropout: Dropout率
                - learning_rate: 学习率
                - batch_size: 批次大小
                - epochs: 训练轮数
                - lookback_window: 回看窗口
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch未安装,请运行: pip install torch")
            
        self.config = config
        self.model_type = config.get('model_type', 'lstm')
        self.hidden_size = config.get('hidden_size', 128)
        self.num_layers = config.get('num_layers', 2)
        self.dropout = config.get('dropout', 0.2)
        self.learning_rate = config.get('learning_rate', 0.001)
        self.batch_size = config.get('batch_size', 64)
        self.epochs = config.get('epochs', 100)
        self.lookback_window = config.get('lookback_window', 20)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.model = None
        
        logger.info(f"深度学习挖掘器初始化完成,模型类型: {self.model_type}, 设备: {self.device}")
        
    def mine_factors(self, data: pd.DataFrame, target: pd.Series) -> List[Dict]:
        """
        挖掘因子
        
        Args:
            data: 原始特征数据
            target: 目标收益率
            
        Returns:
            挖掘的因子列表
        """
        logger.info(f"开始{self.model_type}因子挖掘...")
        
        if self.model_type == 'lstm':
            factors = self._mine_lstm_factors(data, target)
        elif self.model_type == 'transformer':
            factors = self._mine_transformer_factors(data, target)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
            
        logger.info(f"{self.model_type}挖掘完成,发现{len(factors)}个因子")
        return factors
    
    def _mine_lstm_factors(self, data: pd.DataFrame, target: pd.Series) -> List[Dict]:
        """
        使用LSTM挖掘时序因子
        
        Args:
            data: 时序特征数据
            target: 目标收益率
            
        Returns:
            LSTM挖掘的因子列表
        """
        X = data.values
        y = target.values
        
        dataset = TimeSeriesDataset(X, y, self.lookback_window)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        input_size = X.shape[1]
        self.model = LSTMFactorModel(input_size, self.hidden_size, self.num_layers, self.dropout)
        self.model.to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                avg_loss = total_loss / len(dataloader)
                logger.info(f"Epoch [{epoch+1}/{self.epochs}], Loss: {avg_loss:.6f}")
        
        factor_values = self._extract_factor_values(data)
        
        factor = {
            'factor_id': f"AI_DL_LSTM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'factor_name': f"LSTM_Factor_{self.lookback_window}d",
            'method': 'deep_learning',
            'model_type': 'lstm',
            'expression': f"lstm_attention(features, window={self.lookback_window})",
            'factor_values': factor_values,
            'complexity': self._calculate_complexity(),
            'created_at': datetime.now().isoformat()
        }
        
        return [factor]
    
    def _mine_transformer_factors(self, data: pd.DataFrame, target: pd.Series) -> List[Dict]:
        """
        使用Transformer挖掘注意力因子
        
        Args:
            data: 特征数据
            target: 目标收益率
            
        Returns:
            Transformer挖掘的因子列表
        """
        X = data.values
        y = target.values
        
        dataset = TimeSeriesDataset(X, y, self.lookback_window)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        input_size = X.shape[1]
        self.model = TransformerFactorModel(input_size, self.hidden_size)
        self.model.to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            for batch_x, batch_y in dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                avg_loss = total_loss / len(dataloader)
                logger.info(f"Epoch [{epoch+1}/{self.epochs}], Loss: {avg_loss:.6f}")
        
        factor_values = self._extract_factor_values(data)
        
        factor = {
            'factor_id': f"AI_DL_TRANS_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'factor_name': f"Transformer_Factor_{self.lookback_window}d",
            'method': 'deep_learning',
            'model_type': 'transformer',
            'expression': f"transformer_attention(features, window={self.lookback_window})",
            'factor_values': factor_values,
            'complexity': self._calculate_complexity(),
            'created_at': datetime.now().isoformat()
        }
        
        return [factor]
    
    def _extract_factor_values(self, data: pd.DataFrame) -> np.ndarray:
        """
        提取因子值
        
        Args:
            data: 原始数据
            
        Returns:
            因子值数组
        """
        self.model.eval()
        factor_values = []
        
        with torch.no_grad():
            for i in range(len(data) - self.lookback_window):
                x = data.iloc[i:i+self.lookback_window].values
                x = torch.FloatTensor(x).unsqueeze(0).to(self.device)
                output = self.model(x)
                factor_values.append(output.item())
        
        return np.array(factor_values)
    
    def _calculate_complexity(self) -> int:
        """
        计算模型复杂度
        
        Returns:
            复杂度评分
        """
        if self.model is None:
            return 0
        
        num_params = sum(p.numel() for p in self.model.parameters())
        complexity = int(num_params / 1000)
        
        return min(complexity, 100)
