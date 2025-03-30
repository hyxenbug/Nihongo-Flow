import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
import subprocess

class BatchProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频歌词音频转换器")
        self.root.geometry("800x600")
        
        # 创建控件
        self.create_widgets()
        
        # 初始化状态
        self.processing = False
    
    def create_widgets(self):
        # 输入目录部分
        input_frame = ttk.LabelFrame(self.root, text="输入设置")
        input_frame.pack(padx=10, pady=5, fill="x")
        
        self.input_dir = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_dir, width=50).grid(row=0, column=0, padx=5)
        ttk.Button(input_frame, text="浏览...", command=self.select_input_dir).grid(row=0, column=1)
        
        # 输出目录部分
        output_frame = ttk.LabelFrame(self.root, text="输出设置")
        output_frame.pack(padx=10, pady=5, fill="x")
        
        self.output_dir = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=0, padx=5)
        ttk.Button(output_frame, text="浏览...", command=self.select_output_dir).grid(row=0, column=1)
        
        # 处理选项
        options_frame = ttk.LabelFrame(self.root, text="处理选项")
        options_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(options_frame, text="处理模式:").grid(row=0, column=0)
        self.mode = tk.StringVar(value="remove")
        mode_combo = ttk.Combobox(options_frame, textvariable=self.mode, 
                                values=["remove", "fade", "speed"], state="readonly")
        mode_combo.grid(row=0, column=1, sticky="w")
        
        # 日志显示
        log_frame = ttk.LabelFrame(self.root, text="处理日志")
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_area.pack(fill="both", expand=True)
        
        # 控制按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.process_btn = ttk.Button(button_frame, text="开始处理", command=self.start_processing)
        self.process_btn.pack(side="left", padx=5)
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side="left", padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="indeterminate")
    
    def select_input_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.input_dir.set(dir_path)
    
    def select_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)
    
    def log(self, message, color="black"):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, message + "\n", color)
        self.log_area.configure(state="disabled")
        self.log_area.see(tk.END)
    
    def clear_log(self):
        self.log_area.configure(state="normal")
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state="disabled")
    
    def validate_inputs(self):
        if not os.path.isdir(self.input_dir.get()):
            messagebox.showerror("错误", "请输入有效的输入目录")
            return False
        if not os.path.isdir(self.output_dir.get()):
            try:
                os.makedirs(self.output_dir.get(), exist_ok=True)
            except:
                messagebox.showerror("错误", "无法创建输出目录")
                return False
        return True
    
    def process_files(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        mode = self.mode.get()
        
        for filename in os.listdir(input_dir):
            if filename.endswith(".mkv"):
                base_name = os.path.splitext(filename)[0]
                mkv_path = os.path.join(input_dir, filename)
                srt_path = os.path.join(input_dir, f"{base_name}.ja.srt")
                
                if not os.path.exists(srt_path):
                    self.log(f"跳过 {filename}：字幕文件不存在", "red")
                    continue
                
                output_audio = os.path.join(output_dir, f"{base_name}.mp3")
                cmd = [
                    "python",
                    "converter.py",
                    mkv_path,
                    srt_path,
                    output_audio,
                    "--mode",
                    mode
                ]
                
                try:
                    self.log(f"正在处理：{filename}...")
                    subprocess.run(cmd, check=True, capture_output=True)
                    self.log(f"✓ 完成处理：{filename}", "green")
                except subprocess.CalledProcessError as e:
                    self.log(f"✗ 处理失败：{filename}\n错误信息：{e.stderr.decode()}", "red")
        
        self.processing = False
        self.root.after(0, self.on_processing_end)
    
    def start_processing(self):
        if self.processing:
            return
        
        if not self.validate_inputs():
            return
        
        self.processing = True
        self.process_btn.config(state="disabled")
        self.progress.pack(pady=5, fill="x", padx=10)
        self.progress.start()
        
        Thread(target=self.process_files, daemon=True).start()
    
    def on_processing_end(self):
        self.progress.stop()
        self.progress.pack_forget()
        self.process_btn.config(state="normal")
        messagebox.showinfo("完成", "所有文件处理完成！")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchProcessorApp(root)
    
    # 配置日志颜色
    app.log_area.tag_config("red", foreground="red")
    app.log_area.tag_config("green", foreground="green")
    
    root.mainloop()