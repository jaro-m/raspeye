from guizero import *
import sys, socket, struct, json, time, threading
import constants, raspeye_preview


def send_cmd(actionNo):
    '''opens a connection (socket) and sends a COMMAND (number) to the server.
        input: int (command/number)
    '''
    my_server = address_tbox.get()
    my_port = port_tbox.get()
    conn = socket.socket()
    conn.connect((my_server, int(my_port)))
    conn.settimeout(3)#None
    try:
        if conn.sendall(struct.pack('<L', actionNo)) != None:
            #print('Faild sending initiating CMD')
            return
    except socket.timeout as err:
        print('Socket error:', err)
        pass
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
    conn.connect((my_server, int(my_port)))
    conn.settimeout(3)#None

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
        #connection = False
        return
    #else:
    #    print('Sent', flsize)
    #print('Size sent')
    #time.sleep(1)
    bytes_sent = conn.sendall(optstr)
    if bytes_sent != None:
        print('Sending CAM_OPT failure, bytes sent:', bytes_sent)
        #connection = False
        return
    #print('All OK!')
    conn.close()

def receive_opts():
    '''connects to the server and receives options/settings from it.
        Changes state of combo buttons according to received data.
        No input
        output: dictionary
    '''
    #global cam_opt
    my_server = address_tbox.get()
    my_port = port_tbox.get()
    conn = socket.socket()
    conn.connect((my_server, int(my_port)))
    conn.settimeout(3)#None
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
    cam_opt_s = str(data_temp)[2:-1]
    cam_opt_tmp = json.loads(cam_opt_s)
    conn.close()
    if 'tl_active' in cam_opt_tmp['running']:
        tl_combo.set("Time lapse is ON")
    else:
        tl_combo.set("Time lapse is OFF")
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
    info('The address', 'The addres field can contain only the address of your server (you have to find out what address it is).')
def help_port2():
    info('Port', 'The port field should contain the number, the port used by the server (you set it up starting the server)')
def help_tl1():
    info("Number of pictures", "The time lapse is just a process of taking pictures (for example up to 120 pictures)\
     every given period of time (for example 300 seconds)")
def help_tl2():
    info("The frequency of taking pictures", "The most interesting is watching the pictures converted to a video \
    when frames of video made up of the pictures change a lot quicker then the pictures were taken")

def checkout():
    #global cam_opt
    try:
        cam_opt = receive_opts()
    except AttributrError as err:
        tb1.set(err)
        return
    co_msg = ''
    for itm in cam_opt.items():
        co_msg += str(itm)
        co_msg += '\n'
    tb1.set(co_msg)
    return

def tl_func(nm):
    #global cam_opt
    camopts = {}
    if nm == 'Time lapse is ON':
        camopts['tl_nop'] = int(tl_nop_tb.get())
        camopts['tl_delay'] = int(tl_delay_tb.get())
        send_opts(camopts)
        send_cmd(20)

        time.sleep(1)
        receive_opts()
        return
    else:
        camopts['tl_exit'] = 1
        send_opts(camopts)
        return

def md_func(nm): # not tested yet
    send_cmd(10)

    time.sleep(1)
    receive_opts()
    return

def pr_func(nm):
    cam_opt = receive_opts()
    if nm == "Preview is ON":
        if 'pr_active' not in cam_opt['running']:
            my_server = address_tbox.get()
            my_port = port_tbox.get()
            prv_thr = threading.Thread(target=raspeye_preview.start, args=(my_server, my_port, cam_opt))
            prv_thr.start()
        else:
            tb1.set('Preview is running!')
            return
    else:
        if 'pr_active' in cam_opt['running']:
            send_opts({'pr_exit': 1})

    time.sleep(1)
    receive_opts()
    return


# Window setup
address_box_text = "for example: 192.168.0.1" # ;)
port_box_text = "for example: 19876"

app = App(layout='auto', width='480', height='640', title="Raspeye client")

mytitle = Text(app, text="RaspEye", size=24, color="red", font="Helvetica", grid=[0, 0], align="top")

conn_box = Box(app, layout="grid")
myaddress = Text(conn_box, text="Type in the address of your Raspeye server", size=8, color="blue", font="Helvetica", grid=[0, 0], align="bottom")
address_tbox = TextBox(conn_box, text=address_box_text, width=40, grid=[1, 0], align="left")
myport = Text(conn_box, text="Type in the port used by your Raspeye server", size=8, color="blue", font="Helvetica", grid=[3, 0], align="bottom")
port_tbox = TextBox(conn_box, text=port_box_text, width=40, grid=[4, 0], align="left")
helppb1 = PushButton(conn_box, text="   ?   ", command=help_port1, padx=1, pady=1, grid=[1, 1])
helppb2 = PushButton(conn_box, text="   ?   ", command=help_port2, padx=1, pady=1, grid=[4, 1])
conn_button = PushButton(app, text="Check out", command=checkout, padx=1, pady=1)

spacer1 = Text(app, text=" ", size=14)

tl_box = Box(app, layout="grid")
tl_nop_txt = Text(tl_box, text="Type in the number of pictures you want to take", size=8, color="blue", font="Helvetica", grid=[0, 0], align="bottom")
tl_nop_tb = TextBox(tl_box, text="for example: 120", width=40, grid=[1, 0], align="left")
tl_delay_txt = Text(tl_box, text="Type in the time (in seconds) between pictures", size=8, color="blue", font="Helvetica", grid=[3, 0], align="bottom")
tl_delay_tb = TextBox(tl_box, text="for example: 300", width=40, grid=[4, 0], align="left")
helppb3 = PushButton(tl_box, text="   ?   ", command=help_tl1, padx=1, pady=1, grid=[1, 1])
helppb4 = PushButton(tl_box, text="   ?   ", command=help_tl2, padx=1, pady=1, grid=[4, 1])

tl_combo = Combo(app, options=["Time lapse is OFF", "Time lapse is ON"], command=tl_func)

spacer1 = Text(app, text=" ", size=14)

action_box = Box(app, layout="grid")

pr_combo = Combo(action_box, options=["Preview is OFF", "Preview is ON"], command=pr_func, grid=[0, 1])
md_combo = Combo(action_box, options=["Motion detection is OFF", "Motion detection is ON"], command=md_func, grid=[0, 2])

tb_box = Box(app, layout="grid")
#tb0 = TextBox(tb_box) # just testing
tb1 = Text(app, text="", size="8", color="blue", font="Helvetica", align="left")
#tb2 = TextBox(tb_box)

# seting up some initial values
cam_opt = constants.CAM_OPT_DEFAULTS

# render app window
app.display()
print('Be well!')
