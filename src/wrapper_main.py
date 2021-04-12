# Add ./DeepCreamPy into the path, so that imports work.
from sys import path
from os import getcwd
path.append(getcwd() + "/DeepCreamPy")

# Local Libraries.
from wrapper_decensor import Decensor

# External Libraries.
from PIL import Image
import redis
import io

def main():
    r = redis.Redis(host="localhost", port=6379, db=0)

    # Test the connection to Redis.
    r.get("connection-test")

    decensor_instance = Decensor()
    decensor_instance.load_model()


    while True:
        print("ready to receive censored images")
        _, uuid = r.blpop("censored-images:deepcreampy:bar", 0)
        print("ready to receive censored images")

        censored_img_data = r.get("censored-images:%s" % uuid.decode())

        censored_img_file = io.BytesIO(censored_img_data)
        censored_img_file.seek(0)

        censored_img = Image.open(censored_img_file)
        decensored_img = decensor_instance.decensor_image_variation(censored_img, censored_img, 0)

        decensored_img_file = io.BytesIO()
        decensored_img.save(decensored_img_file, format="PNG")

        r.set("decensored-images:%s" % uuid.decode(), decensored_img_file.getvalue())

if __name__ == "__main__":
    main()
