from guizero import *
import sys, socket, struct, json, time, threading, datetime
import constants, raspeye_preview


def send_cmd(actionNo):
    '''opens a connection (socket) and sends a COMMAND (number) to the server.
        input: int (command/number)
    '''
    my_server = address_tbox.get()
    my_port = port_tbox.get()
    conn = socket.socket()
    conn.settimeout(3)#None
    try:
        conn.connect((my_server, int(my_port)))
        if conn.sendall(struct.pack('<L', actionNo)) != None:
            #print('Failed sending initiating CMD')
            return
    except socket.timeout as err:
        print('Socket error:', err)
    conn.close()
    return

def send_opts(camopts):
    '''connects to the server and sends OPTIONS in a json file.
        input: dictionary
    '''
    global cam_opt
    my_server = address_tbox.get()
    my_port = port_tbox.get()
    conn = socket.socket()
    conn.settimeout(3)#None
    try:
        conn.connect((my_server, int(my_port)))
    except OSError as err:
        print("Connection error: {}".format(err))
        con_waffle.set_pixel(0, 0, 'red')
        conn.close()
        return

    cam_opt_s = json.dumps(camopts)
    optstr = cam_opt_s.encode(encoding='UTF-8')
    #try:
    if conn.sendall(struct.pack('<L', 40)) != None:
        print('Faild sending initiating CMD')
        return
    #except socket.timeout as err:
    #    print('Socket error:', err)
    #return

    flsize = len(optstr)
    flen = struct.pack('<L', flsize)
    if conn.sendall(flen) != None:
        print('Some initial sending failure')
        return
    bytes_sent = conn.sendall(optstr)
    if bytes_sent != None:
        print('Sending CAM_OPT failure, bytes sent:', bytes_sent)
        return
    conn.close()

def receive_opts():
    '''connects to the server and receives options/settings from it.
        Changes state of combo buttons according to received data.
        No input
        output: dictionary
    '''
    my_server = address_tbox.get()
    my_port = port_tbox.get()
    conn = socket.socket()
    conn.settimeout(3)#None
    try:
        conn.connect((my_server, int(my_port)))
    except (ConnectionRefusedError, OSError) as err:
        con_waffle.set_pixel(0, 0, 'red')
        tl_waffle.set_pixel(0, 0, 'red')
        md_combo.set('Motion detection is OFF')
        pr_combo.set('Preview is OFF')
        print("No connection, error: {}".format(err))
        return
    try:
        if conn.sendall(struct.pack('<L', 50)) != None:
            #print('Faild sending initiating CMD')
            return
    except socket.timeout as err:
        print('Socket error:', err)
        return
    try:
        length = conn.recv(4)
    except socket.timeout as err:
        #print('Socket error:', err)
        return
    length = struct.unpack('<L', length)[0]
    data_temp = b''
    data_toread = length
    chunk = 4096
    while data_toread != 0:
        try:
            if data_toread >= chunk:
                datain = conn.recv(chunk)
                data_toread -= len(datain)
            else:
                datain = conn.recv(data_toread)
                data_toread -= len(datain)
            data_temp += datain
        except socket.timeout as err:
            #print("CAM_OPT hasn't been received. Socket error:", err)
            return
    cam_opt_s = data_temp.decode()
    cam_opt_tmp = json.loads(cam_opt_s)
    conn.close()

    if 'tl_active' in cam_opt_tmp['running']:
        tl_waffle.set_pixel(0, 0, 'green')
    else:
        tl_waffle.set_pixel(0, 0, 'red')
    if 'md_active' in cam_opt_tmp['running']:
        md_combo.set('Motion detection is ON')
    else:
        md_combo.set('Motion detection is OFF')
    if 'pr_active' in cam_opt_tmp['running']:
        pr_combo.set('Preview is ON')
    else:
        pr_combo.set('Preview is OFF')
    return cam_opt_tmp


'''
    GUI part...
'''

def help_port1():
    info('The address',
        'The addres field can contain only the IP address of your server (you have to find out what address it is).')
def help_port2():
    info('Port',
        'The port field should contain the number, the port used by the server (you set it up starting the server)')
def help_tl1():
    info("Number of pictures",
        "Type in the number of pictures you want to take (for example 120 pictures).")
