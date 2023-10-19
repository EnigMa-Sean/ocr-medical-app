import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
import imutils
# import math
# from PIL import Image
#import skimage.exposure

class GeneratingNoise:

    def __init__(self, image_path):
        self.__image_path = image_path
        self.__image_shape = cv2.imread(self.__image_path).shape

    def blur_image(self):
        img = cv2.imread(self.__image_path, cv2.COLOR_GRAY2BGR)
        kernel_size:int = 5
        blur_img = cv2.GaussianBlur(img,(kernel_size,kernel_size),0)

        return blur_img

    def rotate_image(self):
        img = cv2.imread(self.__image_path, cv2.COLOR_GRAY2BGR)
        rand_angle: int = random.randint(-3,3)
        if(rand_angle<0):
            rand_angle = 360 + rand_angle
        rotate_img = imutils.rotate(img, rand_angle)

        return rotate_img


    def add_noise_image(self):
        img = cv2.imread(self.__image_path, cv2.COLOR_GRAY2BGR)
        mean = random.randint(0,1)
        stddev = random.randint(0,5)
        # print(mean)
        # print(stddev)
        noise = np.random.normal(mean, stddev, img.shape).astype(np.uint8)
        noisy_image = cv2.add(img, noise)

        return noisy_image


    def generate_shadow_coordinates(self, no_of_shadows: int =1):    
        vertices_list=[]    
        for index in range(no_of_shadows):        
            vertex=[]        
            for dimensions in range(np.random.randint(3, 15)): ## Dimensionality of the shadow polygon            
                vertex.append(( self.__image_shape[1]*np.random.uniform(),self.__image_shape[0]//3+self.__image_shape[0]*np.random.uniform()))        
                vertices = np.array([vertex], dtype=np.int32) ## single shadow vertices         
                vertices_list.append(vertices)    

        return vertices_list ## List of shadow vertices

    def add_shadow(self, no_of_shadows: int =1):  
        img = cv2.imread(self.__image_path).astype(np.uint8)
        image_HLS = cv2.cvtColor(img,cv2.COLOR_RGB2HLS) ## Conversion to HLS    
        mask = np.zeros_like(img)     
        vertices_list= self.generate_shadow_coordinates(no_of_shadows) #3 getting list of shadow vertices    
        for vertices in vertices_list:         
            cv2.fillPoly(mask, vertices, 255) ## adding all shadow polygons on empty mask, single 255 denotes only red channel        
            image_HLS[:,:,1][mask[:,:,0]==255] = image_HLS[:,:,1][mask[:,:,0]==255]*0.95   ## if red channel is hot, image's "Lightness" channel's brightness is lowered     
        image_RGB = cv2.cvtColor(image_HLS, cv2.COLOR_HLS2RGB) ## Conversion to RGB  

        return image_RGB

    def add_fake_light(self, light_color: tuple =(255, 255, 255), intensity: float =0.5):
        img =  cv2.imread(self.__image_path)
        mask = np.full_like(img, light_color, dtype=np.uint8)
        result = cv2.addWeighted(img, 1 - intensity, mask, intensity, 0)

        return result

    def wrinkle_image(self):
        img = cv2.imread(self.__image_path).astype("float32") / 255.0
        hh, ww = img.shape[:2]

        # read wrinkle image as grayscale and convert to float in range 0 to 1
        wrinkles = cv2.imread('noisy_images/wrinkles.jpg',0).astype("float32") / 255.0
        wrinkles = cv2.resize(wrinkles, (ww,hh), fx=0, fy=0)
        wrinkles = 1.33 * wrinkles -0.33

        # threshold wrinkles and invert
        thresh = cv2.threshold(wrinkles,0.5,1,cv2.THRESH_BINARY)[1]
        thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR) 
        thresh_inv = 1-thresh

        # shift image brightness so mean is mid gray
        mean = np.mean(wrinkles)
        shift = mean - 0.7
        wrinkles = cv2.subtract(wrinkles, shift)

        # convert wrinkles from grayscale to rgb
        wrinkles = cv2.cvtColor(wrinkles,cv2.COLOR_GRAY2BGR) 

        # do hard light composite and convert to uint8 in range 0 to 255
        low = 2.0 * img * wrinkles
        high = 1 - 2.0 * (1-img) * (1-wrinkles)
        wrinkle_img = ( 255 * (low * thresh_inv + high * thresh) ).clip(0, 255).astype(np.uint8)

        return wrinkle_img

if __name__ == '__main__':

    path = 'images/document_template.jpg'
    gen_noise = GeneratingNoise(path)
    blur_img = gen_noise.blur_image()
    rotate_img = gen_noise.rotate_image()
    noisy_img = gen_noise.add_noise_image()
    light_img = gen_noise.add_fake_light()
    wrinkle_img = gen_noise.wrinkle_image()
    add_shadow_img = gen_noise.add_shadow()
    # plt.imshow(rotate_img) 
    # plt.show() 

    # cv2.imwrite('noisy_images/blurry_image.jpg', blur_img)
    # cv2.imwrite('noisy_images/rotated_image.jpg', rotate_img)
    # cv2.imwrite('noisy_images/noisy_image.jpg', noisy_img)
    # cv2.imwrite('noisy_images/high_exposure_image.jpg', light_img)
    # cv2.imwrite('noisy_images/wrinkled_image.jpg', wrinkle_img)
    # cv2.imwrite('noisy_images/dark_image.jpg', add_shadow_img)