from transformers import RobertaTokenizer, RobertaModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
model = RobertaModel.from_pretrained("microsoft/codebert-base")

def get_code_embedding(code):
    inputs = tokenizer(code, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].numpy()

def calculate_similarity(log1, log2):
    embedding1 = get_code_embedding(log1)
    embedding2 = get_code_embedding(log2)
    similarity = cosine_similarity(embedding1, embedding2)
    return similarity[0][0]