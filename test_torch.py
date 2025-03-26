import numpy as np
import torch
"""
---- returncode=1 ----
stdout> 
stderr> Traceback (most recent call last):
  File "/tmp/tmp1725782189.476746.py", line 6, in <module>
    z = torch.cat(tensors=[x, y, z])
NameError: name 'z' is not defined


"""

x = torch.randn(2, 3)
y = torch.randn(2, 3)
z = torch.cat(tensors=[x, y, z])
z.size()
