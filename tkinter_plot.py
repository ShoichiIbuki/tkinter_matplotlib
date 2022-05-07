# %%
# 参考 https://water2litter.net/rum/post/python_tkinter_matplotlib/

import tkinter as tk
import tkinter.ttk as ttk
from tokenize import String
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np

from glob import glob

from make_graph import read_log



class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Matplotlib in tkinter')
        self.w = self.master.winfo_screenwidth()  # スクリーンサイズの取得
        self.h = self.master.winfo_screenheight()  # スクリーンサイズの取得
        self.master.geometry(str(self.w)+"x"+str(self.h)+"+0+0")  # ウィンドウサイズ(幅x高さ)
        self.master.state("zoomed")  # 最大化
        self.pack()

        """Default Setting"""
        self.log_list = sorted(glob("./logs/*.txt"))
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0,500)
        self.ax.set_ylim(0.02,0.05)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.grid(axis='both')

        self.y_min=0

        self.create_widgets()
        self.start_up()
        self.draw_plot()

    def create_widgets(self):
        self.canvas_frame = tk.Frame(self.master, width=self.w//6, height=3*self.h//4)
        self.canvas_frame.place(x=self.w//18,y=self.h//10)
        self.control_frame = tk.Frame(self.master, width=self.w//5, height=3*self.h//4)
        self.control_frame.place(x=11*self.w//18,y=self.h//10)

        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # select ax_x
        self.x_v = tk.IntVar()
        self.x_scale = tk.Scale(self.control_frame,
            length = 500,
            variable=self.x_v,
            from_=0.0,
            to=1000,
            resolution=1,
            orient=tk.HORIZONTAL,
            command=self.update_plot)
        self.x_scale.pack(anchor=tk.NW)

        # select ax_y
        self.y_v = tk.DoubleVar()
        self.y_scale = tk.Scale(self.control_frame,
            length = 500,
            variable=self.y_v,
            from_=0.0,
            to=0.1,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            command=self.update_plot)
        self.y_scale.pack(anchor=tk.NW)

        #  select log.txt
        self.lg_label  = ttk.Label(self.control_frame,
            width=60,
            text='Select log',
            font=("Arial",10,"bold"))
        self.lg_label.pack(anchor=tk.NW, side=tk.TOP)

        self.lg_v = tk.StringVar()
        self.lg_cmbx =  ttk.Combobox(self.control_frame,
            width=60,
            textvariable=self.lg_v,
            values=self.log_list,
            state='readonly')
        self.lg_cmbx.pack(anchor=tk.NW)

        # select plot mode
        self.mode_v = tk.IntVar(value = 1)
        self.mode_radio_1 = ttk.Radiobutton(self.control_frame,
            text='x: Epoch    y: ChamferDistance',
            value=1,
            variable=self.mode_v)
        self.mode_radio_1.pack(padx=5, pady=5, anchor=tk.NW)

        self.mode_radio_2 = ttk.Radiobutton(self.control_frame,
            text='x: SNR   y: ChamferDistance',
            value=2,
            variable=self.mode_v)
        self.mode_radio_2.pack(padx=5, pady=5, anchor=tk.NW)

        # enter legend
        self.x_label  = ttk.Label(self.control_frame,
            width=60,
            text='Enter xlabel in the text box below',
            font=("Arial",10,"bold"))
        self.x_label.pack(anchor=tk.NW, side=tk.TOP)

        self.xlabel_v = tk.StringVar(value = "X")
        self.xlabel_entry  = ttk.Entry(self.control_frame,
            width=30,
            textvariable=self.xlabel_v)
        self.xlabel_entry.pack(padx=5, pady=5,anchor=tk.NW, side=tk.TOP)

        # enter legend
        self.y_label  = ttk.Label(self.control_frame,
            width=60,
            text='Enter ylabel in the text box below',
            font=("Arial",10,"bold"))
        self.y_label.pack(anchor=tk.NW, side=tk.TOP)

        self.ylabel_v = tk.StringVar(value = "Y")
        self.ylabel_entry  = ttk.Entry(self.control_frame,
            width=30,
            textvariable=self.ylabel_v)
        self.ylabel_entry.pack(padx=5, pady=5,anchor=tk.NW, side=tk.TOP)

        # enter legend
        self.legend_label  = ttk.Label(self.control_frame,
            width=60,
            text='Enter legend in the text box below (commas-separated)',
            font=("Arial",10,"bold"))
        self.legend_label.pack(anchor=tk.NW, side=tk.TOP)

        self.legend_v = tk.StringVar(value = "")
        self.legend_entry  = ttk.Entry(self.control_frame,
            width=50,
            textvariable=self.legend_v)
        self.legend_entry.pack(padx=5, pady=5,anchor=tk.N, side=tk.TOP, fill=tk.BOTH, expand=True)


        # plot button
        self.plt_btn = tk.Button(self.control_frame,
            width=10,
            text='Plot')
        self.plt_btn.bind("<ButtonPress>", self.draw_plot)
        self.plt_btn.pack(anchor=tk.SE, side='left')

        # set button
        self.add_btn = tk.Button(self.control_frame,
            width=10,
            text='Set')
        self.add_btn.bind("<ButtonPress>", self.draw_plot)
        self.add_btn.pack(anchor=tk.SE, side='left')

        # reset button
        self.add_btn = tk.Button(self.control_frame,
            width=10,
            text='Reset')
        self.add_btn.bind("<ButtonPress>", self.draw_plot)
        self.add_btn.pack(anchor=tk.SE, side='left')

        
    def start_up(self):
        self.x_v.set(200)
        self.y_v.set(0.05)
        self.legend_v.set("")

    def reset_ax(self):
        self.ax.set_xlim(0,500)
        self.ax.set_ylim(0.02,0.05)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.grid(axis='both')
        self.p = self.ax.plot([],[], 'green', marker='o', markersize=2)

        self.y_min=0

    def draw_plot(self, event=None):        
        mode = self.mode_v.get()
        if mode == 1:
            label = ['Epoch', 'Test Acc']
        elif mode == 2:
            label = ['SNR', 'Test Acc']
        if event is not None:
            if event.widget.cget('text') == 'Plot':
                self.set_plot(label)
            elif event.widget.cget('text') == 'Set':
                # set legend
                legend = self.legend_v.get().split(',')
                if len(legend) > 0:
                    try:                
                        self.ax.legend(legend)
                    except Exception as e:
                        print('Exception Ocuured (legend)')
                        print(e)
                # set label
                xname = self.xlabel_v.get()
                yname = self.ylabel_v.get()
                self.ax.set_xlabel(xname)
                self.ax.set_ylabel(yname)
            elif event.widget.cget('text') == 'Reset':
                self.ax.cla()
                self.reset_ax()
                self.start_up()
        self.canvas.draw()

    def set_plot(self, label=['x','y']):
        try:
            df = read_log(self.lg_v.get(), label)
            x = df[label[0]].values
            y = df[label[1]].values
            new_plot = self.ax.plot(x,y, marker='o', markersize=2)
            hor = self.x_v.get()
            vert = self.y_v.get()
            self.y_min = y.min() if y.size else 0
            self.ax.set_xlim(0,hor)
            self.ax.set_ylim(self.y_min,vert)
            
            self.xlabel_entry.delete(0,tk.END)
            self.ylabel_entry.delete(0,tk.END)
            self.xlabel_entry.insert(tk.END,label[0])
            self.ylabel_entry.insert(tk.END,label[1])
        except Exception as e:
            print(e)
            print("Select other log text")


    def update_plot(self, event=None):
        try:
            hor = self.x_v.get()
            vert = self.y_v.get()
            self.ax.set_xlim(0,hor)
            self.ax.set_ylim(self.y_min,vert)
            self.canvas.draw()  
        except Exception as e:
            print(e)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
# %%