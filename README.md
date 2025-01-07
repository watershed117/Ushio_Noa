
---

# 项目名称  
**Ushio_Noa**  

> *Qui aimes-tu le mieux, homme énigmatique, dis ?*  
---
## 项目介绍  
一个基于 Ren'Py 制作的开源galgame。<br>
由deepseek进行对话，选择人物动画以及背景图片切换<br>
由chatglm进行文本翻译（中文->日文）<br>
由gpt-sovits进行语音合成 （日语）<br>

对话界面顶部包含四个按钮，从左往右依次为：  
1. 播放语音
2. 保存语音（保存至game/tts）
3. 清除上下文
4. 保存对话（保存至game/history）

## 使用说明  

### 1. 配置 API Key  
进入 `game` 文件夹，修改配置文件以设置 API Key。  

示例配置文件：  
```json
{
  "chatglm_api_key": "***",
  "deepseek_api_key": "***",
  "model": "glm-4-flash",
  "tts": false,
  "limit": "8k",
  "proxy": {
    "http": null,
    "https": null
  }
}
```
chatglm_api_key 和 deepseek_api_key 分别为 ChatGlass 和 DeepSeek 的 API Key。  
model 选项为翻译模型名称，glm-4-flash 为默认模型。  
tts 选项为是否使用 TTS，false 为不使用。目前不启用tts，暂未嵌入gsv包。  
limit 选项为上下文长度限制，8k 为默认值。  
proxy为代理设置：<br>
例如:
```json
"proxy": {
  "http": "http://127.0.0.1:7890",
  "https": "http://127.0.0.1:7890"
}
```

---

## 使用的开源项目  
本项目基于以下开源项目构建：  

1. **[renpy-SWHolo](https://github.com/Gouvernathor/renpy-SWHolo)**  
2. **[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)**  

---

### bug反馈：
    - QQ群：1121897130