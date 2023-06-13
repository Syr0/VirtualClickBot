#Outside-VM
import socket
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import subprocess

PROFILES_FILENAME = '../profiles.json'


def get_vms():
    result = subprocess.run(['C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe', 'list', 'vms'],
                            capture_output=True, text=True)
    vms = [line.split(' ')[0].strip('"') for line in result.stdout.splitlines()]
    return vms


def get_vm_ip(vm_name):
    command = ['C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe', 'guestproperty', 'enumerate', vm_name]
    result = subprocess.run(command, capture_output=True, text=True)
    ip_dict = {}
    for line in result.stdout.splitlines():
        if "Net" in line and "/V4/IP" in line:
            parts = line.split(",")
            interface = parts[0].split("/")[1]
            ip = parts[1].split(":")[1].strip()
            ip_dict[interface] = ip
    return ip_dict


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('VM Controller')
        self.master.configure(bg='#D3D3D3')
        self.pack()

        self.profiles = self.load_profiles()
        self.vms = get_vms()

        self.create_widgets()

    def create_widgets(self):
        self.master.option_add("*Font", "arial 20")
        self.master.option_add('*Background', '#D3D3D3')
        self.master.option_add('*Foreground', 'black')
        self.master.option_add('*Combobox*Listbox*Background', '#D3D3D3')
        self.master.option_add('*Combobox*Listbox*Foreground', 'black')

        self.profile_label = tk.Label(self, text='Profile:')
        self.profile_label.pack(side='top', pady=10)
        self.profile_var = tk.StringVar()
        self.profile_dropdown = ttk.Combobox(self, textvariable=self.profile_var)
        self.profile_dropdown['values'] = ['create a new one'] + list(self.profiles.keys())
        self.profile_dropdown.pack(side='top', pady=10)

        self.stage = "CREATE_PROFILE"
        self.action_button = tk.Button(self, text=self.stage, command=self.update_stage)
        self.action_button.pack(side="top", pady=10)

        self.vm_label = tk.Label(self, text='VM:')
        self.vm_label.pack(side='top', pady=10)
        self.vm_var = tk.StringVar()
        self.vm_dropdown = ttk.Combobox(self, textvariable=self.vm_var)
        self.vm_dropdown['values'] = self.vms
        self.vm_dropdown.pack(side='top', pady=10)

        self.record_button = tk.Button(self, text="CREATE PROFILE", command=self.create_profile)
        self.record_button.pack(side="top", pady=10)

        self.show_profile_button = tk.Button(self, text="SHOW PROFILE", command=self.show_profile)
        self.show_profile_button.pack(side="top", pady=10)

        self.run_button = tk.Button(self, text="START", command=self.select_and_run_profile)
        self.run_button.pack(side="top", pady=10)

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="bottom", pady=10)

        self.profile_dropdown.current(0)

    def select_vm(self):
        vm_name = self.vm_var.get()
        if vm_name in self.vms:
            self.vm_var.set(vm_name)
        else:
            messagebox.showerror("Error", "VM not found")

    def start_recording(self):
        profile_name = self.profile_var.get()
        vm_name = self.vm_var.get()

        if profile_name in self.profiles and vm_name in self.vms:
            self.send_command_to_vm(vm_name, {'action': 'record', 'profile_name': profile_name})
            self.profiles[profile_name] = self.receive_profile_from_vm(vm_name)
            self.save_profiles()
        else:
            messagebox.showerror("Error", "Invalid VM or profile")
    def update_stage(self):
        if self.stage == "CREATE_PROFILE":
            self.create_profile()
            self.stage = "SELECT_VM"
        elif self.stage == "SELECT_VM":
            self.select_vm()
            self.stage = "START_RECORDING"
        elif self.stage == "START_RECORDING":
            self.start_recording()
            self.stage = "SHOW_RECORDING"
        elif self.stage == "SHOW_RECORDING":
            self.show_profile()
            self.stage = "CREATE_PROFILE"
        self.action_button.config(text=self.stage)

    def show_profile(self):
        profile_name = self.profile_var.get()
        if profile_name in self.profiles:
            profile_content = json.dumps(self.profiles[profile_name], indent=4)
            messagebox.showinfo("Profile Content", profile_content)
        else:
            messagebox.showerror("Error", "Profile not found")
    def load_profiles(self):
        if os.path.exists(PROFILES_FILENAME):
            with open(PROFILES_FILENAME, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_profiles(self):
        with open(PROFILES_FILENAME, 'w') as file:
            json.dump(self.profiles, file)

    def create_profile(self):
        name = simpledialog.askstring("Input", "Profile name?")
        if name:
            self.profiles[name] = []
            self.save_profiles()
            self.profile_dropdown['values'] = ['create a new one'] + list(self.profiles.keys())
            self.profile_var.set(name)

    def record_profile(self):
        profile_name = self.profile_var.get()
        vm_name = self.vm_var.get()

        if vm_name not in self.vms:
            messagebox.showerror("Error", "No such VM exists")
            return

        self.send_command_to_vm(vm_name, {'action': 'record', 'profile_name': profile_name})
        self.profiles[profile_name] = self.receive_profile_from_vm(vm_name)
        self.save_profiles()

    def send_command_to_vm(self, vm_name, command):
        ip = get_vm_ip(vm_name)
        if not ip:
            raise Exception(f"No IP found for VM: {vm_name}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, 10000)
        sock.connect(server_address)
        try:
            message = json.dumps(command)
            sock.sendall(message.encode('utf-8'))
        finally:
            sock.close()

    def receive_profile_from_vm(self, vm_name):
        ip = get_vm_ip(vm_name)
        if not ip:
            raise Exception(f"No IP found for VM: {vm_name}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, 10000)
        sock.connect(server_address)
        try:
            data = sock.recv(1024)
            profile = json.loads(data.decode('utf-8'))
            return profile
        finally:
            sock.close()

    def select_and_run_profile(self):
        profile_name = self.profile_var.get()
        if profile_name in self.profiles:
            host = get_vm_ip(self.vm_var.get())
            self.send_profile(host, 9999, self.profiles[profile_name])
        else:
            messagebox.showerror("Error", "Profile not found")


root = tk.Tk()
app = Application(master=root)
app.mainloop()
