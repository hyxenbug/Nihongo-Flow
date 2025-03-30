import argparse
from pydub import AudioSegment
import srt
import os

def ms_to_lrc_time(ms):
    """将毫秒转换为LRC时间格式[MM:SS.XX]"""
    total_seconds = ms / 1000
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    hundredths = int((ms % 1000) // 10)
    return f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"

def parse_srt(file_path):
    """解析SRT文件并返回原始字幕列表和合并后的时间区间（毫秒）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        subs = list(srt.parse(f.read()))
    
    original_subs = []
    intervals = []
    for sub in subs:
        start = int(sub.start.total_seconds() * 1000)
        end = int(sub.end.total_seconds() * 1000)
        original_subs.append((start, end, sub.content))
        intervals.append((start, end))
    
    # 合并重叠或相邻的时间区间
    if not intervals:
        return original_subs, []
    
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return original_subs, merged

def speed_change(sound, speed=1.0):
    """变速处理（会改变音调）"""
    return sound._spawn(
        sound.raw_data,
        overrides={"frame_rate": int(sound.frame_rate * speed)}
    ).set_frame_rate(sound.frame_rate)

def process_audio(audio, merged_intervals, mode, fade_duration=200):
    """处理音频并返回处理后的音频和保留区间信息"""
    time_points = [0]
    for start, end in merged_intervals:
        time_points.extend([start, end])
    time_points.append(len(audio))
    time_points = sorted(time_points)
    
    # 分割音频片段并关联原始区间
    segments = []
    for i in range(len(time_points)-1):
        seg_start = time_points[i]
        seg_end = time_points[i+1]
        is_subtitle = i % 2 == 1
        
        original_start, original_end = None, None
        if is_subtitle:
            interval_idx = (i - 1) // 2
            original_start, original_end = merged_intervals[interval_idx]
        
        segments.append((
            is_subtitle,
            seg_start,
            seg_end,
            original_start,
            original_end
        ))
    
    processed = []
    retained_intervals = []
    current_time = 0
    
    for seg in segments:
        is_subtitle, seg_start, seg_end, orig_start, orig_end = seg
        duration = seg_end - seg_start
        seg_audio = audio[seg_start:seg_end]
        
        if is_subtitle:
            # 处理字幕片段
            if mode == 'fade':
                seg_audio = seg_audio.fade_in(fade_duration).fade_out(fade_duration)
            processed.append(seg_audio)
            
            # 记录保留区间
            retained_intervals.append({
                'original_start': orig_start,
                'original_end': orig_end,
                'processed_start': current_time,
                'processed_end': current_time + duration
            })
            current_time += duration
        else:
            # 处理无字幕片段
            if mode == 'speed':
                speed_factor = 3.0
                seg_audio = speed_change(seg_audio, speed_factor)
                processed.append(seg_audio)
                current_time += len(seg_audio)
            elif mode == 'fade':
                continue  # fade模式直接跳过无字幕片段
            elif mode == 'remove':
                continue
    
    final_audio = sum(processed, AudioSegment.silent(duration=0))
    return final_audio, retained_intervals

def generate_lrc(original_subs, retained_intervals, output_path):
    """生成LRC歌词文件（自动合并换行字幕）"""
    entries = []
    for start, end, text in original_subs:
        # 合并多行字幕并去除换行符
        clean_text = " ".join(text.splitlines()).strip()
        
        # 寻找匹配的保留区间
        for interval in retained_intervals:
            if start >= interval['original_start'] and end <= interval['original_end']:
                # 计算处理后的时间
                processed_start = interval['processed_start'] + (start - interval['original_start'])
                entries.append((
                    processed_start,
                    f"[{ms_to_lrc_time(processed_start)}] {clean_text}"
                ))
                break
    
    # 按时间排序并写入文件
    entries.sort(key=lambda x: x[0])
    with open(output_path, 'w', encoding='utf-8') as f:
        for _, line in entries:
            f.write(line + '\n')

def main():
    parser = argparse.ArgumentParser(description='生成带歌词的音频文件')
    parser.add_argument('input_video', help='输入视频文件路径（支持mp4/mkv/avi等格式）')
    parser.add_argument('input_srt', help='输入SRT字幕文件路径')
    parser.add_argument('output', help='输出音频文件路径（支持mp3/wav等格式）')
    parser.add_argument('--mode', choices=['remove', 'fade', 'speed'], default='remove',
                       help='处理模式：remove直接删除无字幕片段，fade淡入淡出过渡，speed加速跳过')
    
    args = parser.parse_args()
    
    # 解析SRT
    original_subs, merged_intervals = parse_srt(args.input_srt)
    
    # 提取音频
    audio = AudioSegment.from_file(args.input_video)
    
    # 处理音频
    processed_audio, retained_intervals = process_audio(audio, merged_intervals, args.mode)
    
    # 导出音频
    processed_audio.export(args.output, format=args.output.split('.')[-1])
    
    # 生成歌词文件
    lrc_path = os.path.splitext(args.output)[0] + '.lrc'
    generate_lrc(original_subs, retained_intervals, lrc_path)
    
    print(f"处理完成！音频文件：{args.output}")
    print(f"生成的歌词文件：{lrc_path}")

if __name__ == "__main__":
    main()