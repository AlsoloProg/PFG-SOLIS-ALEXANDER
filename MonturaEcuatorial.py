import tkinter as tk
import StellariumRC
from astropy.time import Time
import serial
import time
global board 
board = serial.Serial(port='COM6', baudrate=9600, timeout=.1)

class TelescopeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.bind("<KeyPress>", self.tecla_presionada)
        self.root.bind("<KeyRelease>", self.tecla_suelta)
        self.root.title("Introducir datos para ajuste del telescopio")
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_coordinate = (self.screen_width/2) - (500/2)
        self.y_coordinate = (self.screen_height/2) - (300/2)
        self.root.geometry("800x300")
        self.language_var = tk.StringVar()
        self.language_var.set("Español")
        self.font_style = ("Courier", 14)
        self.language_label = tk.Label(self.root, text="Cambiar lenguage:", font=self.font_style)
        self.language_label.place(relx=0.4, rely=0.1, anchor="e")
        self.language_menu = tk.OptionMenu(self.root, self.language_var, "Español", "English", command=self.cambiar_idioma)
        self.language_menu.config(font=("Courier", 14), width=12)
        self.language_menu.place(relx=0.6, rely=0.05, anchor="n")
        
        #self.root.protocol("WM_DELETE_WINDOW", self.close_serial)
        
        self.cuerpo_celeste_label = tk.Label(self.root, text="Cuerpo Celeste:", font=self.font_style)
        self.cuerpo_celeste_label.place(relx=0.4, rely=0.25, anchor="e")
        self.cuerpo_celeste_entry = tk.Entry(self.root, font=self.font_style)
        self.cuerpo_celeste_entry.place(relx=0.6, rely=0.25, anchor="w")

        self.latitud_label = tk.Label(self.root, text="Latitud:", font=self.font_style)
        self.latitud_label.place(relx=0.4, rely=0.40, anchor="e")
        self.latitud_entry = tk.Entry(self.root, font=self.font_style)
        self.latitud_entry.place(relx=0.6, rely=0.40, anchor="w")

        self.longitud_label = tk.Label(self.root, text="Longitud:", font=self.font_style)
        self.longitud_label.place(relx=0.4, rely=0.55, anchor="e")
        self.longitud_entry = tk.Entry(self.root, font=self.font_style)
        self.longitud_entry.place(relx=0.6, rely=0.55, anchor="w")

        self.default_data_button = tk.Button(self.root, text="Colocar datos por defecto", command=self.default_data, font=self.font_style)
        self.default_data_button.place(relx=0.25, rely=0.70, anchor="center")

        self.move_telescope_button = tk.Button(self.root, text="Mover telescopio", command=self.move_telescope, font=self.font_style)
        self.move_telescope_button.place(relx=0.56, rely=0.70, anchor="center")
                                  
        self.resultado_label = tk.Label(self.root, text="", font=self.font_style)
        self.resultado_label.place(relx=0.5, rely=0.9, anchor="center")
    
    def tecla_presionada(self, event):
        if event.keysym == "Up":
            pack_to_send = bytes("0b0b1" + "\n", 'utf-8')
            board.write(pack_to_send)
        if event.keysym == "Left":
            pack_to_send = bytes("0b0b2" + "\n", 'utf-8')
            board.write(pack_to_send)
        if event.keysym == "Down":
            pack_to_send = bytes("0b0b3" + "\n", 'utf-8')
            board.write(pack_to_send)
        if event.keysym == "Right":
            pack_to_send = bytes("0b0b4" + "\n", 'utf-8')
            board.write(pack_to_send)
        if event.keysym == "space":
            pack_to_send = bytes("0b0b6" + "\n", 'utf-8')
            board.write(pack_to_send)

    def tecla_suelta(self, event):
        if event.keysym == "Left" or event.keysym == "Right" or event.keysym == "Up" or event.keysym == "Down":
            pack_to_send = bytes("0b0b5" + "\n", 'utf-8')
            board.write(pack_to_send)       
            time.sleep(0.001)
            pack_to_send = bytes("0b0b0" + "\n", 'utf-8')
            board.write(pack_to_send)    
        

    def move_telescope(self):
        s = StellariumRC.Stellarium()
        s.location.setLocation(latitude=self.latitud_entry.get(), longitude=self.longitud_entry.get())
        s.main.setFocus(target=self.cuerpo_celeste_entry.get(),mode='zoom')
        ut1_time = Time.now()
        hours = ut1_time.sidereal_time('mean', longitude = 0).hour
        lon = -84.11074/15
        lst = hours+lon
        if lst < 0:
            lst = lst + 24
        self.lst = lst * 15
        visible_sky_min = lst-6
        visible_sky_max = lst + 6
        if visible_sky_max > 24:
            visible_sky_max -= 24
        if visible_sky_min < 0:
            visible_sky_min += 24
        dec = s.objects.getInfo(self.cuerpo_celeste_entry.get())['dec']
        ra = s.objects.getInfo(self.cuerpo_celeste_entry.get())['ra']
        if ra < 0:
            ra = 360+ra
        self.resultado_label.config(text=f"Dec: {dec}\nRA: {ra}")
        if lst > 12:
            if visible_sky_max*15 > ra and self.lst < ra and visible_sky_min*15 < ra:
                self.ra_movement = -visible_sky_max * 15 + ra
                self.dec_movement = -(90-dec)
            elif ra > visible_sky_min*15 and ra < self.lst:
                self.ra_movement = -ra + visible_sky_min*15
                self.dec_movement = 90-dec
            elif ra < visible_sky_max*15 and ra < visible_sky_min*15 and ra < self.lst:
                self.ra_movement = -visible_sky_max*15 + ra
                self.dec_movement = -(90-dec)
            elif ra < visible_sky_max*15 and ra < visible_sky_min*15:
                self.ra_movement = (ra + 24*15) - self.lst
                self.dec_movement = 180-(90+dec)
            else:
                self.ra_movement = self.lst - ra
                self.dec_movement = -(90-dec)
        if lst < 12:
            if ra < visible_sky_max*15 and ra > self.lst:
                self.ra_movement = -visible_sky_max * 15 + ra
                self.dec_movement = -(90-dec)
            elif ra < visible_sky_max*15 and ra < self.lst and ra > visible_sky_min*15:
                self.ra_movement = -(ra - visible_sky_min*15)
                self.dec_movement = (90-dec)
            elif ra > self.lst and ra > visible_sky_max*15 and ra > visible_sky_min *15:
                self.ra_movement = -ra + visible_sky_min*15
                self.dec_movement = (90-dec)
            elif ra < self.lst and ra < visible_sky_min *15 and ra <visible_sky_max * 15:
                self.ra_movement = -(ra + 24*15) + visible_sky_min*15
                self.dec_movement = (90-dec)
            elif ra < self.lst and  visible_sky_min * 15 < ra and ra < visible_sky_max * 15:
                self.ra_movement = -(ra - visible_sky_min*15)
                self.dec_movement = (90-dec)
            else:
                self.ra_movement = ra - self.lst
                self.dec_movement = 180-(90+dec)
        print(ra, " ",self.lst, " ", visible_sky_max*15)
        if self.ra_movement > 90 or self.ra_movement < -90:
            print("The movement is out of boundaries")
        else:
            print("You must move: ", self.ra_movement, "in RA and this in DEC: ", self.dec_movement)
            time.sleep(1)
            if self.dec_movement > 0:
                self.ra_movement = -self.ra_movement
            pack_to_send = bytes(str("{:.2f}".format(round(self.dec_movement*2)/2)) + "b" + str("{:.2f}".format(round(self.ra_movement*2)/2)) +"b0" + "\n", 'utf-8')
            print(pack_to_send)
            board.write(pack_to_send)
            while True:
                board_in = board.readline().decode().strip()
                print(board_in)
                if board_in == "Finished":
                    break
        return dec, ra

    def default_data(self):
        self.cuerpo_celeste_entry.delete(0,len(self.cuerpo_celeste_entry.get()))
        self.cuerpo_celeste_entry.insert(0,"sun")
        self.latitud_entry.delete(0,len(self.latitud_entry.get()))
        self.latitud_entry.insert(0, 9.94298)
        self.longitud_entry.delete(0,len(self.longitud_entry.get()))
        self.longitud_entry.insert(0, -84.11074)

    def cambiar_idioma(self, *args):
        idioma = self.language_var.get()
        if idioma == "Español":
            self.actualizar_texto("es")
        else:
            self.actualizar_texto("en")

    def actualizar_texto(self, idioma):
        if idioma == "es":
            self.cuerpo_celeste_label.config(text="Cuerpo Celeste:")
            self.latitud_label.config(text="Latitud:")
            self.longitud_label.config(text="Longitud:")
            self.default_data_button.config(text="Colocar datos por defecto")
            self.resultado_label.config(text="")
            self.root.title("Introducir datos para ajuste del telescopio")
            self.language_label.config(text="Cambiar lenguage")
            self.move_telescope_button.config(text="Mover telescopio")
        else:
            self.cuerpo_celeste_label.config(text="Celestial Body:")
            self.latitud_label.config(text="Latitude:")
            self.longitud_label.config(text="Longitude:")
            self.default_data_button.config(text="Place default data")
            self.resultado_label.config(text="")
            self.root.title("Enter data for telescope adjustment")
            self.language_label.config(text="Change language")
            self.move_telescope_button.config(text="Move telescope")

if __name__ == "__main__":
    app = TelescopeGUI()
    app.root.mainloop()
