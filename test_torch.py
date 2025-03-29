import numpy as np
import torch
"""
---- returncode=1 ----
stdout> 
stderr> Traceback (most recent call last):
  File "/tmp/tmp1725779414.9681098.py", line 5, in <module>
    x1.layout = torch.strided
AttributeError: attribute 'layout' of 'torch._C._TensorBase' objects is not writable


"""

x1 = torch.rand(2, 3)
x1.layout = torch.strided
