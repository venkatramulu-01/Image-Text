from tkinter import *
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import pytesseract
import threading
import time
from queue import Queue

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Global variables
text_color = "black"
bg_color = "white"
extracted_text = ""
current_image_path = ""
processing_queue = Queue()
camera_running = False
last_captured_frame = None
camera_captured_image = None

# Initialize main window
root = Tk()
root.title('Extract Text from Images')
root.geometry("1100x700")
root.config(bg="#e6f2ff")

# Configure grid layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Create frames
left_frame = Frame(root, bg="#e6f2ff", width=400)
left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
left_frame.grid_propagate(False)

right_frame = Frame(root, bg="white")
right_frame.grid(row=0, column=1, sticky="nsew")

# Configure left panel layout
left_frame.grid_rowconfigure(9, weight=1)

# Function definitions
def apply_preprocessing(image, mode):
    if mode == "Grayscale":
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif mode == "Threshold":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        return thresh
    else:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def update_preview():
    if current_image_path:
        try:
            image = cv2.imread(current_image_path)
            image = cv2.resize(image, (600, 400))
            processed = apply_preprocessing(image, preprocess_mode.get())
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(processed)
            img.thumbnail((380, 280))
            img_tk = ImageTk.PhotoImage(img)
            uploaded_img.configure(image=img_tk)
            uploaded_img.image = img_tk
        except Exception as e:
            print(f"Preview error: {str(e)}")

def process_queue():
    while not processing_queue.empty():
        try:
            processing_queue.get_nowait()()
        except:
            pass
    root.after(100, process_queue)

def real_time_extraction():
    if current_image_path or camera_captured_image is not None:
        try:
            start_time = time.time()
            if camera_captured_image is not None:
                processed = apply_preprocessing(camera_captured_image, preprocess_mode.get())
                texts = pytesseract.image_to_string(processed)
            else:
                Actual_image = cv2.imread(current_image_path)
                Sample_img = cv2.resize(Actual_image, (600, 400))
                Processed_img = apply_preprocessing(Sample_img, preprocess_mode.get())
                texts = pytesseract.image_to_string(Processed_img)
            
            text_box.delete(1.0, END)
            text_box.insert(END, texts)
            text_box.config(fg=text_color, bg=bg_color, font=(selected_font.get(), 14))
            status_label.config(text=f"Processed in {time.time() - start_time:.2f}s")
        except Exception as e:
            messagebox.showerror("Error", f"Processing error: {str(e)}")

def choose_text_color():
    global text_color
    color = colorchooser.askcolor(title="Choose Text Color")
    if color[1]:
        text_color = color[1]
        text_box.config(fg=text_color)

def choose_bg_color():
    global bg_color
    color = colorchooser.askcolor(title="Choose Background Color")
    if color[1]:
        bg_color = color[1]
        text_box.config(bg=bg_color)

def start_live_capture():
    global camera_running
    camera_running = True
    threading.Thread(target=capture_frames, daemon=True).start()

def stop_live_capture():
    global camera_running, camera_captured_image, last_captured_frame
    camera_running = False
    if last_captured_frame is not None:
        camera_captured_image = last_captured_frame.copy()
    if uploaded_img.image:
        img = ImageTk.getimage(uploaded_img.image)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Captured - Click Extract", fill="red")
        img_tk = ImageTk.PhotoImage(img)
        uploaded_img.configure(image=img_tk)
        uploaded_img.image = img_tk

def capture_frames():
    global last_captured_frame
    cap = cv2.VideoCapture(0)
    while camera_running:
        ret, frame = cap.read()
        if ret:
            last_captured_frame = frame.copy()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img.thumbnail((380, 280))
            img_tk = ImageTk.PhotoImage(img)
            uploaded_img.configure(image=img_tk)
            uploaded_img.image = img_tk
            processing_queue.put(lambda: process_frame(frame))
            time.sleep(0.1)
    cap.release()

def process_frame(frame):
    try:
        processed = apply_preprocessing(frame, preprocess_mode.get())
        texts = pytesseract.image_to_string(processed)
        text_box.delete(1.0, END)
        text_box.insert(END, texts)
        text_box.config(fg=text_color, bg=bg_color, font=(selected_font.get(), 14))
    except Exception as e:
        print(f"Frame processing error: {str(e)}")

