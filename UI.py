import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk  # For drop-down menus

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

        self.vm_label = tk.Label(self, text='VM:')
        self.vm_label.pack(side='top', pady=10)
        self.vm_var = tk.StringVar()
        self.vm_dropdown = ttk.Combobox(self, textvariable=self.vm_var)
        self.vm_dropdown['values'] = self.vms
        self.vm_dropdown.pack(side='top', pady=10)

        self.stage = "CREATE_PROFILE"
        self.action_button = tk.Button(self, text=self.stage, command=self.update_stage)
        self.action_button.pack(side="top", pady=10)

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="bottom", pady=10)

        self.profile_dropdown.current(0)
