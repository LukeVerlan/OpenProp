from PIL import Image, ImageTk
import tkinter as tk

root = tk.Tk()

img = Image.open("main/OpenPropLogo.png")
img = img.resize((200, 200))
tk_img = ImageTk.PhotoImage(img)

label = tk.Label(root, image=tk_img)
label.pack()

root.mainloop()
