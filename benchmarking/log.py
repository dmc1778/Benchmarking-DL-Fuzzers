import torch
results = dict()
input_tensor = torch.rand([3, 4], dtype=torch.float32)
input = input_tensor.clone()
dim = -1
try:
  results["res_1"] = torch.sort(input, dim=dim, )
except Exception as e:
  results["err_1"] = "ERROR:"+str(e)
try:
  results["res_2"] = torch.argsort(input_tensor.clone(),dim=dim,)
except Exception as e:
  results["err_2"] = "ERROR:"+str(e)

print(results)
