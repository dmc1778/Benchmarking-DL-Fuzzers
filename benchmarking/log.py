import torch
results = dict()
size_0 = 24
size_1 = 24
size = [size_0,size_1,]
try:
  results["res_1"] = torch.zeros(*size, )
except Exception as e:
  results["err_1"] = "ERROR:"+str(e)
try:
  results["res_2"] = torch.ones(size,)
except Exception as e:
  results["err_2"] = "ERROR:"+str(e)

print(results)
