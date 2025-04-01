import uuid

def is_valid_uuid(filename):
    try:
        # 移除文件扩展名（如果有）
        name_without_ext = filename.split('.')[0]
        uuid_obj = uuid.UUID(name_without_ext)
        return str(uuid_obj) == name_without_ext
    except ValueError:
        return False

# 测试示例
print(is_valid_uuid("123e4567-e89b-12d3-a456-426614174000"))  # True
print(is_valid_uuid("123e4567-e89b-12d3-a456-426614174000.txt"))  # True（忽略扩展名）
print(is_valid_uuid("not-a-uuid"))  # False