import customtkinter


class Explorer(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.label = customtkinter.CTkLabel(self)
        self.label.grid(row=0, column=0, padx=10, pady=10)

        # add widgets to app
        self.button = customtkinter.CTkButton(self, command=self.button_click, text='button1')
        self.button.grid(row=0, column=0, padx=50, pady=50)


    def button_click(self):
        print("button click")
        return
    

    def button_click2(self):
        print("button click")
        return
