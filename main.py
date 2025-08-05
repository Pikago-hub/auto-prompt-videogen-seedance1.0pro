import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

class VideoGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Seedance Video Generator")
        self.root.geometry("600x700")
        self.api_key = os.getenv('ARK_API_KEY')
        if not self.api_key or self.api_key == 'your_api_key_here':
            messagebox.showerror("Error", "Please set your ARK_API_KEY in the .env file")
            root.destroy()
            return
        
        self.setup_ui()
        self.generation_thread = None
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Seedance Video Generator", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Generation Mode Frame
        mode_frame = ttk.LabelFrame(main_frame, text="Generation Mode", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Mode Selection
        self.mode_var = tk.StringVar(value="text")
        ttk.Radiobutton(mode_frame, text="Text-to-Video", variable=self.mode_var, value="text", command=self.on_mode_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Image-to-Video", variable=self.mode_var, value="image", command=self.on_mode_change).grid(row=0, column=1, sticky=tk.W, padx=20)
        
        # Image URL Frame (initially hidden)
        self.image_frame = ttk.LabelFrame(main_frame, text="First Frame Image", padding="10")
        self.image_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.image_frame.grid_remove()  # Hide initially
        
        # Image URL Entry
        ttk.Label(self.image_frame, text="Image URL:").grid(row=0, column=0, sticky=tk.W)
        self.image_url_var = tk.StringVar()
        self.image_url_entry = ttk.Entry(self.image_frame, textvariable=self.image_url_var, width=50)
        self.image_url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Label(self.image_frame, text="(Paste your image URL here)", font=('Arial', 9, 'italic')).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Parameters Frame
        params_frame = ttk.LabelFrame(main_frame, text="Video Parameters", padding="10")
        params_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Aspect Ratio
        ttk.Label(params_frame, text="Aspect Ratio:").grid(row=0, column=0, sticky=tk.W)
        self.ratio_var = tk.StringVar(value="16:9")
        ratio_frame = ttk.Frame(params_frame)
        ratio_frame.grid(row=0, column=1, sticky=tk.W)
        self.ratio_landscape = ttk.Radiobutton(ratio_frame, text="16:9 (Landscape)", variable=self.ratio_var, value="16:9")
        self.ratio_landscape.pack(side=tk.LEFT)
        self.ratio_portrait = ttk.Radiobutton(ratio_frame, text="9:16 (Portrait)", variable=self.ratio_var, value="9:16")
        self.ratio_portrait.pack(side=tk.LEFT, padx=10)
        
        # Resolution
        ttk.Label(params_frame, text="Resolution:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.resolution_var = tk.StringVar(value="720p")
        res_frame = ttk.Frame(params_frame)
        res_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(res_frame, text="720p", variable=self.resolution_var, value="720p").pack(side=tk.LEFT)
        ttk.Radiobutton(res_frame, text="1080p", variable=self.resolution_var, value="1080p").pack(side=tk.LEFT, padx=10)
        
        # Duration
        ttk.Label(params_frame, text="Duration:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar(value="5")
        dur_frame = ttk.Frame(params_frame)
        dur_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(dur_frame, text="5 seconds", variable=self.duration_var, value="5").pack(side=tk.LEFT)
        ttk.Radiobutton(dur_frame, text="10 seconds", variable=self.duration_var, value="10").pack(side=tk.LEFT, padx=10)
        
        # Prompt Frame
        prompt_frame = ttk.LabelFrame(main_frame, text="Video Prompt", padding="10")
        prompt_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Prompt Text Area
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, width=60, height=8)
        self.prompt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Fix Prompt Button
        self.fix_prompt_button = ttk.Button(button_frame, text="Fix Prompt", command=self.fix_prompt)
        self.fix_prompt_button.pack(side=tk.LEFT, padx=5)
        
        # Generate Button
        self.generate_button = ttk.Button(button_frame, text="Generate Video", command=self.generate_video)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        # Progress Frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Status Label
        self.status_label = ttk.Label(progress_frame, text="Ready to generate video")
        self.status_label.grid(row=1, column=0, pady=5)
        
        # Output Frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        output_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Output Text Area
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=60, height=10)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        prompt_frame.rowconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        self.image_frame.columnconfigure(1, weight=1)
        
    def on_mode_change(self):
        """Handle mode change between text-to-video and image-to-video"""
        if self.mode_var.get() == "image":
            self.image_frame.grid()
            # Set aspect ratio to adaptive for image-to-video
            self.ratio_var.set("adaptive")
            # Disable aspect ratio selection
            self.ratio_landscape.config(state="disabled")
            self.ratio_portrait.config(state="disabled")
        else:
            self.image_frame.grid_remove()
            # Re-enable aspect ratio selection
            self.ratio_landscape.config(state="normal")
            self.ratio_portrait.config(state="normal")
            # Reset to default aspect ratio
            if self.ratio_var.get() == "adaptive":
                self.ratio_var.set("16:9")
    
    def log_output(self, message):
        """Add message to output log"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.output_text.update()
        
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.status_label.update()
        
    def fix_prompt(self):
        """Optimize the prompt using Doubao chat API"""
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt to fix")
            return
        
        self.fix_prompt_button.config(state="disabled")
        self.generate_button.config(state="disabled")
        
        # Run in separate thread
        threading.Thread(target=self._fix_prompt_thread, args=(prompt,)).start()
    
    def _fix_prompt_thread(self, prompt):
        """Thread function to call chat API for prompt optimization"""
        try:
            self.update_status("Optimizing prompt...")
            self.log_output("Calling AI to optimize prompt...")
            
            system_prompt = """你是一个提示词优化工程师，根据以下提示词指南,优化提示词，在优化过程中，请保持所有指南的完整性，并且尽量具体，不要返回优化说明，直接返回优化后的提示词:
{
  "动作指令": [
    "1. 基础动作：主体+动作",
    "2.多动作指令：按照动作发生的时序，清晰描述出多个动作，实现单人物多动作/多人物多动作。"
  ],
  "镜头语言": [
    "1. 基础运镜：精准响应推、拉、摇、移、环绕、跟随、升、降、变焦等运镜指令。",
    "2. 复杂运镜：对于进阶玩家，可以将多个运镜指令进行组合构建出有创意的长镜头",
    "3.景别和视角控制：可以使用远景、全景、中景、近景、特写这样的专业景别描述来控制。还可以选择具体的观察角度：水下镜头，航拍镜头，高机位俯拍，低机位仰拍，微距摄影，以xx为前景的镜头等"
  ],
  "多风格直出": [
    "具有直出多种风格的能力，包含2D/3D，以及更细分的体素，像素，毛毡，粘土，插画等。"
  ],
  "Prompt 控制美感": [
    "1.人物外形： 可以发挥想象，精细刻画出人物/场景/衣着的细节，生成各种不同长相特征的角色。",
    "2. 画面美感：精细化描述画面，用自然语言写出画面的氛围特征，可以控制画面整体的美感"
  ],
  "多镜头能力": [
    "支持在同一prompt里包含多个切镜，这些切镜会根据提示词的内容，保持主体/风格/场景的延续性。镜头的变化，通过"镜头切换"来进行连接，在每次切镜之后，如果场景和人物发生了变化，可以用prompt刻画新出现的人物/场景的特征。"
  ],
  "创意特效": [
    "模型本身即可实现多种特效，发挥想象可以实现许多有意思的效果。"
  ]
}

请根据以上指南，将用户的简单描述优化成专业的视频生成提示词。"""
            
            # Call the chat API
            url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "doubao-seed-1-6-thinking-250715",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Extract the optimized prompt
            if "choices" in result and len(result["choices"]) > 0:
                optimized_prompt = result["choices"][0]["message"]["content"]
                
                # Update the prompt text area
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", optimized_prompt)
                
                self.log_output("Prompt optimized successfully!")
                self.update_status("Prompt optimization complete")
            else:
                raise Exception("Unexpected API response format")
                
        except Exception as e:
            self.log_output(f"Error optimizing prompt: {str(e)}")
            self.update_status("Error during optimization")
            messagebox.showerror("Error", f"Failed to optimize prompt: {str(e)}")
            
        finally:
            self.fix_prompt_button.config(state="normal")
            self.generate_button.config(state="normal")
    
    def generate_video(self):
        """Handle generate button click"""
        if self.generation_thread and self.generation_thread.is_alive():
            messagebox.showwarning("Warning", "Video generation already in progress!")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a video prompt")
            return
        
        # Disable buttons
        self.generate_button.config(state="disabled")
        self.fix_prompt_button.config(state="disabled")
        
        # Clear output log
        self.output_text.delete("1.0", tk.END)
        
        # Start generation in separate thread
        self.generation_thread = threading.Thread(target=self._generate_video_thread, args=(prompt,))
        self.generation_thread.start()
        
    def _generate_video_thread(self, prompt):
        """Video generation thread"""
        try:
            # Get parameters
            mode = self.mode_var.get()
            ratio = self.ratio_var.get()
            resolution = self.resolution_var.get()
            duration = self.duration_var.get()
            
            # Build full prompt
            full_prompt = f"{prompt} --rt {ratio} --rs {resolution} --dur {duration}"
            self.log_output(f"Mode: {'Image-to-Video' if mode == 'image' else 'Text-to-Video'}")
            self.log_output(f"Prompt: {full_prompt}")
            
            # Reset progress
            self.progress_var.set(0)
            self.update_status("Starting video generation...")
            
            # Start generation
            url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Build content array based on mode
            content = [{"type": "text", "text": full_prompt}]
            
            if mode == "image":
                image_url = self.image_url_var.get().strip()
                if not image_url:
                    raise Exception("Please provide an image URL for image-to-video mode")
                
                self.log_output(f"Image URL: {image_url}")
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            
            data = {
                "model": "doubao-seedance-1-0-pro-250528",
                "content": content
            }
            
            # Log the request data
            self.log_output(f"Request URL: {url}")
            self.log_output(f"Request Data: {data}")
            
            response = requests.post(url, headers=headers, json=data)
            
            # Log the response details
            self.log_output(f"Response Status Code: {response.status_code}")
            self.log_output(f"Response Headers: {dict(response.headers)}")
            
            try:
                result = response.json()
                self.log_output(f"Response Body: {result}")
            except:
                self.log_output(f"Response Text: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            if "id" not in result:
                raise Exception(f"Unexpected API response: {result}")
            
            task_id = result["id"]
            self.log_output(f"Task ID: {task_id}")
            
            # Poll for completion
            poll_url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
            start_time = time.time()
            
            while True:
                elapsed = int(time.time() - start_time)
                
                # Update progress 
                progress = min(elapsed / 60 * 90, 90)  
                self.progress_var.set(progress)
                
                # Check status
                status_response = requests.get(poll_url, headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                
                status = status_data.get("status")
                self.update_status(f"Status: {status} ({elapsed}s)")
                
                if status == "succeeded":
                    # Get video URL
                    content = status_data.get("content", {})
                    video_url = content.get("video_url")
                    
                    if not video_url:
                        raise Exception("No video URL in response")
                    
                    self.log_output(f"Video URL received")
                    self.update_status("Downloading video...")
                    
                    # Download video
                    video_response = requests.get(video_url)
                    video_response.raise_for_status()
                    
                    # Save video
                    timestamp = int(time.time())
                    filename = f"seedance_video_{timestamp}.mp4"
                    
                    with open(filename, "wb") as f:
                        f.write(video_response.content)
                    
                    self.progress_var.set(100)
                    total_time = int(time.time() - start_time)
                    
                    self.log_output(f"Success! Video saved as: {filename}")
                    self.log_output(f"Generation time: {total_time} seconds")
                    self.log_output(f"Location: {os.path.abspath(filename)}")
                    self.update_status(f"Complete! Saved as {filename}")
                    
                    messagebox.showinfo("Success", f"Video saved as {filename}")
                    break
                    
                elif status == "failed":
                    error_msg = status_data.get("error", "Unknown error")
                    raise Exception(f"Generation failed: {error_msg}")
                
                time.sleep(5)
                
                # Timeout after 10 minutes
                if elapsed > 600:
                    raise Exception("Generation timed out after 10 minutes")
                    
        except Exception as e:
            self.log_output(f"Error: {str(e)}")
            self.update_status("Error occurred")
            messagebox.showerror("Error", str(e))
            
        finally:
            # Re-enable buttons
            self.generate_button.config(state="normal")
            self.fix_prompt_button.config(state="normal")
            
def main():
    root = tk.Tk()
    app = VideoGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()