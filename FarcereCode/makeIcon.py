from PIL import Image

img = Image.open("app.png")

img.save("app.ico", sizes=[(16,16), (32,32), (48,48)])

print("app.ico laget!")