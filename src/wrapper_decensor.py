# local library
import config
from model import InpaintNN
from libs.utils import *
from NoMaskedRegionsFoundError import NoMaskedRegionsFoundError

# external library
import numpy as np
from PIL import Image
import tensorflow as tf

class Decensor():
    def __init__(self, is_mosaic):
        args = config.get_args()
        self.mask_color = [args.mask_color_red/255.0, args.mask_color_green/255.0, args.mask_color_blue/255.0]
        self.model = None
        self.is_mosaic = is_mosaic

    def find_mask(self, colored):
        mask = np.ones(colored.shape, np.uint8)
        i, j = np.where(np.all(colored[0] == self.mask_color, axis=-1))
        mask[0, i, j] = 0
        return mask

    def load_model(self):
        if self.model is None :
            self.model = InpaintNN(bar_model_name = "../model/09-11-2019 DCPv2 model/bar/Train_775000.meta",
                                   bar_checkpoint_name = "../model/09-11-2019 DCPv2 model/bar/",
                                   mosaic_model_name = "../model/09-11-2019 DCPv2 model/mosaic/Train_290000.meta",
                                   mosaic_checkpoint_name = "../model/09-11-2019 DCPv2 model/mosaic/",
                                   is_mosaic=self.is_mosaic)
        print("load model finished")

    def decensor(self, colored, ori=None):
        if not self.is_mosaic:
            ori = colored
        
        width, height = ori.size

        #save the alpha channel if the image has an alpha channel
        has_alpha = False
        if ori.mode == "RGBA":
            has_alpha = True
            alpha_channel = np.asarray(ori)[:,:,3]
            alpha_channel = np.expand_dims(alpha_channel, axis =-1)
            ori = ori.convert("RGB")

        ori_array = image_to_array(ori)
        ori_array = np.expand_dims(ori_array, axis = 0)

        if self.is_mosaic:
            colored = colored.convert("RGB")
            color_array = image_to_array(colored)
            color_array = np.expand_dims(color_array, axis = 0)
            mask = self.find_mask(color_array)
            mask_reshaped = mask[0,:,:,:] * 255.0
            mask_img = Image.fromarray(mask_reshaped.astype("uint8"))
        else:
            mask = self.find_mask(ori_array)

        #colored image is only used for finding the regions
        regions = find_regions(colored.convert("RGB"), [v*255 for v in self.mask_color])
        print("Found {region_count} censored regions in this image!".format(region_count = len(regions)))

        if len(regions) == 0 and not self.is_mosaic:
            raise NoMaskedRegionsFoundError("No masked regions detected.")

        print("Found {} masked regions".format(len(regions)))

        output_img_array = ori_array[0].copy()

        for region_counter, region in enumerate(regions, 1):
            bounding_box = expand_bounding(ori, region, expand_factor=1.5)
            crop_img = ori.crop(bounding_box)

            #convert mask back to image
            mask_reshaped = mask[0,:,:,:] * 255.0
            mask_img = Image.fromarray(mask_reshaped.astype("uint8"))

            #resize the cropped images
            crop_img = crop_img.resize((256, 256))
            crop_img_array = image_to_array(crop_img)

            #resize the mask images
            mask_img = mask_img.crop(bounding_box)
            mask_img = mask_img.resize((256, 256))

            #convert mask_img back to array
            mask_array = image_to_array(mask_img)

            if not self.is_mosaic:
                a, b = np.where(np.all(mask_array == 0, axis = -1))
                crop_img_array[a,b,:] = 0.

            crop_img_array = np.expand_dims(crop_img_array, axis = 0)
            mask_array = np.expand_dims(mask_array, axis = 0)

            crop_img_array = crop_img_array * 2.0 - 1

            #run predictions for this batch of images
            pred_img_array = self.model.predict(crop_img_array, crop_img_array, mask_array)

            pred_img_array = np.squeeze(pred_img_array, axis = 0)
            pred_img_array = (255.0 * ((pred_img_array + 1.0) / 2.0)).astype(np.uint8)

            #scale prediction image back to original size
            bounding_width = bounding_box[2]-bounding_box[0]
            bounding_height = bounding_box[3]-bounding_box[1]

            #convert np array to image
            pred_img = Image.fromarray(pred_img_array.astype("uint8"))
            pred_img = pred_img.resize((bounding_width, bounding_height), resample = Image.BICUBIC)

            pred_img_array = image_to_array(pred_img)
            pred_img_array = np.expand_dims(pred_img_array, axis = 0)

            #copy the decensored regions into the output image
            for i in range(len(ori_array)):
                for col in range(bounding_width):
                    for row in range(bounding_height):
                        bounding_width_index = col + bounding_box[0]
                        bounding_height_index = row + bounding_box[1]
                        if (bounding_width_index, bounding_height_index) in region:
                            output_img_array[bounding_height_index][bounding_width_index] = pred_img_array[i,:,:,:][row][col]

            print("{region_counter} out of {region_count} regions decensored.".format(region_counter=region_counter, region_count=len(regions)))

        output_img_array = output_img_array * 255.0

        #restore the alpha channel if the image had one
        if has_alpha:
            output_img_array = np.concatenate((output_img_array, alpha_channel), axis = 2)

        output_img = Image.fromarray(output_img_array.astype("uint8"))

        print("current image finished")

        print("Decensored image. Returning it.")
        return output_img
