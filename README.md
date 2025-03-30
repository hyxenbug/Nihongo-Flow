# Nihongo Flow - 日语沉浸式听力优化工具

## 📚 项目背景  
灵感来源于[TheMoeWay](https://learnjapanese.moe/)日语学习方法论，基于"浓缩音频(Condensed Audio)"理念开发。通过智能处理番剧/动画音频，移除非对话片段，帮助学习者在被动听力训练中最大化接触有效日语内容。

## ✨ 核心功能  
- 🎧 自动生成带歌词的音频文件  
- ✂️ 智能处理模式：  
  - `remove` 直接删除无字幕片段  
  - `fade` 淡入淡出过渡  
  - `speed` 3倍速跳过静音段落  
- 📖 同步生成LRC歌词文件  
- 🚀 支持批量处理与图形界面操作  

## 🛠️ 技术特性  
- 支持MP4/MKV/AVI等主流视频格式  
- 自动匹配字幕文件（*.ja.srt）  
- 保持原始音质的高效处理  

## 📥 安装  
```bash
pip install pydub python-srt
sudo apt install ffmpeg  # Linux
brew install ffmpeg     # macOS

## 🚀 快速开始

### 单文件处理
python converter.py input.mkv subtitles.ja.srt output.mp3 --mode speed

### 批量处理
python batch_processor.py ./input_dir ./output_dir --mode fade

### GUI
python gui_processor.py

## 🌐 相关资源

[30 Day Japanese - TheMoeWay](https://learnjapanese.moe/routine/#day-10)
[Japanese subtitles - kitsunekko.net](https://kitsunekko.net/dirlist.php?dir=subtitles%2Fjapanese%2F)




Love Live! 浓缩音频示例
