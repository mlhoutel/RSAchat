import socket
import select 
import sys   
import threading
import time

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

Window.softinput_mode = "below_target"

#Palette
# D7D7D7  grey (0.85, 0.85, 0.85, 1)
# F18C8E   red   (0.94, 0.54, 0.55, 1)
# F0B7A4  orange (0.94, 0.71, 0.64, 1)
# F1D1B5  yellow (0.94, 0.82, 0.71, 1)
# 568EA6  blue (0.32, 0.55, 0.65, 1)
# 305F72   black (0.19, 0.37, 0.45, 1)

# Custom classes implementation
class BackgroundColor(Widget):
	pass
class BackgroundLabel(Label,BackgroundColor):
	pass
class Message(BackgroundLabel):
	pass
	
class SendMessage(Message):
	# Font color
	fnt_r=NumericProperty(0.85)
	fnt_g=NumericProperty(0.85)
	fnt_b=NumericProperty(0.85)
	fnt_a=NumericProperty(1)
	# Background color
	bkg_r=NumericProperty(0.32)
	bkg_g=NumericProperty(0.55)
	bkg_b=NumericProperty(0.65)
	bkg_a=NumericProperty(1)
	
class RecvMessage(Message):
	# Font color
	fnt_r=NumericProperty(0.2)
	fnt_g=NumericProperty(1)
	fnt_b=NumericProperty(1)
	fnt_a=NumericProperty(1)
	# Background color
	bkg_r=NumericProperty(0)
	bkg_g=NumericProperty(0)
	bkg_b=NumericProperty(0)
	bkg_a=NumericProperty(1)
	
class SysMessage(Message):
	# Font color
	fnt_r=NumericProperty(0.5)
	fnt_g=NumericProperty(0.5)
	fnt_b=NumericProperty(0.5)
	fnt_a=NumericProperty(0.5)
	# Background color
	bkg_r=NumericProperty(0)
	bkg_g=NumericProperty(0)
	bkg_b=NumericProperty(0)
	bkg_a=NumericProperty(1)

class SendButton(Button):
	# Font color
	fnt_r=NumericProperty(0.85)
	fnt_g=NumericProperty(0.85)
	fnt_b=NumericProperty(0.85)
	fnt_a=NumericProperty(1)
	# Background color
	bkg_r=NumericProperty(0.94)
	bkg_g=NumericProperty(0.54)
	bkg_b=NumericProperty(0.55)
	bkg_a=NumericProperty(1)

class BackgroundScroller(ScrollView,BackgroundColor):
	# Background color
	bkg_r=NumericProperty(0.94)
	bkg_g=NumericProperty(0.54)
	bkg_b=NumericProperty(0.55)
	bkg_a=NumericProperty(0.3)

class TextBox(TextInput):
	pass
class MenuLabel(Label):
	pass
class ScreenManager(ScreenManager):
	pass
class MenuScreen(Screen):
	pass
class MessagesScreen(Screen):
	pass

