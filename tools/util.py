def xyFromLoc(loc, width):
    x = loc % width
    y = (loc - x) / width
    return x, y

def remap(value, min1, max1, min2, max2):
    return np.interp(value, [min1, max1], [min2, max2])

def remap2(value, min1, max1, min2, max2):
    range1 = max1 - min1
    range2 = max2 - min2
    valueScaled = float(value - min1) / float(range1)
    return min2 + (valueScaled * range2)

def changeExtension(_url, _newExt, _append=None):
    returns = ""
    returnsPathArray = _url.split(".")
    for i in range(0, len(returnsPathArray)-1):
        returns += returnsPathArray[i]
    if (_append != None):
        returns += _append
    returns += _newExt

    print ("New url: " + returns)
    return returns

# https://blender.stackexchange.com/questions/241001/packing-float32-to-vertex-color
def fract(x):
    return x - np.floor(x)
    
def kinectDepthToRgb(depth):
    r = 0
    g = 0
    b = 0

    #v = depth / 2047.0 # we assume this is already normalized here
    #v = float(math.pow(v, 3) * 6.0)
    v = float(pow(depth, 3) * 6.0)
    v = v * 6.0 * 256.0

    pval = int(round(v))
    lb = pval & 0xff
  
    if (pval >> 8 == 0):
        b = 255
        g = 255-lb
        r = 255-lb
    elif (pval >> 8 == 1):
        b = 255
        g = lb
        r = 0
    elif (pval >> 8 == 2):
        b = 255-lb
        g = 255
        r = 0
    elif (pval >> 8 == 3):
        b = 0
        g = 255
        r = lb
    elif (pval >> 8 == 4):
        b = 0
        g = 255-lb
        r = 255
    elif (pval >> 8 == 5):
        b = 0
        g = 0
        r = 255-lb
    else:
        r = 0
        g = 0
        b = 0

    pixel = (r, g, b)#(0xFF) << 24 | (b & 0xFF) << 16 | (g & 0xFF) << 8 | (r & 0xFF) << 0
    #print(pixel)
    return pixel

def packIntToColor(val):
    val_i = int(16777216.0 * val)

    rMask = 255 << 16
    gMask = 255 << 8
    bMask = 255
    
    r = (val_i & rMask) >> 16
    g = (val_i & gMask) >> 8
    b = val_i & bMask
  
    return (r, g, b)

def packIntToGray(val): 
    gray = int(val * 255.0)
    return (gray, gray, gray)

def packFloatToColor(val):
    enc = np.float32((1.0, 256.0, 65536.0, 16777216.0)) * val
    enc = fract(enc)
    enc -= (enc[1], enc[2], enc[3], enc[3]) * np.float32((1.0/256.0, 1.0/256.0, 1.0/256.0, 0.0))
    enc_i = (int(enc[0] * 255.0), int(enc[1] * 255.0), int(enc[2] * 255.0), int(enc[3] * 255.0))
    return enc_i

# https://www.w3resource.com/python-exercises/math/python-math-exercise-77.php
def rgbToHsv(val):
    r, g, b = val[0]/255.0, val[1]/255.0, val[2]/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return (int(h), int(s), int(v))

def packIntToHsv(val):
    rgb = kinectDepthToRgb(val) #packIntToColor(val)
    return rgbToHsv(rgb)