import torch
import torch.nn as nn

class TradingModel(nn.Module):
    def __init__(self, input_size=15, hidden=128, seq_len=60, dropout=0.3):
        super(TradingModel, self).__init__()
        # LSTM layer — learns from 60-step sequences
        self.lstm = nn.LSTM(input_size, hidden, batch_first=True, num_layers=2,
                            dropout=dropout)
        
        # Classification head with regularization
        self.head = nn.Sequential(
            nn.Linear(hidden, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 2)   # UP / DOWN logits
        )

    def forward(self, x):          # x: (batch, 60, 15)
        # out: (batch, seq_len, hidden)
        out, _ = self.lstm(x)
        # return the head's output for the last timestep
        return self.head(out[:, -1, :])