class AppChat(BoxLayout):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	IP_address=str("127.0.0.1")
	Port=int(8027)
	stop_threads=False
	threads=[]
	clients=[]
	Admin=False
	Menu=None
	Messages=None
	
	def addSendMessage(self, message):
		msg=SendMessage(text=message)
		self.Messages.ids.messages.add_widget(msg)
		self.Messages.ids.scroller.scroll_to(msg)
		self.Messages.ids.textbox.text=""
	
	def addRecvMessage(self, message):
		self.Messages.ids.messages.add_widget(RecvMessage(text=message))
	
	def addSysMessage(self, message):
		self.Messages.ids.messages.add_widget(SysMessage(text=message))

	def receptThread(self):
		# Reception loop
		while True:
			if self.stop_threads:
				break

			sockets_list = [sys.stdin, self.server] 
			read_sockets, write_socket, error_socket = select.select(sockets_list,[],[])
			# Read all the received sockets
			for socks in read_sockets:
			   	data = socks.recv(2048)
			   	if data:
			   		# Display the received message
			   		message = data.decode('utf-8','ignore')
			   		if message.startswith('<system>'):
			   			self.addSysMessage(message)
			   		else:
			   			self.addRecvMessage(message)
			   	else:
			   		#Server closed
			   		break
		# Notify the server closure
		self.addSysMessage("<system>Server Closed<system>")
		self.disconnectServer()
				   		
	def serverThread(self):
		# Create the server/Test if the port is available
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self.server.bind((self.IP_address, self.Port))
			self.addSysMessage("<system>Binded["+str(self.IP_address)+":"+str(self.Port)+"]<system>")
		except:
			self.Menu.ids.create_label.text="Create a room ("+str(self.IP_address)+":"+str(self.Port)+" already binded)"
			self.disconnectServer()
		
		# Setup the server limits
		temp_limit=self.Menu.ids.create_limit.text.rstrip()
		if temp_limit:
			self.server.listen(int(temp_limit))
		else:
			self.server.listen(int(20))

		# Server loop
		try:
			while True:
				if self.stop_threads:
					break
				# Create and notify the connexion
				conn, addr = self.server.accept()
				self.clients.append(conn)
				self.addSysMessage("<system>"+str(addr[0])+" connected<system>")

				# Add the client Thread
				temp_thread=threading.Thread(target=self.clientThread, args=(conn,addr))
				temp_thread.start()
				self.threads.append(temp_thread)
		except:
			pass
		# Disconnect the server and close the threads
		self.disconnectServer()
				
	def clientThread(self, conn, addr):
		keep_connection=True
		message = "<system>Welcome to this chatroom " + str(addr[0]) + "<system>"
		conn.send(message.encode('utf-8'))

		# Client loop
		while keep_connection:
			if self.stop_threads:
				break
			try:
				data = conn.recv(2048)
				if data:
				   message = data.decode('utf-8','ignore')
				   recv_msg="<"+str(addr[0])+"> "+message.rstrip()
				   self.addRecvMessage(recv_msg)
				   self.broadcast(recv_msg.encode('utf-8'), conn)
				else:
					dec_msg="<system> "+str(addr[0])+" disconnected<system>"
					self.addSysMessage(dec_msg)
					#self.remove(conn)
					conn.shutdown(2)
					conn.close()
					keep_connection=False
			except:
				pass
		self.disconnectServer()
	
	def broadcast(self, message, conn):
		for client in self.clients: 
			if client!=conn: 
				try:
					client.sendall(message.encode('utf-8')) 
				except:
					continue
					#self.remove(client) 
	
	def remove(self,conn):
	    if conn in self.clients:
	        conn.close()
	        self.clients.remove(conn)
        
	def joinRoom(self):
		self.Menu=self.ids.scr_menu
		self.Messages=self.ids.scr_messages
		try:
			temp_ip=self.Menu.ids.join_ip.text.rstrip()
			if temp_ip:
				self.IP_address=str(temp_ip)
				
			temp_port=self.Menu.ids.join_port.text.rstrip()
			if temp_port:
				self.Port=int(temp_port)
				
			# Server connection
			self.server.connect((self.IP_address,self.Port))
			# To fix: when right ip and port but no server freeze
			self.ids.sm.transition.direction = 'left'
			self.ids.sm.current = "messages"
			
			self.addSysMessage("Connected ("+str(self.IP_address)+":"+str(self.Port)+")")

			# Add the reception thread
			temp_thread=threading.Thread(target=receptThread, args=())
			temp_thread.start()
			self.threads.append(temp_thread)
		except:
			self.Menu.ids.join_label.text="Join a room (Can't reach "+str(self.IP_address)+":"+str(self.Port)+")"
	
	def get_ip(self):
	   	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	   	try:
	   	   	s.connect(('10.255.255.255', 1))
	   	   	IP = s.getsockname()[0]
	   	except Exception:
	   		IP = '127.0.0.1'
	   	finally:
	   		s.close()
	   	return IP
    	
	def createRoom(self):
		self.Menu=self.ids.scr_menu
		self.Messages=self.ids.scr_messages

		host_ip = self.get_ip()
		try:
			self.IP_address=str(host_ip)
			temp_port=self.Menu.ids.create_port.text.rstrip()
			if temp_port:
				self.Port=int(temp_port)
			
			# Add the server thread
			temp_thread=threading.Thread(target=self.serverThread, args=())
			temp_thread.start()
			self.threads.append(temp_thread)
			
			self.ids.sm.transition.direction = 'left'
			self.ids.sm.current = "messages"
			self.Admin=True
		except:
			self.Menu.ids.create_label.text="Create a room (Can't create "+str(self.IP_address)+":"+str(self.Port)+")"
	
	def sendMessage(self):
		txt=self.Messages.ids.textbox.text.rstrip()
		#popup = Popup(title='Test popup', content=Label(text='Hello world'),size_hint=(None, None), size=(600, 800))
		#popup.open()
		try:
			if txt:
				self.addSendMessage("<You> "+str(txt))
				if self.Admin:
					self.broadcast(txt, None)
				else:
					self.server.sendall(txt.encode('utf-8'))
		except:
			self.disconnectServer()
			
	def disconnectServer(self):
		self.Messages=self.ids.scr_messages
		
		self.clients=[]
		self.stop_threads=True
		self.Admin=False
		time.sleep(0.01)
		#[t.join() for t in self.threads]
		self.stop_threads=False
		
		self.server.close()
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		if self!=None:
			self.ids.sm.transition.direction = 'right'
			self.ids.sm.current = "menu"
			self.Messages.ids.messages.clear_widgets()

	def quitApplication(self, app):
		self.disconnectServer()
		app.stop()
			
class CryptedChatApp(App):

	def build(self):
		self.load_kv('app.kv')
		return AppChat()

	def on_stop(self):
		AppChat().disconnectServer()
		return True
 
if __name__ == "__main__":
	appChat=CryptedChatApp().run()