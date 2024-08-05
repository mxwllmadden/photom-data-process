# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 15:55:40 2024

@author: mbmad
"""

import MSPhotom as msp
import threading
import copy
import time

def main():
    reporter = {'App' : None,
                'Data' : None}
    app_thread = threading.Thread(target=MSPhotom_Automated,
                                  args=(reporter,),
                                  daemon=True)
    app_thread.start()
    
    print('Waiting for App to load')
    app = waitfor(reporter,'App')
    print('Please load the pckl data file you would like to update')
    data = waitfor(reporter,'Data')
    return data
    
class MSPhotom_Automated(msp.MSPApp):
    def __init__(self, reporter : list):
        self.reporter = reporter
        reporter['App'] = self
        super().__init__()

    def load_data(self):
        super().load_data()
        self.view.update_state('None')
        print('loaded!')
        self.reporter['Data'] = self.data

def waitfor(value, index):
    while True:
        print('check')
        time.sleep(1)
        if value[index] is not None:
            break
    return value[index]

if __name__ == '__main__':
    data = main()