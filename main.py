import concurrent.futures
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk

import cv2
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
        
        # Video title, Text input with default text as the files name
        self.title_label = ttk.Label(master, text="Video Title:")
        self.title_label.grid(row=4, column=0, padx=10, pady=10)

        self.title_entry = ttk.Entry(master)
        self.title_entry.grid(row=4, column=1, padx=10, pady=10)
        
        # Season and Episode
        self.season_label = ttk.Label(master, text="Season:")
        self.season_label.grid(row=5, column=0, padx=10, pady=10)

        self.season_entry = ttk.Entry(master)
        self.season_entry.grid(row=5, column=1, padx=10, pady=10)

        self.episode_label = ttk.Label(master, text="Episode:")
        self.episode_label.grid(row=6, column=0, padx=10, pady=10)

        self.episode_entry = ttk.Entry(master)
        self.episode_entry.grid(row=6, column=1, padx=10, pady=10)
        
        
        self.split_button = ttk.Button(master, text="Split Video", command=self.split_video)
        self.split_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        

    def select_input_file(self):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, filedialog.askopenfilename(title="Select Input Video"))
        self.title_entry.insert(0, os.path.splitext(os.path.basename(self.input_entry.get()))[0])

    def select_output_dir(self):
        self.output_dir_entry.delete(0, tk.END)
        self.output_dir_entry.insert(0, filedialog.askdirectory(title="Select Output Directory"))
        

    def split_video(self):
        input_file = self.input_entry.get() 
        split_duration = float(self.duration_entry.get())
        output_dir = self.output_dir_entry.get()
        title = self.title_entry.get()
        season = self.season_entry.get()
        episode = self.episode_entry.get()
        

        if not os.path.exists(input_file):
            print("Error: Input file not found.")
            return

        if not os.path.exists(output_dir):
            print("Error: Output directory not found.")
            return

        with mp.VideoFileClip(input_file) as video:
            fps = video.fps
            width, height = video.size
            aspect_ratio = width / height
            # if aspect_ratio == 16/9:
            new_height = int(width * 9/16)
            white_box_height = new_height - height
            final_height = new_height
            # else:
            #     print("Input video is not 16:9 aspect ratio.")
            #     return

            total_duration = video.duration
            num_splits = int(total_duration // split_duration)

            # Use a ThreadPoolExecutor with the specified max number of cores
            # with concurrent.futures.ThreadPoolExecutor(max_workers=max_cores) as executor:
                # futures = []
            for i in range(num_splits):
            # for i in range(2):
                start_time = i * split_duration
                end_time = start_time + split_duration
                if end_time > total_duration:
                    end_time = total_duration
                
                self.split_video_part(video, output_dir, i, start_time, end_time, fps, width, final_height, white_box_height, title, season, episode)

                #     futures.append(executor.submit(self.split_video_part, video, output_dir, i, start_time, end_time, fps, width, final_height, white_box_height))

                # for future in concurrent.futures.as_completed(futures):
                #     future.result()

        print("Video splitting completed.")

    def split_video_part(self, video, output_dir, part_index, start_time, end_time, fps, width, height, white_box_height, title, season, episode):
        print(f"video: {video} output_dir: {output_dir} part_index: {part_index} start_time: {start_time} end_time: {end_time} fps: {fps} width: {width} height: {height} white_box_height: {white_box_height}")
        clip = video.subclip(start_time, end_time)
        clip = clip.resize((1080, 608))
        clip = clip.set_position(("center", "center"))
        white_box = mp.ColorClip(size=(1080, 1920), color=(255, 255, 255)).set_position(("center", "top"))
        title_clip = mp.TextClip(title, fontsize=90).set_position(("center", 30))
        meta_clip = mp.TextClip(f"Part: {part_index+1}", fontsize=40).set_position(("center", 130))
        
        final_clip = mp.CompositeVideoClip([white_box, clip, title_clip, meta_clip], size=(1080, 1920))
        final_clip = final_clip.set_duration(end_time-start_time)
        output_file = os.path.join(output_dir, f"output_{part_index+1}.mp4")
        with final_clip:
            final_clip.write_videofile(output_file, codec="libx264", threads=4, audio_codec="aac", fps=fps, bitrate="800k")
        
        print(f"Video clip {part_index+1} saved as: {output_file}")

root = tk.Tk()
app = VideoSplitter(root)
root.mainloop()