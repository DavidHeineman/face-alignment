import numpy as np
from PIL import Image
import dlib

def shape_to_normal(shape):
    shape_normal = []
    for i in range(0, 5):
        shape_normal.append((i, (shape.part(i).x, shape.part(i).y)))
    return shape_normal

def get_eyes_nose_dlib(shape):
    nose = shape[4][1]
    left_eye_x = int(shape[3][1][0] + shape[2][1][0]) // 2
    left_eye_y = int(shape[3][1][1] + shape[2][1][1]) // 2
    right_eyes_x = int(shape[1][1][0] + shape[0][1][0]) // 2
    right_eyes_y = int(shape[1][1][1] + shape[0][1][1]) // 2
    return nose, (left_eye_x, left_eye_y), (right_eyes_x, right_eyes_y)

def distance(a, b):
    return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def cosine_formula(length_line1, length_line2, length_line3):
    return -(length_line3 ** 2 - length_line2 ** 2 - length_line1 ** 2) / (2 * length_line2 * length_line1)

def rotate_point(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
    return qx, qy

def is_between(point1, point2, point3, extra_point):
    c1 = (point2[0] - point1[0]) * (extra_point[1] - point1[1]) - (point2[1] - point1[1]) * (extra_point[0] - point1[0])
    c2 = (point3[0] - point2[0]) * (extra_point[1] - point2[1]) - (point3[1] - point2[1]) * (extra_point[0] - point2[0])
    c3 = (point1[0] - point3[0]) * (extra_point[1] - point3[1]) - (point1[1] - point3[1]) * (extra_point[0] - point3[0])
    return (c1 < 0 and c2 < 0 and c3 < 0) or (c1 > 0 and c2 > 0 and c3 > 0)
    
def center_zoom(img, zoom):
    x, y = img.size[0]/2, img.size[1]/2
    w, h = img.size
    img = img.crop((x - w / (zoom * 2), y - h / (zoom * 2), 
                    x + w / (zoom * 2), y + h / (zoom * 2)))
    return img.resize((w, h), Image.LANCZOS)

def draw_circle(point, radius, draw_obj, color=128):
    draw_obj.ellipse((point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius), fill=color)
    
# Calculate angle of rotation to center eyes
def calculate_angle(face, center_of_forehead, nose):
    x, y, w, h = face.left(), face.top(), face.right(), face.bottom()
    center_pred = (int((x + w) / 2), int((y + y) / 2))
    length_line1 = distance(center_of_forehead, nose)
    length_line2 = distance(center_pred, nose)
    length_line3 = distance(center_pred, center_of_forehead)
    cos_a = cosine_formula(length_line1, length_line2, length_line3)
    angle = np.arccos(cos_a)
    rotated_point = rotate_point(nose, center_of_forehead, angle)
    rotated_point = (int(rotated_point[0]), int(rotated_point[1]))
    if is_between(nose, center_of_forehead, center_pred, rotated_point):
        return np.degrees(-angle)
    else:
        return np.degrees(angle)    

def center_image(img, point):
    return img.rotate(0, translate=(img.size[0]/2 - point[0], img.size[1]/2 - point[1]))

def midpoint(p1, p2):
    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

def crop(img):
    if img.size[0] / img.size[1] < 16 / 9:
        # too tall
        n_h = img.size[0] * 9 / 16
        deltah = (img.size[1] - n_h) / 2
        return img.crop((0, deltah, img.size[0], img.size[1] - deltah))
    # too wide
    n_w = img.size[1] * 16 / 9
    deltah = (img.size[0] - n_w) / 2
    return img.crop((deltah, 0, img.size[0] - deltah, img.size[1]))
    
def scale(img):
    return img.resize((1920, 1080), Image.ANTIALIAS)

def correct_orientation(img):
    rotate_vals = {3: 180, 6: 270, 8: 90}
    
    try:
        exif = img.getexif()
    except AttributeError as e:
        return img
    
    if 274 in exif:
        o = exif[274]
        if o in rotate_vals:
            # img loses Image object metadata, since a new object is being created
            print('Rotated photo')
            temp = f'photos/rotated_{img.filename[7:-4]}.jpg'
            new = ImageOps.exif_transpose(img)
            new.save(temp)
            new.filename = temp
            return new
    return img