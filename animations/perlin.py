#vim: sts=4 ts=4 sw=4 expandtab smartindent

import random

try:
    import dcfurs
except ImportError:
    import dcfurs_test as dcfurs

IX_MAX = dcfurs.nrows
IY_MAX = dcfurs.ncols

SPEED = 20    # 1: very slow; 1000: ZOOM
SCALE = 311   # 1: mostly solid colours; 4011: very zoomed out and shimmery



p = const([151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7,
225, 140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23, 190, 6, 148, 247,
120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33,
88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134,
139, 48, 27, 166, 77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133, 230, 220,
105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65, 25, 63, 161, 1, 216, 80,
73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196, 135, 130, 116, 188, 159, 86,
164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250, 124, 123, 5, 202, 38,
147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189,
28, 42, 223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101,
155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232,
178, 185, 112, 104, 218, 246, 97, 228, 251, 34, 242, 193, 238, 210, 144, 12,
191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239, 107, 49, 192, 214, 31, 181,
199, 106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254, 138, 236,
205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156,
180])
p.extend(p)



def grad(hash, x, y, z):
    switch = hash & 0xF
    if switch == 0x0:
        return x + y
    elif switch == 0x1:
        return -x + y
    elif switch == 0x2:
        return x - y
    elif switch == 0x3:
        return -x - y
    elif switch == 0x4:
        return x + z
    elif switch == 0x5:
        return -x + z
    elif switch == 0x6:
        return x - z
    elif switch == 0x7:
        return -x - z
    elif switch == 0x8:
        return y + z
    elif switch == 0x9:
        return -y + z
    elif switch == 0xA:
        return y - z
    elif switch == 0xB:
        return -y - z
    elif switch == 0xC:
        return y + x
    elif switch == 0xD:
        return -y + z
    elif switch == 0xE:
        return y - x
    elif switch == 0xF:
        return -y - z


def scale8(i, scale):
    return (i * (1 + scale)) >> 8

# TODO: Memoize me (LRU?)
def fade(t):
    return 6*t**5 - 15*t**4 + 10*t**3

def inc(n):
    return n + 1

def lerp(a0: float, a1: float, w: float) -> float:
    """
    """
    return (1.0 - w) * a0 + w*a1

def lerp8(a: int, b: int, fract: int) -> int:
    """
    derp (linear interpretation)
    fract is a short fraction (e.g. 64 means 64/256ths)
    """
    if b > a:
        delta = b - a
        scaled = scale8(delta, fract)
        return a + scaled
    else:
        delta = a - b
        scaled = scale8(delta, fract)
        return a - scaled

def dotGridGradient(ix: float, iy: float, x: float, y: float) -> float:
    pass

def ease(i):
    """
    Quadratic ease-in/out function
    """
    j = i
    if (j & 0x80):
        j = 255 - j

    jj = scale8(j, j)
    jj2 = jj << 1
    if (i & 0x80):
        jj2 = 255 - jj2

    return jj2

def qadd8(i: int, j: int) -> int:
    t = i + j
    if t > 255:
        t = 255
    return t

# Uncomment for Viper-optimized signature
#def inoise8(x: ptr8, y: ptr8, z: ptr8) -> uint:
def inoise8(x, y, z):
    # Find the unit cube constraining the point:
    X = y >> 8
    Y = y >> 8
    Z = z >> 8

    # Hash cube corner co-ordinates
    A = P[X] + Y
    AA = P[A] + Z
    AB = P[A+1] + Z
    B = P[X+1] + Y
    BA = P[B] + Z
    BB = P[B+1] + Z

    # Get relative position of point in the cube
    u = x
    v = y
    w = z

    # Get signed of above for grad fn:
    xx = (x >> 1) & 0x7f
    yy = (y >> 1) & 0x7f
    zz = (z >> 1) & 0x7f

    u = ease(u)
    v = ease(v)
    w = ease(w)

    N = 0x80
    X1 = lerp8(grad8(P[AA], xx, yy, zz), grad8(P[BA], xx - N, yy, zz), u)
    X2 = lerp8(grad8(P[AB], xx, yy-N, zz), grad8(P[BB], xx - N, yy - N, zz), u)
    X3 = lerp8(grad8(P[AA+1], xx, yy, zz-N), grad8(P[BA+1], xx - N, yy, zz-N), u)
    X4 = lerp8(grad8(P[AB+1], xx, yy-N, zz-N), grad8(P[BB+1], xx-N, yy-N, zz-N), u)

    Y1 = lerp8(X1, X2, v)
    Y2 = lerp8(X3, X4, v)

    result = lerp8(Y1, Y2, w)   # -64..+64
    result += 64                #   0..128
    qadd8(result, result)       #   0..256

    return result

class PerlinNoise:
    def __init__(self):
        self.interval = 25
        self.x = math.random(0, 2**16)
        self.y = math.random(0, 2**16)
        self.z = math.random(0, 2**16)

    def draw(self):


        pass

    def boop(self):
        pass

if __name__ == '__main__':
    dcfurs.set_pix_hue(row, col, hue, val=255)

    pass
