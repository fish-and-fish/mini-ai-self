import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGO_DIR = os.path.join(DATA_DIR, "logos")
PREVIEW_DIR = os.path.join(DATA_DIR, "previews")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# 确保目录存在
os.makedirs(MODEL_DIR, exist_ok=True)

# 图片预处理参数
IMAGE_SIZE = (224, 224)  # ResNet输入尺寸
MEAN = [0.485, 0.456, 0.406]  # ImageNet均值
STD = [0.229, 0.224, 0.225]   # ImageNet标准差

# 相似度阈值（可根据实际数据调整）
SIMILARITY_THRESHOLD = 0.85

# 特征保存路径
FEATURES_PATH = os.path.join(MODEL_DIR, "logo_features.pkl")

# 设备配置（自动使用GPU）
import torch
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")