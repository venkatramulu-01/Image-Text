from tkinter import *
from tkinter import filedialog, colorchooser, messagebox
from PIL import ImageTk, Image
import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

root = Tk()
root.title('Extract Text from Images - Powered by Venkat')
root.geometry('900x700')
root.config(bg="#e6f2ff")

# Configure grid weights for responsive layout
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Main frames
top_frame = Frame(root, bg="#e6f2ff")
top_frame.grid(row=0, column=0, sticky="nsew")

bottom_frame = Frame(root, bg="#e6f2ff")
bottom_frame.grid(row=1, column=0, sticky="nsew")
bottom_frame.grid_rowconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(0, weight=1)

# Title
title = Label(top_frame, text="Text Extraction App", font=('Arial', 24, 'bold'), 
              fg="#003366", bg="#e6f2ff")
title.grid(row=0, column=0, columnspan=3, pady=10)

# Upload button
uploadbtn = Button(top_frame, text="Upload Image", command=lambda: upload(), 
                  bg="#2f2f77", fg="white", height=2, width=20, 
                  font=('Arial', 13, 'bold'))
uploadbtn.grid(row=1, column=0, columnspan=3, pady=10)

# Image display
uploaded_img = Label(top_frame, bg="#e6f2ff")
uploaded_img.grid(row=2, column=0, columnspan=3, pady=10)

# Font Selection
Label(top_frame, text="Select Font:", bg="#e6f2ff", 
      font=('Arial', 12, 'bold')).grid(row=3, column=0, sticky="e", padx=5)

selected_font = StringVar()
selected_font.set("Times")
fonts = ["Times", "Arial", "Comic Sans MS", "Courier", "Helvetica", "Verdana"]
font_menu = OptionMenu(top_frame, selected_font, *fonts)
font_menu.grid(row=3, column=1, sticky="w")

# Preprocessing Mode
Label(top_frame, text="Preprocessing:", bg="#e6f2ff", 
      font=('Arial', 12, 'bold')).grid(row=4, column=0, sticky="e", padx=5)

preprocess_mode = StringVar()
preprocess_mode.set("Normal")
mode_menu = OptionMenu(top_frame, preprocess_mode, "Normal", "Grayscale", "Threshold")
mode_menu.grid(row=4, column=1, sticky="w")

# Color buttons
Button(top_frame, text="Text Color", command=lambda: choose_text_color(), 
       bg="#2f2f77", fg="white", pady=5, padx=10, 
       font=('Arial', 10)).grid(row=3, column=2, padx=10)

Button(top_frame, text="BG Color", command=lambda: choose_bg_color(), 
       bg="#2f2f77", fg="white", pady=5, padx=10, 
       font=('Arial', 10)).grid(row=4, column=2, padx=10)

# Extract button (will be shown after upload)
extractBtn = Button(top_frame, text="Extract Text", command=lambda: extract(), 
                   bg="#2f2f77", fg="white", pady=10, padx=20, 
                   font=('Arial', 13, 'bold'))
extractBtn.grid(row=5, column=0, columnspan=3, pady=10)
extractBtn.grid_remove()  # Hidden initially

# Text box with scrollbar
text_box = Text(bottom_frame, wrap=WORD, font=('Times', 14))
text_scroll = Scrollbar(bottom_frame, command=text_box.yview)
text_box.config(yscrollcommand=text_scroll.set)

text_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
text_scroll.grid(row=0, column=1, sticky="ns")

# Action buttons frame
action_frame = Frame(bottom_frame, bg="#e6f2ff")
action_frame.grid(row=1, column=0, columnspan=2, pady=10)

Button(action_frame, text="Save Text", command=lambda: save_text(), 
       bg="#2f2f77", fg="white", pady=5, padx=10, 
       font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10)

Button(action_frame, text="Clear Text", command=lambda: clear_text(), 
       bg="#2f2f77", fg="white", pady=5, padx=10, 
       font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10)

# Global variables
text_color = "black"
bg_color = "white"
extracted_text = ""
current_image_path = ""

def apply_preprocessing(image, mode):
    if mode == "Grayscale":
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif mode == "Threshold":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        return thresh
    else:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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
        
        # Limit display size while maintaining aspect ratio
        max_display_size = (400, 300)
        image.thumbnail(max_display_size, Image.Resampling.LANCZOS)
        
        img = ImageTk.PhotoImage(image)
        uploaded_img.configure(image=img)
        uploaded_img.image = img
        
        # Show extract button
        extractBtn.grid()
    except Exception as e:
        messagebox.showerror("Error", f"Could not open image: {str(e)}")

root.mainloop()