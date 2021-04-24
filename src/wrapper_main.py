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

    decensor_bar = Decensor(is_mosaic=False)
    decensor_bar.load_model()

    decensor_mosaic = Decensor(is_mosaic=True)
    decensor_mosaic.load_model()

    while True:
        print("ready to receive decensor requests")
        key, uuid = r.blpop(["decensor-requests:bar", "decensor-requests:mosaic"], 0)
        print("received decensor request")

        masked_img_data = r.get("masked-images:%s" % uuid.decode())
        masked_img = ImageProcessor.bytes_to_image(masked_img_data)

        try:
            if key.decode() == "decensor-requests:mosaic":
                censored_img_data = r.get("censored-images:%s" % uuid.decode())
                censored_img = ImageProcessor.bytes_to_image(censored_img_data)
                decensored_img = decensor_mosaic.decensor(masked_img, censored_img)
            else:
                decensored_img = decensor_bar.decensor(masked_img)

            r.set("decensored-images:%s" % uuid.decode(), ImageProcessor.image_to_bytes(decensored_img))
        except NoMaskedRegionsFoundError as e:
            print(e.description)
            r.set("errors:%s" % uuid.decode(), e.json)

if __name__ == "__main__":
    main()
