import tkinter as tk
from tkinter import ttk, messagebox
import base64
import requests
import os
import shutil
from datetime import datetime
import time

# -------------------------- 配置远程API地址（修改1：端口改为8901） --------------------------
API_URL = "http://47.245.150.252:8901/api/check_similarity_base64"
# API_URL = "http://127.0.0.1:8901/api/check_similarity_base64"
# 移除HEALTH_URL配置（修改2：删除健康检查相关）

# -------------------------- 全局变量 --------------------------
# 支持的图片格式
SUPPORT_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
# 相似阈值（和API保持一致）
SIMILARITY_THRESHOLD = 0.85


# -------------------------- 核心功能函数 --------------------------
def log_print(content):
    """日志打印（带时间戳，输出到文本框）"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_text = f"{timestamp} {content}\n"
    text_log.insert(tk.END, log_text)
    text_log.see(tk.END)  # 自动滚动到最新日志
    root.update_idletasks()  # 实时刷新界面


def get_all_images_deep(dir_path):
    """修改3：深度遍历目录下所有图片（包括子文件夹）"""
    image_paths = []
    for root_dir, sub_dirs, files in os.walk(dir_path):
        for file in files:
            if file.lower().endswith(SUPPORT_FORMATS):
                full_path = os.path.join(root_dir, file)
                image_paths.append(full_path)
    return image_paths


def image_to_base64(image_path):
    """将本地图片转为Base64字符串"""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"文件不存在：{image_path}")
        with open(image_path, "rb") as f:
            base64_str = base64.b64encode(f.read()).decode("utf-8")
        return base64_str
    except Exception as e:
        log_print(f"【错误】图片转Base64失败：{image_path} - {str(e)}")
        return None


def call_similarity_api(original_base64, compare_base64):
    """调用API获取相似度结果"""
    try:
        request_data = {
            "original_base64": original_base64,
            "compare_base64": compare_base64
        }
        start_time = time.time()
        response = requests.post(
            API_URL,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        cost_time = round(time.time() - start_time, 2)
        if response.status_code == 200:
            result = response.json()
            return {
                "similarity": result["similarity"],
                "is_similar": result["is_similar"],
                "cost_time": cost_time
            }
        else:
            log_print(f"【错误】模型比对失败，状态码：{response.status_code}，响应：{response.text}")
            return None
    except Exception as e:
        log_print(f"【错误】模型比对异常：{str(e)}")
        return None


def batch_compare():
    """批量比对主逻辑"""
    # 获取输入路径
    path_a = entry_path_a.get().strip()
    path_b = entry_path_b.get().strip()

    # 输入校验
    if not path_a or not path_b:
        messagebox.warning("警告", "请输入完整的图库路径！")
        return
    if not os.path.isdir(path_a):
        messagebox.showerror("错误", f"路径A不是有效目录：{path_a}")
        return
    if not os.path.isdir(path_b):
        messagebox.showerror("错误", f"路径B不是有效目录：{path_b}")
        return

    # 移除健康检查（修改2：删除check_api_health调用）
    log_print("【初始化】开始批量比对，跳过API健康检查")

    # 1. 创建时间命名的差异目录X
    dir_x_name = f"差异图片_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dir_x = os.path.join(path_a, dir_x_name)
    os.makedirs(dir_x, exist_ok=True)
    log_print(f"【初始化】创建差异目录：{dir_x}")

    # 2. 深度遍历路径A的所有图片（修改3：使用深度遍历函数）
    path_a_images = get_all_images_deep(path_a)
    if not path_a_images:
        log_print(f"【警告】路径A下未找到支持的图片（{SUPPORT_FORMATS}）")
        return
    log_print(f"【初始化】路径A（含子文件夹）找到{len(path_a_images)}张基准图片")

    # 3. 深度遍历路径B的所有图片（修改3：使用深度遍历函数）
    path_b_images = get_all_images_deep(path_b)
    if not path_b_images:
        log_print(f"【警告】路径B下未找到支持的图片（{SUPPORT_FORMATS}）")
        return
    log_print(f"【初始化】路径B（含子文件夹）找到{len(path_b_images)}张待识别图片")

    # 4. 批量比对逻辑
    similar_records = []  # 记录相似图片对
    total_compare = 0  # 总比对次数
    start_total_time = time.time()

    for b_img_path in path_b_images:
        b_filename = os.path.basename(b_img_path)
        b_relative_path = os.path.relpath(b_img_path, path_b)  # 显示相对路径，便于识别子文件夹
        log_print(f"\n【开始比对】待识别图片：{b_relative_path}")

        # 转换待识别图片为Base64
        b_base64 = image_to_base64(b_img_path)
        if not b_base64:
            log_print(f"【跳过】图片转换失败：{b_relative_path}")
            continue

        # 和路径A的所有图片比对
        is_similar_any = False  # 是否和任意一张基准图相似
        similar_a_img = ""  # 相似的基准图名称
        similar_score = 0.0  # 相似度分数

        for a_img_path in path_a_images:
            a_filename = os.path.basename(a_img_path)
            a_relative_path = os.path.relpath(a_img_path, path_a)
            total_compare += 1

            # 转换基准图片为Base64
            a_base64 = image_to_base64(a_img_path)
            if not a_base64:
                log_print(f"【跳过】基准图转换失败：{a_relative_path}")
                continue

            # 调用API比对
            result = call_similarity_api(a_base64, b_base64)
            if not result:
                continue

            # 打印单次比对结果（显示相对路径）
            log_print(
                f"  比对 {a_relative_path} vs {b_relative_path} | 相似度：{result['similarity']:.4f} | 耗时：{result['cost_time']}s")

            # 判断是否相似
            if result["is_similar"]:
                is_similar_any = True
                similar_a_img = a_relative_path
                similar_score = result["similarity"]
                break  # 找到相似图，停止比对该待识别图

        # 处理比对结果
        if is_similar_any:
            # 相似：记录信息
            record = f"相似图片对 | 基准图：{similar_a_img} | 待识别图：{b_relative_path} | 相似度：{similar_score:.4f}"
            similar_records.append(record)
            log_print(f"【结果】{record}")
        else:
            # 不相似：移动到差异目录X
            try:
                # 保留子文件夹结构（可选，若需还原路径）
                b_target_subdir = os.path.dirname(os.path.relpath(b_img_path, path_b))
                target_dir = os.path.join(dir_x, b_target_subdir)
                os.makedirs(target_dir, exist_ok=True)

                target_path = os.path.join(target_dir, b_filename)
                shutil.move(b_img_path, target_path)
                log_print(f"【结果】{b_relative_path} 无相似图片 | 已移动到：{os.path.relpath(target_path, path_a)}")
            except Exception as e:
                log_print(f"【错误】移动图片失败：{b_relative_path} - {str(e)}")

    # 5. 打印最终统计
    total_cost_time = round(time.time() - start_total_time, 2)
    log_print(f"\n【批量比对完成】")
    log_print(f"  总比对次数：{total_compare}")
    log_print(f"  总耗时：{total_cost_time}s")
    log_print(f"  相似图片对数量：{len(similar_records)}")
    if similar_records:
        log_print(f"  相似记录：")
        for record in similar_records:
            log_print(f"    - {record}")
    log_print(f"  差异图片目录：{dir_x}")


# -------------------------- 构建GUI界面 --------------------------
def create_gui():
    global root, entry_path_a, entry_path_b, text_log

    # 主窗口配置
    root = tk.Tk()
    root.title("图库批量相似度检测工具（深度遍历版）")
    root.geometry("800x600")
    root.resizable(True, True)

    # 样式配置
    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 9))
    style.configure("TEntry", font=("Arial", 9))
    style.configure("TButton", font=("Arial", 9))

    # 1. 路径输入区域（紧凑布局）
    frame_input = ttk.Frame(root, padding="5")
    frame_input.pack(fill=tk.X, padx=5, pady=3)

    # 路径A输入
    label_a = ttk.Label(frame_input, text="基准图库路径(A)：", width=12)
    label_a.grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)
    entry_path_a = ttk.Entry(frame_input, width=50)
    entry_path_a.grid(row=0, column=1, padx=2, pady=2, sticky=tk.EW)
    entry_path_a.insert(0, "/Users/linglong/Downloads/test/image")

    # 路径B输入
    #  a文本的默认值是 /Users/linglong/Downloads/test/image_duibi
    label_b = ttk.Label(frame_input, text="待识别图库路径(B)：", width=12)
    label_b.grid(row=1, column=0, padx=2, pady=2, sticky=tk.W)
    entry_path_b = ttk.Entry(frame_input, width=50)
    entry_path_b.grid(row=1, column=1, padx=2, pady=2, sticky=tk.EW)
    entry_path_b.insert(0, "/Users/linglong/Downloads/test/image_duibi")

    # 按钮区域
    frame_button = ttk.Frame(root, padding="5")
    frame_button.pack(fill=tk.X, padx=5, pady=3)
    btn_start = ttk.Button(frame_button, text="开始批量比对", command=batch_compare)
    btn_start.pack(padx=2, pady=2)

    # 2. 日志展示区域（最大化占比）
    frame_log = ttk.Frame(root, padding="5")
    frame_log.pack(fill=tk.BOTH, padx=5, pady=3, expand=True)

    label_log = ttk.Label(frame_log, text="实时比对日志（深度遍历）：")
    label_log.pack(anchor=tk.W, padx=2, pady=2)

    # 日志文本框（带滚动条）
    scrollbar = ttk.Scrollbar(frame_log)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_log = tk.Text(frame_log, font=("Consolas", 12), wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text_log.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    scrollbar.config(command=text_log.yview)

    # 布局权重
    frame_input.columnconfigure(1, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)

    # 启动主循环
    root.mainloop()


# -------------------------- 程序入口 --------------------------
if __name__ == "__main__":
    try:
        create_gui()
    except Exception as e:
        messagebox.showerror("启动失败", f"GUI界面启动失败：{str(e)}")