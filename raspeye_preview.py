#!/usr/bin/env python3.4

import sys, os, io, socket, struct, json, pygame, threading, copy#just for testing
from datetime import datetime
import constants
#from time import sleep
#from timeit import default_timer as timer# temporary
def start(my_server, my_port, cam_opt):

    def settingup_values():

        return constants.CAM_OPT_DEFAULTS

    def pygame_events(pr_opt, cam_opt):
        pygame.display.init()
        scr_res = cam_opt['cam_res']#.split('x')
        screen = pygame.display.set_mode([scr_res[0], scr_res[1]])
        pygame.display.set_caption('RaspEye')
        #pygame.event.set_blocked(pygame.MOUSEMOTION)
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN])

        while pr_opt['stay']:
            if pr_opt['display_ready']:
                if pr_opt['data'] == None:
                    pr_opt['display_ready'] = False
                    continue
                pr_opt['display_ready'] = False
                img = pygame.image.load(io.BytesIO(pr_opt['data']), '.jpg')
                screen.blit(img, (0, 0))
                pygame.display.flip()
            else:
                for event in pygame.event.get():
                    print(event)
                    if event.type == pygame.QUIT:
                        pr_opt['stay'] = False
                        break
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        stay = False
                        break
                        #if threading.active_count() < 2:
                        #    d_writer = threading.Thread(target=writetofile, args=(copy.copy(data),))
                        #if not d_writer.is_alive():
                        #    d_writer.start()
                else:
                    pygame.event.clear()

        pygame.display.quit()
        return

    client_socket = socket.socket()

    try:
        client_socket.connect((my_server, int(my_port)))
    except:
        print('Connection refused. Check Ip address and port number. Exiting...')
        sys.exit()

    pr_opt = {'display_ready': False, 'stay': True, 'data': None}
    #data = None


    cam_opt = settingup_values()

    pygame_side = threading.Thread(target=pygame_events, args=(pr_opt, cam_opt))
    pygame_side.start()

    if client_socket.sendall(struct.pack('<L', 30)) != None:
        print('[PR] Faild sending initiating CMD')
        client_socket.close()
        pygame.display.quit()
        sys.exit()

    while pr_opt['stay']:
        #tstart = timer()
        if cam_opt['pr_exit'] == 1:
            pr_opt['stay'] = 0
        try:
            filelen = client_socket.recv(4)
            flen = struct.unpack('<L',filelen)
            flen = flen[0]
        except:
            pr_opt['stay'] = False
            pygame_side.join()
            break
        data_temp = b''
        data_toread = flen
        chunk = 4096
        while data_toread != 0:
            if data_toread >= chunk:
                datain = client_socket.recv(chunk)
                data_toread -= len(datain)
            else:
                datain = client_socket.recv(data_toread)
                data_toread -= len(datain)
            data_temp += datain
            if pr_opt['stay'] == False:
                break
        pr_opt['data'] = copy.copy(data_temp)
        pr_opt['display_ready'] = True

    pygame.display.quit()
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    sys.exit()
