# Add ./DeepCreamPy into the path, so that imports work.
from sys import path
from os import getcwd
path.append(getcwd() + "/DeepCreamPy")

# Local Libraries.
from wrapper_decensor import Decensor
from NoRegionsFoundError import NoRegionsFoundError

# External Libraries.
from PIL import Image
import redis
import io
from erogaki_wrapper_shared_python.ErogakiWrapperConfig import ErogakiWrapperConfig

# convert encoded image file to PIL image object
def bytes_to_image(bytes):
    img_file = io.BytesIO(bytes)
    img_file.seek(0)
    return Image.open(img_file)

# convert PIL image object to PNG
def image_to_bytes(image):
    img_file = io.BytesIO()
    image.save(img_file, format="PNG")
    return img_file.getvalue()

def main():
    config = ErogakiWrapperConfig()
    r = redis.Redis(host=config.redis.hostname, port=config.redis.port, db=config.redis.db)

    # Test the connection to Redis.
    r.get("connection-test")

    decensor_instance = Decensor()
    decensor_instance.load_model()

    while True:
        print("ready to receive censored images")
        _, uuid = r.blpop("censored-images:deepcreampy:bar", 0)
        print("received censored image")

        censored_img_data = r.get("censored-images:%s" % uuid.decode())
        try:
            decensored_img = decensor_instance.decensor_image(bytes_to_image(censored_img_data))
            r.set("decensored-images:%s" % uuid.decode(), image_to_bytes(decensored_img))
        except NoRegionsFoundError as e:
            print(e.message)

if __name__ == "__main__":
    main()
