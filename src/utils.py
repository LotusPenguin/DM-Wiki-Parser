from datetime import datetime
from dependencies.realesrgan import inference_realesrgan
import os


class stringButBetter(str):
    def __new__(cls, *args, **kw):
        return str.__new__(cls, *args, **kw)

    def replace(self, __old, __new, __count=-1):
        return stringButBetter(str.replace(self, __old, __new, __count))

    def strip(self, __chars=None):
        return stringButBetter(str.strip(self, __chars))

    def replace_nth(self, __old, __new, __nth):
        arr = self.split(__old)
        i = 0
        result = ''
        for token in arr:
            i += 1
            if i < __nth:
                result += token + __old
            elif i == __nth and i < len(arr):
                result += token + __new
            elif __nth < i < len(arr):
                result += token + __old
            else:
                result += token
        return stringButBetter(result)

    def replace_nth_and_further(self, __old, __new, __nth):
        arr = self.split(__old)
        i = 0
        result = ''
        for token in arr:
            i += 1
            if i < __nth:
                result += token + __old
            elif __nth <= i < len(arr):
                result += token + __new
            else:
                result += token
        return stringButBetter(result)


def println(*to_print):
    print((datetime.now()).strftime("[%H:%M:%S] "), end='')
    print(*to_print)


def upscaleCatalog(input_directory, upscaled_image_directory, setName="Upscaled"):
    if not os.path.exists(input_directory):
        println("Error: invalid input directory")

    for image_file in os.listdir(input_directory):
        image_path = os.path.join(input_directory, image_file)
        if not os.path.isfile(image_path):
            continue
        inference_realesrgan.upscale(setName, image_path, upscaled_image_directory)


if __name__ == '__main__':
    upscaleCatalog("C:\\Users\\Pingwin\\Desktop\\temp", "C:\\Users\\Pingwin\\Desktop\\Upscaled_temp")