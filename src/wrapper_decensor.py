
# default library
import os, logging, sys

# local library
import config
from model import InpaintNN
from libs.utils import *

# external library
import numpy as np
from PIL import Image
import tensorflow as tf

class Decensor():
    def __init__(self):
        args = config.get_args()
        self.is_mosaic = False
        self.variations = 1
        self.mask_color = [args.mask_color_red/255.0, args.mask_color_green/255.0, args.mask_color_blue/255.0]
        self.decensor_input_path = args.decensor_input_path
        self.decensor_input_original_path = args.decensor_input_original_path
        self.decensor_output_path = args.decensor_output_path

        self.model = None

    def init(self):
        self.load_model()

    def find_mask(self, colored):
        mask = np.ones(colored.shape, np.uint8)
        i, j = np.where(np.all(colored[0] == self.mask_color, axis=-1))
        mask[0, i, j] = 0
        return mask

    def load_model(self):
        if self.model is None :
            self.model = InpaintNN(bar_model_name = "./DeepCreamPy/erogaki-models/09-11-2019 DCPv2 model/bar/Train_775000.meta",
                                   bar_checkpoint_name = "./DeepCreamPy/erogaki-models/09-11-2019 DCPv2 model/bar/",
                                   mosaic_model_name = "./DeepCreamPy/erogaki-models/09-11-2019 DCPv2 model/mosaic/Train_290000.meta",
                                   mosaic_checkpoint_name = "./DeepCreamPy/erogaki-models/09-11-2019 DCPv2 model/models/mosaic/",
                                   is_mosaic=self.is_mosaic)
        print("load model finished")

    def decensor_image_variations(self, ori, colored):
        for i in range(self.variations):
            self.decensor_image_variation(ori, colored, i)

    #create different decensors of the same image by flipping the input image
    def apply_variant(self, image, variant_number):
        if variant_number == 0:
            return image
        elif variant_number == 1:
            return image.transpose(Image.FLIP_LEFT_RIGHT)
        elif variant_number == 2:
            return image.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            return image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)

    #decensors one image at a time
    #TODO: decensor all cropped parts of the same image in a batch (then i need input for colored an array of those images and make additional changes)
    def decensor_image_variation(self, ori, colored, variant_number):
        ori = self.apply_variant(ori, variant_number)
        colored = self.apply_variant(colored, variant_number)
        width, height = ori.size
        #save the alpha channel if the image has an alpha channel
        has_alpha = False
        if (ori.mode == "RGBA"):
            has_alpha = True
            alpha_channel = np.asarray(ori)[:,:,3]
            alpha_channel = np.expand_dims(alpha_channel, axis =-1)
            ori = ori.convert("RGB")

        ori_array = image_to_array(ori)
        ori_array = np.expand_dims(ori_array, axis = 0)

        mask = self.find_mask(ori_array)

        #colored image is only used for finding the regions
        regions = find_regions(colored.convert("RGB"), [v*255 for v in self.mask_color])
        print("Found {region_count} censored regions in this image!".format(region_count = len(regions)))

        if len(regions) == 0 and not self.is_mosaic:
            print("No green (0,255,0) regions detected! Make sure you're using exactly the right color.")
            return
            # ToDo: Error

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

            a, b = np.where(np.all(mask_array == 0, axis = -1))
            crop_img_array[a,b,:] = 0.

            crop_img_array = np.expand_dims(crop_img_array, axis = 0)
            mask_array = np.expand_dims(mask_array, axis = 0)

            crop_img_array = crop_img_array * 2.0 - 1

            # Run predictions for this batch of images
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

            # copy the decensored regions into the output image
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
        output_img = self.apply_variant(output_img, variant_number)

        print("current image finished")

        print("Decensored image. Returning it.")
        return output_img
