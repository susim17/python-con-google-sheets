from serial import Serial
from threading import Thread
from Queue import Queue
import signal
import sys
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('PruebaSusana-90da3c7fa1a9.json', scope)
gc = gspread.authorize(credentials)


class serialWatcher (Thread, Serial):
    def __init__(self, q, port = 'COM3', baudrate = 115200):
        Thread.__init__(self)
        Serial.__init__(self, port, baudrate)
        self.daemon = True
        self.queue = q
    def run(self):
        self.running = True
        while self.running:
            if self.in_waiting:
                line = self.readline()[0:-1];
                try:
                    data = json.loads(line)
                    self.queue.put(data)
                    # print "Sensor data in Queue"
                except:
                    # print "Invalid data discarted"
                    pass
    def stop(self):
        self.running = False

data_queue = Queue(10)
sensor = serialWatcher(q = data_queue)
sensor.start()

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def data_process(data):
	print "Dato siendo procesado..."
	print data
	wks = gc.open('Pruena Susana Molina').sheet1

    currentd=data.get('current','Error')
    voltaged=data.get('voltage','Error')
    temperatured=data.get('temperature','Error')

    wks.append_row([data.get('current', 'Error'),data.get('voltage', 'Error'),data.get('temperature', 'Error')])



while True:
    if not data_queue.empty():
        data = data_queue.get()
        data_process(data)
