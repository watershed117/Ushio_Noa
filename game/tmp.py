data = {
    "result": {
        "error": "Invalid 'value'"
    },
    "tool_call_id": "12345"
}

# 先将字典转换为字符串
str_data = str(data)

# 手动替换转义字符
str_data = str_data.replace("\\'", "'")
print(str_data)