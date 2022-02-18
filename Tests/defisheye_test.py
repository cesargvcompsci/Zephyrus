from defisheye import Defisheye

dtype = 'linear'
format = 'fullframe'
fov = 180
pfov = 140

img = "fisheye_test.jpg"
img_out = f"example3_{dtype}_{format}_{pfov}_{fov}.jpg"

obj = Defisheye(img, dtype=dtype, format=format, fov=fov, pfov=pfov)
obj.convert(img_out)