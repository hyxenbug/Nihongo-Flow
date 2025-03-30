import os
import subprocess
import argparse

def process_batch(input_dir, output_dir, mode):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 遍历输入目录
    for filename in os.listdir(input_dir):
        if filename.endswith(".mkv"):
            # 获取文件名主干
            base_name = os.path.splitext(filename)[0]
            
            # 构建文件路径
            mkv_path = os.path.join(input_dir, filename)
            srt_path = os.path.join(input_dir, f"{base_name}.ja.srt")
            
            # 检查字幕文件是否存在
            if not os.path.exists(srt_path):
                print(f"跳过 {filename}：未找到对应的字幕文件")
                continue
            
            # 构建输出路径
            output_audio = os.path.join(output_dir, f"{base_name}.mp3")
            output_lrc = os.path.join(output_dir, f"{base_name}.lrc")
            
            # 执行转换命令
            cmd = [
                "python",
                "converter.py",  # 替换为你的主脚本文件名
                mkv_path,
                srt_path,
                output_audio,
                "--mode",
                mode
            ]
            
            try:
                subprocess.run(cmd, check=True)
                print(f"成功处理：{filename}")
            except subprocess.CalledProcessError as e:
                print(f"处理失败：{filename} - 错误信息：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量视频转带歌词音频工具")
    parser.add_argument("input_dir", help="输入目录路径")
    parser.add_argument("output_dir", help="输出目录路径")
    parser.add_argument("--mode", choices=['remove', 'fade', 'speed'], default='remove',
                       help="处理模式：remove直接删除无字幕片段，fade淡入淡出过渡，speed加速跳过")
    
    args = parser.parse_args()
    
    process_batch(args.input_dir, args.output_dir, args.mode)