def save_text():
    if not extracted_text.strip():
        messagebox.showwarning("Warning", "No text to save!")
        return
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                filetypes=[("Text files", "*.txt"), 
                                                          ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(extracted_text)
            messagebox.showinfo("Success", "Text saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")

def clear_text():
    text_box.delete(1.0, END)

def clear_camera_capture():
    global camera_captured_image, last_captured_frame
    camera_captured_image = None
    last_captured_frame = None
    uploaded_img.config(image='')
    uploaded_img.image = None
    text_box.delete(1.0, END)
    status_label.config(text="Camera capture cleared")

def upload():
    global current_image_path, camera_captured_image
    clear_camera_capture()
    try:
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not path:
            return
        current_image_path = path
        image = Image.open(path)
        max_display_size = (380, 280)
        image.thumbnail(max_display_size, Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(image)
        uploaded_img.configure(image=img)
        uploaded_img.image = img
    except Exception as e:
        messagebox.showerror("Error", f"Could not open image: {str(e)}")

# GUI Elements
# Title
title = Label(left_frame, text="Text Extraction App", 
             font=('Arial', 20, 'bold'), fg="#003366", bg="#e6f2ff")
title.grid(row=0, column=0, columnspan=2, pady=15)

# Upload Section
upload_btn = Button(left_frame, text="Upload Image", command=upload,
                   bg="#2f2f77", fg="white", width=20,
                   font=('Arial', 12, 'bold'))
upload_btn.grid(row=1, column=0, columnspan=2, pady=10)

# Image display
uploaded_img = Label(left_frame, bg="#e6f2ff")
uploaded_img.grid(row=2, column=0, columnspan=2, pady=10)

# Font Selection
Label(left_frame, text="Font Style:", bg="#e6f2ff",
     font=('Arial', 11)).grid(row=3, column=0, sticky='w', padx=10)
selected_font = StringVar()
selected_font.set("Times")
fonts = ["Times", "Arial", "Comic Sans MS", "Courier", "Helvetica", "Verdana"]
font_menu = OptionMenu(left_frame, selected_font, *fonts)
font_menu.grid(row=3, column=1, sticky='ew', padx=10, pady=5)

# Preprocessing Mode
Label(left_frame, text="Preprocessing:", bg="#e6f2ff",
     font=('Arial', 11)).grid(row=4, column=0, sticky='w', padx=10)
preprocess_mode = StringVar()
preprocess_mode.set("Normal")
mode_menu = OptionMenu(left_frame, preprocess_mode, "Normal", "Grayscale", "Threshold")
mode_menu.grid(row=4, column=1, sticky='ew', padx=10, pady=5)

# Color Buttons
color_frame = Frame(left_frame, bg="#e6f2ff")
color_frame.grid(row=5, column=0, columnspan=2, pady=10)
Button(color_frame, text="Text Color", command=choose_text_color,
      bg="#2f2f77", fg="white", width=10).pack(side=LEFT, padx=5)
Button(color_frame, text="BG Color", command=choose_bg_color,
      bg="#2f2f77", fg="white", width=10).pack(side=LEFT, padx=5)

# Extract Button
extract_btn = Button(left_frame, text="Extract Text", command=real_time_extraction,
                    bg="#2f2f77", fg="white", width=20,
                    font=('Arial', 12, 'bold'))
extract_btn.grid(row=6, column=0, columnspan=2, pady=15)

# Status Label
status_label = Label(left_frame, text="Ready", bg="#e6f2ff", fg="#003366")
status_label.grid(row=7, column=0, columnspan=2, pady=10)

# Camera Controls
camera_frame = Frame(left_frame, bg="#e6f2ff")
camera_frame.grid(row=8, column=0, columnspan=2, pady=10)
Button(camera_frame, text="Start Camera", command=start_live_capture,
      bg="#2f2f77", fg="white", width=12).pack(side=LEFT, padx=5)
Button(camera_frame, text="Stop Camera", command=stop_live_capture,
      bg="#2f2f77", fg="white", width=12).pack(side=LEFT, padx=5)
Button(camera_frame, text="Clear Capture", command=clear_camera_capture,
      bg="#2f2f77", fg="white", width=12).pack(side=LEFT, padx=5)

# Save/Clear Buttons
btn_frame = Frame(left_frame, bg="#e6f2ff")
btn_frame.grid(row=9, column=0, columnspan=2, pady=20, sticky='sw')
Button(btn_frame, text="Save Text", command=save_text,
       bg="#2f2f77", fg="white", width=10).pack(side=LEFT, padx=10)
Button(btn_frame, text="Clear Text", command=clear_text,
       bg="#2f2f77", fg="white", width=10).pack(side=LEFT, padx=10)

# Right Panel Text Area
text_box = Text(right_frame, wrap=WORD, font=('Times', 14), padx=10, pady=10)
text_scroll = Scrollbar(right_frame)
text_scroll.pack(side=RIGHT, fill=Y)
text_box.pack(expand=True, fill=BOTH)
text_scroll.config(command=text_box.yview)
text_box.config(yscrollcommand=text_scroll.set)

# Real-time updates
preprocess_mode.trace_add("write", lambda *args: processing_queue.put(update_preview))
selected_font.trace_add("write", lambda *args: processing_queue.put(real_time_extraction))

# Start processing thread
root.after(100, process_queue)

root.mainloop()