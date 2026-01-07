import base64
import requests
import argparse

# API地址
API_URL = "http://localhost:8091/api/check_similarity_base64"
HEALTH_URL = "http://localhost:8091/health"

def image_to_base64(image_path):
    """将本地图片转为Base64字符串（不含data:image前缀）"""
    try:
        with open(image_path, "rb") as f:
            # 读取图片字节并编码为Base64
            base64_str = base64.b64encode(f.read()).decode("utf-8")
        return base64_str
    except Exception as e:
        print(f"❌ 读取图片失败 {image_path}：{e}")
        return None

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get(HEALTH_URL)
        if response.status_code == 200:
            print("✅ 健康检查通过：")
            print(response.json())
            return True
        else:
            print(f"❌ 健康检查失败，状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查失败：{e}")
        return False

def call_similarity_api(original_path, compare_path):
    """调用相似度检测API"""
    # 1. 先做健康检查
    if not test_health_check():
        return

    # 2. 转换图片为Base64
    print("\n📸 转换图片为Base64...")
    original_base64 = image_to_base64(original_path)
    compare_base64 = image_to_base64(compare_path)
    if not original_base64 or not compare_base64:
        return

    # 3. 构造请求体
    request_data = {
        "original_base64": original_base64,
        "compare_base64": compare_base64
    }

    # 4. 调用API
    print("🚀 调用相似度检测API...")
    try:
        response = requests.post(
            API_URL,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # 5. 处理响应
        if response.status_code == 200:
            result = response.json()
            print("\n✅ API返回结果：")
            print(f"   相似度：{result['similarity']}")
            print(f"   是否相似：{result['is_similar']}")
            print(f"   阈值：{result['threshold']}")
            print(f"   提示：{result['message']}")
        else:
            print(f"❌ API调用失败，状态码：{response.status_code}")
            print(f"   错误信息：{response.text}")
    except Exception as e:
        print(f"❌ API调用异常：{e}")

if __name__ == "__main__":
    # 解析命令行参数
    # parser = argparse.ArgumentParser(description="测试Logo相似度检测API（Base64版）")
    # parser.add_argument("--original", required=True, help="Logo原图路径，如：/Users/linglong/Downloads/test/image/1.jpg")
    # parser.add_argument("--compare", required=True, help="对比图路径，如：/Users/linglong/Downloads/test/image/2.jpg")
    # args = parser.parse_args()

    # 调用API
    # call_similarity_api(args.original, args.compare)
    call_similarity_api("/Users/linglong/Downloads/test/image/1.jpg", "/Users/linglong/Downloads/test/image/1.jpg")