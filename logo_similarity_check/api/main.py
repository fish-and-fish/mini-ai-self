import io
import base64
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from PIL import Image

# 导入原有工具函数和配置
import sys

sys.path.append("..")
from logo_similarity_check.utils import get_feature_extractor, extract_image_feature, calculate_cosine_similarity
from logo_similarity_check.config import SIMILARITY_THRESHOLD, DEVICE

# 初始化FastAPI应用
app = FastAPI(
    title="Logo相似度检测API（Base64版）",
    description="接收Base64编码的图片，返回相似度结果",
    version="1.0.0"
)


# 定义请求体模型
class SimilarityRequest(BaseModel):
    original_base64: str = Field(..., description="Logo原图的Base64编码字符串（不含data:image前缀）")
    compare_base64: str = Field(..., description="待对比图的Base64编码字符串（不含data:image前缀）")


# 全局加载特征提取模型
feature_extractor = None


@app.on_event("startup")
async def startup_event():
    """服务启动时加载特征提取模型"""
    global feature_extractor
    feature_extractor = get_feature_extractor()
    print(f"✅ API服务启动完成，使用设备：{DEVICE}")


def base64_to_image(base64_str):
    """将Base64字符串转为PIL Image对象"""
    try:
        # 解码Base64字符串
        img_bytes = base64.b64decode(base64_str)
        # 转为图片对象
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        return img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Base64解码失败：{str(e)}")


@app.post("/api/check_similarity_base64", summary="检测两张Base64图片的相似度")
async def check_similarity_base64(request: SimilarityRequest):
    """
    接收两张图片的Base64字符串，返回相似度结果
    请求体示例：
    {
        "original_base64": "xxxxxxx",  // 原图Base64编码
        "compare_base64": "yyyyyyy"    // 对比图Base64编码
    }
    返回格式：
    {
        "similarity": 0.9234,        // 余弦相似度（0-1）
        "is_similar": true,          // 是否相似（基于阈值）
        "threshold": 0.85,           // 相似度阈值
        "message": "图片相似度符合要求"  // 结果说明
    }
    """
    try:
        # 1. 将Base64转为图片对象
        original_img = base64_to_image(request.original_base64)
        compare_img = base64_to_image(request.compare_base64)

        # 2. 生成临时文件（复用原有特征提取函数）
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp_original:
            original_img.save(tmp_original.name)
            original_feature = extract_image_feature(tmp_original.name, feature_extractor)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp_compare:
            compare_img.save(tmp_compare.name)
            compare_feature = extract_image_feature(tmp_compare.name, feature_extractor)

        # 3. 计算相似度
        similarity = calculate_cosine_similarity(original_feature, compare_feature)
        is_similar = similarity >= SIMILARITY_THRESHOLD
        is_similar_py = bool(is_similar)

        # 4. 构造返回结果
        result = {
            "similarity": round(float(similarity), 4),
            "is_similar": is_similar_py,
            "threshold": SIMILARITY_THRESHOLD,
            "message": "图片相似度符合要求" if is_similar else "图片相似度不达标，可能上传错误"
        }
        print(f"请求处理完成，result：{result}")

        return JSONResponse(content=result)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败：{str(e)}")


@app.get("/health", summary="健康检查接口")
async def health_check():
    """用于验证服务是否正常运行"""
    return {
        "status": "healthy",
        "device": str(DEVICE),
        "threshold": SIMILARITY_THRESHOLD
    }