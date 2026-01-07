import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
from config import IMAGE_SIZE, MEAN, STD, DEVICE


def load_and_preprocess_image(image_path):
    """
    加载并预处理图片
    :param image_path: 图片路径
    :return: 预处理后的tensor（1, 3, 224, 224）
    """
    try:
        # 用PIL加载图片（支持更多格式）
        img = Image.open(image_path).convert("RGB")

        # 定义预处理流程
        preprocess = transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.CenterCrop(IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ])

        # 预处理并添加batch维度
        img_tensor = preprocess(img).unsqueeze(0).to(DEVICE)
        return img_tensor

    except Exception as e:
        print(f"图片预处理失败 {image_path}: {e}")
        return None


def get_feature_extractor():
    """
    获取特征提取模型（ResNet50，去掉最后一层）
    :return: 特征提取模型
    """
    from torchvision import models

    # 加载预训练的ResNet50
    model = models.resnet50(pretrained=True).to(DEVICE)

    # 去掉最后一层全连接层，保留特征提取部分
    feature_extractor = torch.nn.Sequential(*list(model.children())[:-1])

    # 设置为评估模式
    feature_extractor.eval()

    return feature_extractor


def extract_image_feature(image_path, feature_extractor):
    """
    提取单张图片的特征
    :param image_path: 图片路径
    :param feature_extractor: 特征提取模型
    :return: 归一化后的特征向量（numpy数组）
    """
    img_tensor = load_and_preprocess_image(image_path)
    if img_tensor is None:
        return None

    # 禁用梯度计算
    with torch.no_grad():
        feature = feature_extractor(img_tensor)

    # 展平并归一化
    feature_np = feature.cpu().numpy().flatten()
    feature_np = feature_np / np.linalg.norm(feature_np)  # 归一化

    return feature_np


def calculate_cosine_similarity(feature1, feature2):
    """
    计算两个特征向量的余弦相似度
    :param feature1: 特征向量1
    :param feature2: 特征向量2
    :return: 相似度值（0-1）
    """
    if feature1 is None or feature2 is None:
        return 0.0

    # 计算余弦相似度
    similarity = np.dot(feature1, feature2) / (np.linalg.norm(feature1) * np.linalg.norm(feature2))
    return max(0.0, min(1.0, similarity))  # 限制在0-1之间