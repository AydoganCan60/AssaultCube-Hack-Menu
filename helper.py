import ctypes
from ctypes import wintypes

# Dynamic screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def get_offset(name):
    with open("offsets.txt", "r") as f:
        for line in f:
            key_value = line.strip().split("=")
            if len(key_value) == 2:
                key, value = key_value
                if key.strip() == name:  # Strip the key to avoid issues like " health_offset"
                    return int(value.strip(), 16)  # Also strip the value
    return None

class Pointer:
    player_count = 0x18AC0C
    entity_list = 0x18AC04
    local_player = 0x17E0A8
    view_matrix = 0x17DFD0

class Vec2(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]

class Vec2_int(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int)]

class Vec3(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float), ('z', ctypes.c_float)]

class Entity(ctypes.Structure):
    _fields_ = [
        ("_pad1", ctypes.c_byte * 0x4),
        ("pos", Vec3),
        ("_pad2", ctypes.c_byte * 0xDC),
        ("health", ctypes.c_int),
        ("_pad3", ctypes.c_byte * 0x115),
        ("name", ctypes.c_char * 0x50),
        ("_pad4", ctypes.c_byte * 0xB7),
        ("team", ctypes.c_int)
    ]

class WINDOWINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcWindow', wintypes.RECT),
        ('rcClient', wintypes.RECT),
        ('dwStyle', wintypes.DWORD),
        ('dwExStyle', wintypes.DWORD),
        ('dwWindowStatus', wintypes.DWORD),
        ('cxWindowBorders', wintypes.UINT),
        ('cyWindowBorders', wintypes.UINT),
        ('atomWindowType', wintypes.ATOM),
        ('wCreatorVersion', wintypes.WORD),
    ]

# Get window information
def get_window_info(title):
    hwnd = ctypes.windll.user32.FindWindowW(None, title)
    if not hwnd:
        raise Exception("Window not found: " + title)

    win_info = WINDOWINFO()
    win_info.cbSize = ctypes.sizeof(WINDOWINFO)
    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowInfo(hwnd, ctypes.byref(win_info))
    ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))

    global SCREEN_WIDTH, SCREEN_HEIGHT
    SCREEN_WIDTH = rect.right - rect.left
    SCREEN_HEIGHT = rect.bottom - rect.top

    return (win_info.rcClient.left, win_info.rcClient.top, SCREEN_WIDTH, SCREEN_HEIGHT)

# World to Screen
def world_to_screen(matrix, pos):
    clip = Vec3()
    ndc = Vec2()
    result = Vec2_int()

    # World -> Clip
    clip.x = pos.x * matrix[0] + pos.y * matrix[4] + pos.z * matrix[8] + matrix[12]
    clip.y = pos.x * matrix[1] + pos.y * matrix[5] + pos.z * matrix[9] + matrix[13]
    clip.z = pos.x * matrix[3] + pos.y * matrix[7] + pos.z * matrix[11] + matrix[15]

    if clip.z < 0.1:
        raise IOError("Out of bounds")

    # Clip -> NDC
    ndc.x = clip.x / clip.z
    ndc.y = clip.y / clip.z

    # NDC -> Screen
    result.x = int((ndc.x + 1) * (SCREEN_WIDTH / 2))
    result.y = int((1 - ndc.y) * (SCREEN_HEIGHT / 2))

    return result
