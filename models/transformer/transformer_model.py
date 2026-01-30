import torch
import torch.nn as nn


class GameplayTransformer(nn.Module):
    """Transformer模型用于游戏动作预测
    Transformer-based model for gameplay action prediction"""
    
    def __init__(self, input_size, num_heads, hidden_size, num_layers, output_size):
        """
        Transformer模型初始化
        Transformer-based model for gameplay action prediction.

        输入格式 Expected input:
          - (batch, input_size)            -> 单时间步输入 / treated as single-timestep sequence
          - (batch, seq_len, input_size)   -> 序列输入 / sequence input

        输出格式 Output:
          - (batch, output_size) 动作概率 / action probabilities
        """
        super().__init__()

        self.embedding = nn.Linear(input_size, hidden_size)  # 特征嵌入层 (Feature embedding)

        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=hidden_size * 4,
            batch_first=True,  # 重要：使输入形状为 (batch, seq, hidden) / IMPORTANT: makes input (batch, seq, hidden)
        )
        self.transformer_encoder = nn.TransformerEncoder(
            self.encoder_layer,
            num_layers=num_layers,  # Transformer编码器层数
        )

        self.fc = nn.Linear(hidden_size, output_size)  # 输出层 (Output layer)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播 / Forward pass
        
        x:
          - (B, F) 或 (B, T, F) - 批大小、特征数或时间步
        返回 returns:
          - (B, C) - 批大小、动作类别
        """
        if x.dim() == 2:
            # (B, F) -> (B, 1, F) 扩展时间维度 / Expand time dimension
            x = x.unsqueeze(1)
        elif x.dim() != 3:
            raise ValueError(f"Expected input of shape (B,F) or (B,T,F), got {tuple(x.shape)}")

        x = self.embedding(x)                  # (B, T, H) 特征嵌入
        x = self.transformer_encoder(x)        # (B, T, H) Transformer编码
        x = x.mean(dim=1)                      # 时间维度池化 / pool over T -> (B, H)
        logits = self.fc(x)                    # (B, C) 动作类别预测
        return logits
