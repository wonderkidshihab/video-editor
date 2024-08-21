import os
import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import subprocess
import concurrent.futures
import moviepy.editor as mp

class VideoSplitter:
    def __init__(self, master):
        self.master = master
        master.title("Video Splitter")

        # Create widgets
        self.input_label = ttk.Label(master, text="Input Video:")
        self.input_label.grid(row=0, column=0, padx=10, pady=10)

        self.input_entry = ttk.Entry(master)
        self.input_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = ttk.Button(master, text="Browse", command=self.select_input_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.duration_label = ttk.Label(master, text="Split Duration (seconds):")
        self.duration_label.grid(row=1, column=0, padx=10, pady=10)

        self.duration_entry = ttk.Entry(master)
        self.duration_entry.grid(row=1, column=1, padx=10, pady=10)

        self.output_dir_label = ttk.Label(master, text="Output Directory:")
        self.output_dir_label.grid(row=2, column=0, padx=10, pady=10)

        self.output_dir_entry = ttk.Entry(master)
        self.output_dir_entry.grid(row=2, column=1, padx=10, pady=10)

        self.browse_dir_button = ttk.Button(master, text="Browse", command=self.select_output_dir)
        self.browse_dir_button.grid(row=2, column=2, padx=10, pady=10)
        
        self.max_cores_label = ttk.Label(master, text="Max Cores:")
        self.max_cores_label.grid(row=4, column=0, padx=10, pady=10)

        self.max_cores_entry = ttk.Entry(master)
        self.max_cores_entry.grid(row=4, column=1, padx=10, pady=10)
        self.max_cores_entry.insert(0, "4")  # Default to 4 cores
        
        
        
        self.split_button = ttk.Button(master, text="Split Video", command=self.split_video)
        self.split_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        

    def select_input_file(self):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, filedialog.askopenfilename(title="Select Input Video"))

    def select_output_dir(self):
        self.output_dir_entry.delete(0, tk.END)
        self.output_dir_entry.insert(0, filedialog.askdirectory(title="Select Output Directory"))
        

    def split_video(self):
        input_file = self.input_entry.get()
        split_duration = float(self.duration_entry.get())
        output_dir = self.output_dir_entry.get()
        max_cores = int(self.max_cores_entry.get())

        if not os.path.exists(input_file):
            print("Error: Input file not found.")
            return

        if not os.path.exists(output_dir):
            print("Error: Output directory not found.")
            return

        video = mp.VideoFileClip(input_file)
        total_duration = video.duration
        video.close()

        num_splits = int(total_duration // split_duration)

        # Use a ThreadPoolExecutor to split the video into multiple parts
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_cores) as executor:
            futures = []
            for i in range(num_splits):
                start_time = i * split_duration
                end_time = start_time + split_duration
                if end_time > total_duration:
                    end_time = total_duration

                futures.append(executor.submit(self.split_video_part, input_file, output_dir, i, start_time, end_time))

            for future in concurrent.futures.as_completed(futures):
                future.result()

        print("Video splitting completed.")

    def split_video_part(self, input_file, output_dir, part_index, start_time, end_time):
        output_file = os.path.join(output_dir, f"output_{part_index+1}.mp4")
        clip = mp.VideoFileClip(input_file).subclip(start_time, end_time)
        clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
        clip.close()
        print(f"Video clip {part_index+1} saved as: {output_file}")

root = tk.Tk()
app = VideoSplitter(root)
root.mainloop()