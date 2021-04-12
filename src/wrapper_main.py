# Add ./DeepCreamPy into the path, so that imports work.
from sys import path
from os import getcwd
path.append(getcwd() + "/DeepCreamPy")

# Local Libraries.
from wrapper_decensor import Decensor

# External Libraries.
from PIL import Image

def main():
    decensor_instance = Decensor()
    decensor_instance.load_model()

    img = Image.open("./DeepCreamPy/readme_images/mermaid_face_censored_good.png")
    decensored_img = decensor_instance.decensor_image_variation(img, img, 0)
    decensored_img.save("./out/decensored.png")

if __name__ == "__main__":
    main()
