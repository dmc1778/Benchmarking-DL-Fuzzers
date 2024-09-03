import torch
param = torch.rand(16, 32)
optimizer = torch.optim.SparseAdam(param)