#!/usr/bin/env python3
import config
import serial
import telebot

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['get_sms'])
def at_any_message(message):

  port = serial.Serial('/dev/ttyACM0', 460800, timeout=5)

  try:
    port.open()
    print("Port is ready")
  except IOError:
    port.close()
    port.open()
    print("Port was reopened")

  port.write(b'AT+CMGF=1\r\n')      #set text mode
  port.write(b'AT+CSCS="UCS2"\r\n') #set encoding to UCS2
  port.write(b'AT+CMGL="ALL"\r\n')  #get all messages

  def __decode(str):
    ustr = u''
    str = str.strip().replace(b'"', b'')
    for i in range(len(str)):
      if not i % 4:
        ustr += chr(int(str[i:i+4], 16))
    return ustr

  gotmsg = False

  while(1):
    line = port.readline()
    if line.startswith(b'+CMGL'):
      info = line.split(b',')
      msg = '[' + __decode(info[2]) + '] (' + info[4].decode('utf-8') + ' ' + info[5].decode('utf-8') + '): \r\n' +  __decode(port.readline())
      bot.send_message(message.chat.id, msg)
      gotmsg = True
    if gotmsg and line.startswith(b'OK'): break

if __name__ == '__main__':
     bot.polling(none_stop=True)