from PIL import Image
import numpy as np

def eng(i, j, img):
    if i>=len(img[0])-2 or i == 0 \
        or j>=len(img)-2 or j == 0:
        return 10000000
    sobel_hor = img[j-1][i-1] + 2*img[j][i-1] + img[j+1][i-1] + \
                -img[j-1][i+1] + -2*img[j][i+1] + -img[j+1][i+1]
    sobel_ver = img[j-1][i-1] + 2*img[j-1][i] + img[j-1][i+1] + \
                -img[j+1][i-1] + -2*img[j+1][i] + -img[j+1][i+1]
    return sobel_hor + sobel_ver

# img[h][w]
def carve_vertical(img):
    h = len(img)
    w = len(img[0])
    e = np.zeros((h,w))
    c = np.zeros((h,w))
    p = np.zeros((h,w,2))
    for j in range(h):
        for i in range(w):
            e[j][i] = eng(i,j,img)
    e = e / 1050
    for i in range(w):
        c[0,i] = e[0,i]
        p[0,i] = (-1,-1)

    for j in range(1,h):
        for i in range(0,w):
            c[j,i] = c[j-1,i]
            p[j,i] = (j-1,i)
            if i > 0 and c[j-1,i-1] < c[j,i] and c[j-1,i-1] > 0:
                c[j,i] = c[j-1,i-1]
                p[j,i] = (j-1,i-1)
            if i < w-1 and c[j-1,i+1] < c[j,i] and c[j-1,i+1] > 0:
                c[j,i] = c[j-1,i+1]
                p[j,i] = (j-1,i+1)
            c[j,i] += e[j,i]
    pos = (5,5)
    for i in range(w):
        if c[pos] < c[h-1,i] and c[h-1,i] > 0:
            pos = (j,i)
            
    seam = [(pos[0], pos[1])]
    for j in range(h-2, -1, -1):
        seam.append((int(p[pos][0]//1), int(p[pos][1]//1)))
        pos = (int(p[pos][0]//1), int(p[pos][1]//1))
    return seam

def delete_seam(seam, img):
    h = len(img)
    w = len(img[0])
    _img = np.zeros((h,w-1))
    i_adj = 0
    for j in range(h):
        i_adj = 0
        for i in range(w-1):
            if (j,i) in seam:
                i_adj=1
            _img[j,i] = img[j,i+i_adj]
    return _img 


def dupe_seam(seam, img):
    h = len(img)
    w = len(img[0])
    _img = np.zeros((h,w+1))
    for j in range(h):
        i_adj = 0
        for i in range(w):
            if (j,i) in seam:
                _img[j,i] = img[j,i]
                i_adj=1
            _img[j,i+i_adj] = img[j,i]
    return _img 


def seam_carve_ver(new_width, img):
    _img = np.array(img)

    if new_width > img.width:
        n = new_width - img.width
        for i in range(n):
            print(i)
            seam = carve_vertical(_img)
            _img = dupe_seam(seam , _img)
    else:
        n = img.width - new_width
        for i in range(n):
            print(i)
            seam = carve_vertical(_img)
            _img = delete_seam(seam , _img)

    return Image.fromarray(_img)


def seam_carve_hor(new_height, img):
    img = img.rotate(90, expand=True)
    print('hor')
    img = seam_carve_ver(new_height, img)
    img = img.rotate(270, expand=True)
    return img

def seam_carve(new_size, img):
    img = seam_carve_ver(new_size[0], img)
    return seam_carve_hor(new_size[1], img)
    

img = Image.open('photo.jpeg').convert("L")
img = img.resize((img.width//4, img.height//4))
img.show()

img = seam_carve((img.width+10, img.height-10), img)

img.show()