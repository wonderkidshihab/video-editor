import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


class VideoSplitterApp:
    def __init__(self, master):
        self.master = master
        master.title("Video Splitter")
        master.geometry("400x300")

        self.file_path = tk.StringVar()
        self.duration = tk.StringVar()
        self.output_dir = tk.StringVar()

        tk.Label(master, text="Select Video File:").pack(pady=10)
        tk.Entry(master, textvariable=self.file_path, width=40).pack()
        tk.Button(master, text="Browse", command=self.browse_file).pack(pady=5)
        
        tk.Label(master, text="Select Output Directory:").pack(pady=10)
        tk.Entry(master, textvariable=self.output_dir, width=40).pack()
        tk.Button(master, text="Browse", command=self.browse_output_dir).pack(pady=5)



        tk.Label(master, text="Split Duration (in seconds):").pack(pady=10)
        tk.Entry(master, textvariable=self.duration, width=10).pack()

        tk.Button(master, text="Split Video", command=self.split_video).pack(pady=20)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.mkv")])
        self.file_path.set(filename)
        
    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        self.output_dir.set(directory)
        
    def show_message(self, message):
        messagebox.showinfo("Message", message)


    def split_video(self):
        input_file = self.file_path.get()
        segment_duration = self.duration.get()

        if not input_file or not segment_duration:
            messagebox.showerror("Error", "Please select a file and specify the split duration.")
            return

        try:
            segment_duration = int(segment_duration)
        except ValueError:
            messagebox.showerror("Error", "Invalid duration. Please enter a number.")
            return

        output_dir = self.output_dir.get()

        if not os.path.exists(output_dir):
            messagebox.showerror("Error", "Invalid output directory.")
            return

        base_name = os.path.splitext(os.path.basename(input_file))[0]

        # Prepare the ffmpeg command for segmenting the video
        command = [
            "ffmpeg",
            "-i", input_file,
            "-fflags", "+genpts",  # Generate PTS if missing
            "-map", "0",
            "-map", "-0:s",  # Exclude subtitles
            "-codec", "copy",
            "-f", "segment",
            "-segment_format", "mp4",
            "-segment_time", str(segment_duration),
            "-reset_timestamps", "1",
            os.path.join(output_dir, f"{base_name}_%03d.mp4")
        ]

        # Run the ffmpeg command
        self.run_ffmpeg_command(command)
        
        self.show_message(f"Video split into segments of {segment_duration} seconds and saved in {output_dir}, total {len(os.listdir(output_dir))} segments.")
        

    def run_ffmpeg_command(self, command):
        """Run the ffmpeg command with subprocess."""
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())  # Print output for debugging
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while processing: {e.stderr.decode()}")
            messagebox.showerror("Error", f"An error occurred while splitting: {e.stderr.decode()}")

root = tk.Tk()
app = VideoSplitterApp(root)
root.mainloop()
