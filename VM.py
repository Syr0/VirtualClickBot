#Inside-VM
import socket
import json
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
import threading

keyboard = KeyboardController()
mouse = MouseController()


class RecordController:
    def __init__(self):
        self.actions = []
        self.is_recording = False

    def start_recording(self):
        self.actions = []
        self.is_recording = True

    def stop_recording(self):
        self.is_recording = False
        return self.actions

    def record_keyboard(self, key, event_type):
        if self.is_recording:
            self.actions.append({'device': 'keyboard', 'type': event_type, 'key': str(key)})

    def record_mouse(self, pos_or_button, event_type):
        if self.is_recording:
            self.actions.append({'device': 'mouse', 'type': event_type, 'pos_or_button': pos_or_button})


record_controller = RecordController()


def on_key_press(key):
    record_controller.record_keyboard(key, 'press')


def on_key_release(key):
    record_controller.record_keyboard(key, 'release')


def on_mouse_move(x, y):
    record_controller.record_mouse((x, y), 'move')


def on_mouse_click(x, y, button, pressed):
    record_controller.record_mouse((x, y, button), 'click' if pressed else 'release')


def on_mouse_scroll(x, y, dx, dy):
    record_controller.record_mouse((dx, dy), 'scroll')


def handle_client(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    command = json.loads(request)

    if command['action'] == 'record':
        record_controller.start_recording()
        with MouseListener(on_move=on_mouse_move, on_click=on_mouse_click, on_scroll=on_mouse_scroll) as mouse_listener, \
                KeyboardListener(on_press=on_key_press, on_release=on_key_release) as keyboard_listener:
            mouse_listener.join()
            keyboard_listener.join()
    elif command['action'] == 'stop':
        actions = record_controller.stop_recording()
        client_socket.send(json.dumps(actions).encode('utf-8'))
    elif command['action'] == 'replay':
        actions = command['actions']
        for action in actions:
            if action['device'] == 'keyboard':
                if action['type'] == 'press':
                    keyboard.press(action['key'])
                elif action['type'] == 'release':
                    keyboard.release(action['key'])
            elif action['device'] == 'mouse':
                if action['type'] == 'move':
                    mouse.move(*action['pos'])
                elif action['type'] == 'click':
                    mouse.click(action['button'])
                elif action['type'] == 'scroll':
                    mouse.scroll(*action['scroll'])
    client_socket.close()


def run_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    while True:
        client, _ = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


def main():
    host = '0.0.0.0'
    port = 9999
    run_server(host, port)


if __name__ == '__main__':
    main()
