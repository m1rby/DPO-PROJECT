from PIL import Image, ImageDraw
import os

def create_default_avatar():
    # Create a new image with a white background
    size = 200
    img = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    circle_color = (108, 92, 231)  # Primary color from your CSS
    draw.ellipse((0, 0, size, size), fill=circle_color)
    
    # Draw a user icon
    icon_color = 'white'
    # Draw a simple user icon (head and shoulders)
    draw.ellipse((size//4, size//4, size*3//4, size*3//4), fill=icon_color)  # Head
    draw.rectangle((size//3, size*3//4, size*2//3, size*7//8), fill=icon_color)  # Body
    
    # Create the directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Save the image
    img.save('static/images/default-avatar.png')

if __name__ == '__main__':
    create_default_avatar() 