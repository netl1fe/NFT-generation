import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
import shutil
import zipfile

class TraitBubble:
    def __init__(self, canvas, trait_name, x, y):
        self.canvas = canvas
        self.trait_name = trait_name
        self.x = x
        self.y = y
        self.radius = 25
        self.bubble_id = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="white", outline="black"
        )
        self.text_id = self.canvas.create_text(
            self.x, self.y - self.radius - 15,
            text=self.trait_name, fill="black",
            font=("Arial", 10, "bold")
        )
        self.canvas.tag_bind(self.bubble_id, "<Button-1>", self.start_drag)
        self.canvas.tag_bind(self.bubble_id, "<B1-Motion>", self.move_drag)
        self.canvas.tag_bind(self.bubble_id, "<ButtonRelease-1>", self.stop_drag)
        self.canvas.tag_bind(self.bubble_id, "<Double-Button-1>", self.delete_bubble)
    
    def start_drag(self, event):
        self.drag_data = {"x": event.x, "y": event.y}
        
    def move_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.bubble_id, dx, dy)
        self.canvas.move(self.text_id, dx, dy)
        self.x += dx
        self.y += dy
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
    def stop_drag(self, event):
        self.drag_data = None
        
    def delete_bubble(self, event):
        self.canvas.delete(self.bubble_id)
        self.canvas.delete(self.text_id)

class NFTGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFT Generator")
        
        self.trait_categories = {}
        self.trait_bubbles = []
        self.generated_images = []
        self.num_nfts = 1
        
        # Create and configure the UI elements
        self.trait_label = tk.Label(self.root, text="Trait Categories:")
        self.trait_label.pack()
        
        self.trait_buttons_frame = tk.Frame(self.root)
        self.trait_buttons_frame.pack()
        
        self.add_trait_button = tk.Button(self.root, text="Add Trait Category", command=self.add_trait_category)
        self.add_trait_button.pack()
        
        self.generate_label = tk.Label(self.root, text="Number of NFTs to Generate:")
        self.generate_label.pack()
        
        self.generate_entry = tk.Entry(self.root)
        self.generate_entry.insert(tk.END, "1")
        self.generate_entry.pack()
        
        self.generate_button = tk.Button(self.root, text="Generate NFT", command=self.generate_nft)
        self.generate_button.pack()
        
        self.download_button = tk.Button(self.root, text="Download All NFTs", command=self.download_nfts)
        self.download_button.pack()
        
        self.image_label = tk.Label(self.root)
        self.image_label.pack()
        
        self.canvas = tk.Canvas(self.root, width=500, height=500)
        self.canvas.pack()
        
    def add_trait_category(self):
        trait_category = simpledialog.askstring("Add Trait Category", "Enter the name of the trait category:")
        if trait_category:
            folder_path = filedialog.askdirectory(title="Select Folder for {}".format(trait_category))
            if folder_path:
                self.trait_categories[trait_category] = self.get_valid_image_files(folder_path)
                self.create_trait_bubbles(trait_category)
                
    def create_trait_bubbles(self, trait_category):
        x = 60
        y = len(self.trait_bubbles) * 60 + 60
        
        bubble = TraitBubble(self.canvas, trait_category, x, y)
        self.trait_bubbles.append(bubble)
        
    def generate_nft(self):
        self.num_nfts = int(self.generate_entry.get())
        
        if self.trait_bubbles and self.num_nfts > 0:
            self.generated_images = []
            
            for _ in range(self.num_nfts):
                layers = sorted(self.trait_bubbles, key=lambda bubble: bubble.y)
                base_image = Image.new("RGBA", (400, 400))
                
                for bubble in layers:
                    trait_category = bubble.trait_name
                    trait_image = self.get_random_image(self.trait_categories[trait_category])
                    trait_image = trait_image.resize((400, 400))
                    base_image = Image.alpha_composite(base_image, trait_image)
                
                self.generated_images.append(base_image)
            
            self.show_image(self.generated_images[0])
        
    def get_valid_image_files(self, folder_path):
        valid_extensions = [".png", ".jpg", ".jpeg", ".gif"]
        image_files = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in valid_extensions:
                    image_files.append(os.path.join(root, file))
        
        return image_files
    
    def get_random_image(self, image_list):
        return Image.open(random.choice(image_list)).convert("RGBA")
        
    def show_image(self, image):
        image = image.resize((400, 400))
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
    
    def download_nfts(self):
        if self.generated_images:
            folder_path = filedialog.askdirectory(title="Select Folder to Save NFTs")
            if folder_path:
                zip_path = os.path.join(folder_path, "nfts.zip")
                
                with zipfile.ZipFile(zip_path, "w") as zip_file:
                    for index, image in enumerate(self.generated_images):
                        image_path = os.path.join(folder_path, f"nft_{index + 1}.png")
                        image.save(image_path)
                        zip_file.write(image_path, f"nft_{index + 1}.png")
                        os.remove(image_path)
                
                messagebox.showinfo("Download Complete", "All NFTs have been downloaded as a zip file.")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = NFTGeneratorApp(root)
    root.mainloop()
