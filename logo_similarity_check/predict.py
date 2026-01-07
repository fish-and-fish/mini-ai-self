import os
import pickle
from tqdm import tqdm
from config import PREVIEW_DIR, FEATURES_PATH, SIMILARITY_THRESHOLD
from utils import get_feature_extractor, extract_image_feature, calculate_cosine_similarity


def predict():
    """
    检查预览图与对应Logo的相似度
    """
    # 加载预提取的Logo特征
    if not os.path.exists(FEATURES_PATH):
        print(f"错误：未找到Logo特征文件，请先运行 train.py")
        return

    with open(FEATURES_PATH, "rb") as f:
        logo_features = pickle.load(f)

    # 获取特征提取模型
    feature_extractor = get_feature_extractor()

    # 结果统计
    total_previews = 0
    similar_count = 0
    dissimilar_count = 0
    error_count = 0

    print(f"\n开始检查预览图相似度（阈值: {SIMILARITY_THRESHOLD}）")
    print("-" * 80)

    # 遍历所有预览图文件夹
    preview_folders = [f for f in os.listdir(PREVIEW_DIR) if os.path.isdir(os.path.join(PREVIEW_DIR, f))]

    for preview_folder in tqdm(preview_folders, desc="检查预览图"):
        logo_id = preview_folder
        preview_folder_path = os.path.join(PREVIEW_DIR, preview_folder)

        # 检查Logo特征是否存在
        if logo_id not in logo_features:
            print(f"\n跳过 {logo_id}: 未找到对应的Logo特征")
            continue

        logo_feature = logo_features[logo_id]

        # 遍历该Logo下的所有预览图
        preview_images = [f for f in os.listdir(preview_folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        for preview_img_name in preview_images:
            total_previews += 1
            preview_img_path = os.path.join(preview_folder_path, preview_img_name)

            # 提取预览图特征
            preview_feature = extract_image_feature(preview_img_path, feature_extractor)
            if preview_feature is None:
                error_count += 1
                print(f"\n{logo_id}/{preview_img_name}: 预览图处理失败")
                continue

            # 计算相似度
            similarity = calculate_cosine_similarity(logo_feature, preview_feature)
            is_similar = similarity >= SIMILARITY_THRESHOLD

            # 统计结果
            if is_similar:
                similar_count += 1
            else:
                dissimilar_count += 1

            # 打印结果（相似度低于阈值的重点标注）
            status = "✅ 相似" if is_similar else "❌ 不相似"
            print(f"\n{logo_id}/{preview_img_name}: 相似度 = {similarity:.4f} | {status}")

    # 打印汇总结果
    print("-" * 80)
    print(f"汇总结果：")
    print(f"总预览图数: {total_previews}")
    print(f"相似: {similar_count}")
    print(f"不相似: {dissimilar_count}")
    print(f"处理失败: {error_count}")
    print(f"不相似率: {dissimilar_count / total_previews * 100:.2f}%" if total_previews > 0 else "无数据")


if __name__ == "__main__":
    predict()