def help_tl2():
    info("The frequency of taking pictures",
        "The time between 2 consecutive pictures in seconds (for example 300).")

def help_tl3():
    info("Setting up the date and time for the time lapse to start",
        "At the moment the format of date and time has to be provided in the following format:\n\
        DD/MM/YYY HH:MM\n and the time hass to point to future")

def checkout():
    #global cam_opt
    try:
        cam_opt = receive_opts()
    except AttributeError as err:
        con_waffle.set_pixel(0, 0, 'red')
        return
    co_msg = ''
    if type(cam_opt) != type({}):
        print("<checkout> function: An error occurred")
        con_waffle.set_pixel(0, 0, 'red')
        return
    con_waffle.set_pixel(0, 0, 'green')
    return

def validate_time(timestr):
    """Simple checking whether time string can be converted
        to datetime object.
        input:
            timestr = string representing date and time in format:
                    DD/MM/YYYY HH:MM
        output:
            True if the string can be succesfully converted
            False otherwise 
    """
    if len(timestr) < 9:
        return 0
    #try:
    date0, time0 = timestr.split(' ')
    if '/' in date0:
        day0, month0, year0 = date0.split('/')
    elif '-' in date0:
        day0, month0, year0 = date0.split('-')
    else:
        print("date is not correct", date0, time0)
        return 0
    hour0, minute0 = time0.split(':')
    year0 = int(year0)
    month0 = int(month0)
    day0 = int(day0)
    hour0 = int(hour0)
    minute0 = int(minute0)
    thetime0 = (year0, month0, day0, hour0, minute0)
    thetime = datetime.datetime(thetime0[0], thetime0[1], thetime0[2], thetime0[3], thetime0[4])
    # except:
    #     print("date/time conversion failure")
    #     return 0
    # else:
    if thetime > datetime.datetime.today():
        return 1
    else:
        print("The set time has just passed. It has to point to the future.")
        return 0

def tl_start_set():
    """
    """
    camopts = {}
    try:
        nop = int(tl_nop_tb.get())
        delay = int(tl_delay_tb.get())
    except ValueError as err:
        nop = constants.CAM_OPT_DEFAULTS['tl_nop']
        delay = constants.CAM_OPT_DEFAULTS['tl_delay']
    if nop < 1:
        nop = constants.CAM_OPT_DEFAULTS['tl_nop']
    if delay < 1:
        delay = constants.CAM_OPT_DEFAULTS['tl_delay']
    camopts['tl_nop'] = nop
    camopts['tl_delay'] = delay
    if validate_time(tl_time_tb.get()):
        print("time's correct")
        camopts['tl_starts'] = tl_time_tb.get()
        camopts['tl_now'] = 0
    else:
        print("time's NOT! correct, time lapse will start immediately")
        camopts['tl_now'] = 1
        camopts['tl_starts'] = 0
    tl_waffle.set_pixel(0, 0, 'green')
    send_opts(camopts)
    send_cmd(20)

    time.sleep(1)
    receive_opts()
    return

def tl_stop():
    camopts = {}
    camopts['tl_exit'] = 1
    send_opts(camopts)
    tl_waffle.set_pixel(0, 0, 'red')
    return

def md_func(nm):
    send_cmd(10)

    time.sleep(1)
    receive_opts()
    return

def pr_func(nm):
    cam_opt = receive_opts()
    if not isinstance(cam_opt, dict):
        return
    if nm == "Preview is ON":
        if 'pr_active' not in cam_opt['running']:
            my_server = address_tbox.get()
            my_port = port_tbox.get()
            prv_thr = threading.Thread(target=raspeye_preview.start, args=(my_server, my_port, cam_opt))
            prv_thr.start()
        else:
            #tb1.set('Preview is running!')
            return
    else:
        if 'pr_active' in cam_opt['running']:
            send_opts({'pr_exit': 1})

    time.sleep(1)
    receive_opts()
    return

def srv_exit():
    try:
        cam_opt = receive_opts()
    except AttributeError as err:
        con_waffle.set_pixel(0, 0, 'red')
        return
    send_cmd(0)


# Window setup

address_box_text = "192.168.1.15" # ;)
port_box_text = "19876"
time_now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

app = App(layout='auto', width='480', height='384', title="Raspeye client")

menubar = MenuBar(app,
                  toplevel=["Advanced Options"],
                  options=[[["Stop server", srv_exit]]])

