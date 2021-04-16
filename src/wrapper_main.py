# Add ./DeepCreamPy into the path, so that imports work.
from sys import path
from os import getcwd
path.append(getcwd() + "/DeepCreamPy")

# Local Libraries.
from wrapper_decensor import Decensor
from NoMaskedRegionsFoundError import NoMaskedRegionsFoundError

# External Libraries.
import redis
import io
from erogaki_wrapper_shared_python.ErogakiWrapperConfig import config
from erogaki_wrapper_shared_python.ImageProcessor import ImageProcessor

def main():
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
            decensored_img = decensor_instance.decensor_image(ImageProcessor.bytes_to_image(censored_img_data))
            r.set("decensored-images:%s" % uuid.decode(), ImageProcessor.image_to_bytes(decensored_img))
        except NoMaskedRegionsFoundError as e:
            print(e.description)
            r.set("errors:%s" % uuid.decode(), e.json)

if __name__ == "__main__":
    main()
