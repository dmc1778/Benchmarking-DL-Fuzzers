import torch
results = dict()
input_tensor = torch.rand([1, 64, 540, 540], dtype=torch.float32)
input = input_tensor.clone()
scale_factor = 2
try:
  results["res_1"] = torch.nn.functional.interpolate(input, scale_factor=scale_factor, )
except Exception as e:
  results["err_1"] = "ERROR:"+str(e)
try:
  results["res_2"] = torch.sub(input_tensor.clone(),alpha=scale_factor,)
except Exception as e:
  results["err_2"] = "ERROR:"+str(e)

print(results)
