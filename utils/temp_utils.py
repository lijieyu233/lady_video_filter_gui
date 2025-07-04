import os


def transform_path(original_path, parameter):
    """
    将原始文件路径转换为新的筛选后路径

    参数:
        original_path: 原始文件路径 (字符串)
        parameter: 要插入的筛选参数 (字符串)

    返回:
        转换后的新路径 (字符串)
    """
    # 分离驱动器号和路径主体
    drive, path = os.path.splitdrive(original_path)
    # 标准化路径分隔符并分割路径
    path = os.path.normpath(path)
    path_parts = [part for part in path.split(os.sep) if part]

    try:
        index = path_parts.index("待筛选")
    except ValueError:
        return original_path

    new_parts = (
            path_parts[:index] +
            ["已筛选", parameter] +
            path_parts[index + 1:]
    )

    # 重新组合路径
    new_path = os.sep + os.path.join(*new_parts) if new_parts else ""

    # 添加驱动器号（如果存在）
    if drive:
        new_path = drive + (os.sep if not new_path.startswith(os.sep) else "") + new_path
    else:
        new_path = os.path.join(*new_parts) if new_parts else ""

    return new_path.replace("\\", "/")


# 示例使用
if __name__ == "__main__":
    # 测试用例1
    original1 = r"D:\wsl\chfs\搬运视频\国内搬运\游戏号\待筛选\抖音\dy_7504493900145446170.mp4"
    new1 = transform_path(original1, "合格")
    print(f"原始路径: {original1}")
    print(f"生成路径: {new1}")
    print()

    # 测试用例2
    original2 = r"D:\wsl\chfs\搬运视频\国内搬运\专家号\待筛选\快手\dy_7504493900145446170.mp4"
    new2 = transform_path(original2, "优质")
    print(f"原始路径: {original2}")
    print(f"生成路径: {new2}")