mytitle = Text(app, text="RaspEye", size=24, color="red", font="Helvetica", grid=[0, 0], align="top")

conn_box = Box(app, layout="grid")
myaddress = Text(conn_box,
                text="The IP address of your Raspeye server",
                size=8,
                color="blue",
                font="Helvetica",
                grid=[0, 0],
                align="bottom")

address_tbox = TextBox(conn_box,
                text=address_box_text,
                width=40,
                grid=[1, 0],
                align="left")

myport = Text(conn_box,
                text="The port used by your Raspeye server",
                size=8,
                color="blue",
                font="Helvetica",
                grid=[3, 0],
                align="bottom")

port_tbox = TextBox(conn_box,
                text=port_box_text,
                width=40,
                grid=[4, 0],
                align="left")

helppb1 = PushButton(conn_box,
                text="   ?   ",
                command=help_port1,
                padx=1,
                pady=1,
                grid=[1, 1])

helppb2 = PushButton(conn_box,
                text="   ?   ",
                command=help_port2,
                padx=1,
                pady=1,
                grid=[4, 1])

con_btn = Box(app, layout="grid")

con_waffle = Waffle(con_btn, height=1, width = 1, dim=15, pad=1, color="red", dotty=True, grid=[0, 0])

conn_button = PushButton(con_btn,
                text="Check/Connect",
                command=checkout,
                padx=1,
                pady=1,
                grid=[0, 1])

spacer1 = Text(app,
                text=" ",
                size=14)

tl_box = Box(app, layout="grid")

tl_nop_txt = Text(tl_box,
                text="The number of pictures",
                size=8, color="blue",
                font="Helvetica",
                grid=[0, 0],
                align="bottom")

tl_nop_tb = TextBox(tl_box,
                text="120",
                width=40,
                grid=[1, 0],
                align="left")

tl_delay_txt = Text(tl_box,
                text="The time to wait before taking the next picture",
                size=8,
                color="blue",
                font="Helvetica",
                grid=[3, 0],
                align="bottom")

tl_delay_tb = TextBox(tl_box,
                text="300",
                width=40,
                grid=[4, 0],
                align="left")

tl_time_txt = Text(tl_box,
                text="The date and time in the form: DD/MM/YYYY HH:MM",
                size=8,
                color="blue",
                font="Helvetica",
                grid=[5, 0],
                align="bottom")

tl_time_tb = TextBox(tl_box,
                text=time_now,
                width=40,
                grid=[6, 0],
                align="left")

helppb3 = PushButton(tl_box,
                text="   ?   ",
                command=help_tl1,
                padx=1,
                pady=1,
                grid=[1, 1])

helppb4 = PushButton(tl_box,
                text="   ?   ",
                command=help_tl2,
                padx=1,
                pady=1,
                grid=[4, 1])

helppb5 = PushButton(tl_box,
                text="   ?   ",
                command=help_tl3,
                padx=1,
                pady=1,
                grid=[6, 1])

tl_btn = Box(app, layout="grid")

tl_waffle = Waffle(tl_btn, height=1, width = 1, dim=15, pad=1, color="red", dotty=True, grid=[0, 0])

tlstart_button = PushButton(tl_btn,
                text="Start/Set TL",
                command=tl_start_set,
                padx=1,
                pady=1,
                grid=[0, 1])

tlstop_button = PushButton(tl_btn,
                text="Stop TL",
                command=tl_stop,
                padx=15,
                pady=1,
                grid=[0, 2])

spacer1 = Text(app, text=" ", size=8)

action_box = Box(app, layout="grid")

pr_combo = Combo(action_box,
                options=["Preview is OFF", "Preview is ON"],
                command=pr_func,
                grid=[0, 1])

md_combo = Combo(action_box,
                options=["Motion detection is OFF", "Motion detection is ON"],
                command=md_func,
                grid=[0, 2])

# tb_box = Box(app, layout="grid")
# tb0 = TextBox(tb_box) # just testing
# tb1 = Text(app,
#             text="",
#             size="8",
#             color="blue",
#             font="Helvetica",
#             align="left")
#
# tb2 = TextBox(tb_box)

# setting up some initial values
cam_opt = constants.CAM_OPT_DEFAULTS

# render app window
app.display()
print('Be well!')

