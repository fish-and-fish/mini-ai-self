import os
import pickle
from tqdm import tqdm
from config import LOGO_DIR, FEATURES_PATH, DEVICE
from utils import get_feature_extractor, extract_image_feature


def train():
    """
    提取所有Logo的特征并保存
    """
    # 获取特征提取模型
    feature_extractor = get_feature_extractor()
    print(f"使用设备: {DEVICE}")
    print("开始提取Logo特征...")

    # 存储Logo特征 {logo_id: feature_vector}
    logo_features = {}

    # 遍历所有Logo文件夹
    logo_folders = [f for f in os.listdir(LOGO_DIR) if os.path.isdir(os.path.join(LOGO_DIR, f))]

    for logo_folder in tqdm(logo_folders, desc="提取Logo特征"):
        logo_id = logo_folder
        logo_folder_path = os.path.join(LOGO_DIR, logo_folder)

        # 找Logo原图（默认original.jpg）
        logo_image_path = None
        for file in os.listdir(logo_folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                logo_image_path = os.path.join(logo_folder_path, file)
                break

        # 提取特征
        feature = extract_image_feature(logo_image_path, feature_extractor)
        if feature is not None:
            logo_features[logo_id] = feature
        else:
            print(f"跳过 {logo_id}: 特征提取失败")

    # 保存特征到文件
    with open(FEATURES_PATH, "wb") as f:
        pickle.dump(logo_features, f)

    print(f"\n训练完成！共提取 {len(logo_features)} 个Logo特征")
    print(f"特征文件保存至: {FEATURES_PATH}")


if __name__ == "__main__":
    train()