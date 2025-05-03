from tkinter import *
from tkinter import filedialog, colorchooser, messagebox
from PIL import ImageTk, Image
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Global variables
text_color = "black"
bg_color = "white"
extracted_text = ""
current_image_path = ""

# Define functions
def apply_preprocessing(image, mode):
    if mode == "Grayscale":
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif mode == "Threshold":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        return thresh
    else:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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

def extract():
    global extracted_text
    if not current_image_path:
        messagebox.showwarning("Warning", "Please upload an image first!")
        return
    
    try:
        Actual_image = cv2.imread(current_image_path)
        Sample_img = cv2.resize(Actual_image, (600, 400))
        Processed_img = apply_preprocessing(Sample_img, preprocess_mode.get())

        texts = pytesseract.image_to_string(Processed_img)
        extracted_text = texts

        text_box.delete(1.0, END)
        text_box.insert(END, extracted_text)
        text_box.config(fg=text_color, bg=bg_color, font=(selected_font.get(), 14))
    except Exception as e:
        messagebox.showerror("Error", f"Error extracting text: {str(e)}")

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

def upload():
    global current_image_path
    try:
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not path:
            return
        
        current_image_path = path
        image = Image.open(path)
        
        # Limit display size
        max_display_size = (380, 280)
        image.thumbnail(max_display_size, Image.Resampling.LANCZOS)
        
        img = ImageTk.PhotoImage(image)
        uploaded_img.configure(image=img)
        uploaded_img.image = img
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not open image: {str(e)}")

# Initialize main window
root = Tk()
root.title('Extract Text from Images - Powered by Venkat')
root.geometry("1100x700")
root.config(bg="#e6f2ff")

# Configure grid layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Left Panel Frame
left_frame = Frame(root, bg="#e6f2ff", width=400)
left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
left_frame.grid_propagate(False)

# Right Panel Frame
right_frame = Frame(root, bg="white")
right_frame.grid(row=0, column=1, sticky="nsew")

# Configure left panel layout
left_frame.grid_rowconfigure(7, weight=1)

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
extract_btn = Button(left_frame, text="Extract Text", command=extract,
                    bg="#2f2f77", fg="white", width=20,
                    font=('Arial', 12, 'bold'))
extract_btn.grid(row=6, column=0, columnspan=2, pady=15)

# Save/Clear Buttons
btn_frame = Frame(left_frame, bg="#e6f2ff")
btn_frame.grid(row=7, column=0, columnspan=2, pady=20, sticky='sw')
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

root.mainloop()