CAM_OPT_KEYS = {'tl_now', 'tl_delay', 'tl_nop', 'tl_starts', 'tl_ends',
'tl_camres', 'tl_exit', 'md_exit', 'pr_exit', 'pr_camres', 'cam_res', 'cam_shtr_spd', 'cam_iso', 'cam_exp_mode',
'cam_led', 'disk_full', 'exit', 'running'}

TL_NOW_VAL = {0, 1, True, False}
CAM_RES_MAXVAL = {2592: 1944, 1920: 1080}
CAM_SHTR_SPD_MAXVAL = 6000000
CAM_ISO_VAL = (0, 100, 200, 320, 400, 500, 640, 800)
CAM_EXP_MODE_VAL = ('off', 'auto', 'night', 'nightpreview',
'backlight','spotlight', 'sports', 'snow', 'beach', 'verylong',
'fixedfps', 'antishake', 'fireworks')
CAM_LED_VAL = {0, 1, True, False}
EXIT_VAL = (True, False, 1, 0)
#ACTION_VAL = ('preview', 'mo_detect', 'timelapse')

CAM_OPT_DEFAULTS = {
    'tl_now': 0,
    'tl_delay': 1,
    'tl_nop': 1,
    'tl_starts': 0,
    'tl_req': 0,
    'tl_path': "",
    'tl_camres': (640, 480),
    'tl_exit': False,
    'md_exit': False,
    'pr_exit': False,
    'pr_camres': (640, 480),
    'cam_res': (540, 405),
    'cam_shtr_spd': 0,
    'cam_iso': 0,
    'cam_exp_mode': 'auto',
    'cam_led': 0,
    'running': {},
    'disk_full': 0,
    'exit': False
    }

RUNNING_KEYS = ("tl_active", "md_active", "pr_active")#probably obsolete
