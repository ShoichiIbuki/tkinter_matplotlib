# %%
# 参考 https://water2litter.net/rum/post/python_tkinter_matplotlib/
# 参考 https://stackoverflow.com/questions/66992052/rotate-matplotlib-navigationtoolbar2tk-to-make-it-vertical

import tkinter as tk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np

from glob import glob

from txt_handling import read_log

# NavigationToolbar2Tkの継承クラス(垂直に表示するために追加)
class VerticalNavigationToolbar2Tk(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window, pack_toolbar=False)

    # override _Button() to re-pack the toolbar button in vertical direction
    def _Button(self, text, image_file, toggle, command):
        b = super()._Button(text, image_file, toggle, command)
        b.pack(side=tk.TOP) # re-pack button in vertical direction
        return b

    # override _Spacer() to create vertical separator
    def _Spacer(self):
        s = tk.Frame(self, width=26, relief=tk.RIDGE, bg="DarkGray", padx=2)
        s.pack(side=tk.TOP, pady=5) # pack in vertical direction
        return s

    # disable showing mouse position in toolbar
    def set_message(self, s):
        pass


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Matplotlib in tkinter')
        self.w = self.master.winfo_screenwidth()  # スクリーンサイズの取得
        self.h = self.master.winfo_screenheight()  # スクリーンサイズの取得
        self.master.geometry(str(self.w)+"x"+str(19*self.h//20)+"+0+0")  # ウィンドウサイズ(幅x高さ)
        # self.master.state("iconic")  # 最大化
        self.pack()

        """Default Setting"""
        # all font size setting
        plt.rcParams['font.size'] = 17

        self.log_list = sorted(glob("./logs/*.txt"))
        self.fig = Figure(figsize=(10,8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0,500)
        self.ax.set_ylim(0.02,0.05)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.grid(axis='both')

        self.y_min=0

        self.create_widgets()
        self.create_controller()
        self.push_button()


    def create_widgets(self):
        self.canvas_frame = tk.Frame(self.master, width=19*self.w//20, height=19*self.h//20)
        # self.canvas_frame.place(x=self.w//18,y=self.h//10)
        # self.canvas_frame.place(x=0,y=0)
        self.canvas_frame.pack()

        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.toolbar = VerticalNavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

    def create_controller(self):
        # 操作ボタン配置用のサブウィンドウを作成
        self.sub_win = tk.Toplevel()
        self.sub_win.title('Controller')
        self.sub_win.geometry(str(5*self.w//12)+"x"+str(19*self.h//20)+"+0+0")
        self.create_plot_frame()    # plotコントローラーの作成

        # メニューバーの作成
        menuBar = tk.Menu()
        self.sub_win.config(menu=menuBar)
        menuBar.add_command(label='Plot',command=lambda: self.change_frame(self.sub_win,'Plot'))
        menuBar.add_command(label='Scatter',command=lambda: self.change_frame(self.sub_win,'Scatter'))
        # menuBar.add_cascade(labe='MODE', menu=mode_menu)

        self.sub_win.attributes("-topmost", True) # 最前面で固定する
        # xボタンを押すと閉じるのではなく最小化するようにする。
        self.sub_win.protocol("WM_DELETE_WINDOW", lambda: self.sub_win.iconify())

    def create_scatter_frame(self):
        self.scatter_frame = tk.Frame(self.sub_win, width=5*self.w//12, height=19*self.h/20)
        self.scatter_frame.place(x=0,y=0)
        # self.control_frame.place(x=11*self.w//18,y=self.h//10)

        # select ax_x
        ax_x_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='  X',
            font=("Arial",10,"bold"))
        ax_x_label.pack(anchor=tk.NW, side=tk.TOP)
        self.x_v = tk.DoubleVar(value=0.05)
        x_scale = tk.Scale(self.scatter_frame,
            length = 500,
            variable=self.x_v,
            from_=0.0,
            to=1.0,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            command=self.update_ax)
        x_scale.pack(anchor=tk.NW)

        # select ax_y
        ax_y_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='  Y',
            font=("Arial",10,"bold"))
        ax_y_label.pack(anchor=tk.NW, side=tk.TOP)
        self.y_v = tk.DoubleVar(value=0.05)
        y_scale = tk.Scale(self.scatter_frame,
            length = 500,
            variable=self.y_v,
            from_=0.0,
            to=1.0,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            command=self.update_ax)
        y_scale.pack(anchor=tk.NW)

        # select marker-size
        m_size_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='marker size',
            font=("Arial",10,"bold"))
        m_size_label.pack(anchor=tk.NW, side=tk.TOP)
        self.m_size_v = tk.IntVar(value=40)
        m_scale = tk.Scale(self.scatter_frame,
            length = 500,
            variable=self.m_size_v,
            from_=0,
            to=100,
            resolution=1,
            orient=tk.HORIZONTAL,
            command=self.update_ax)
        m_scale.pack(anchor=tk.NW)

        #  select log.txt
        lg_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='Select data',
            font=("Arial",10,"bold"))
        lg_label.pack(anchor=tk.NW, side=tk.TOP)
        self.lg_v = tk.StringVar()
        lg_cmbx =  ttk.Combobox(self.scatter_frame,
            width=60,
            textvariable=self.lg_v,
            values=self.log_list,
            state='readonly')
        lg_cmbx.pack(anchor=tk.NW)

        # select plot mode
        self.mode_v = tk.IntVar(value = 1)
        mode_radio_1 = ttk.Radiobutton(self.scatter_frame,
            text='x: Epoch    y: ChamferDistance',
            value=1,
            variable=self.mode_v)
        mode_radio_1.pack(padx=5, pady=5, anchor=tk.NW)

        mode_radio_2 = ttk.Radiobutton(self.scatter_frame,
            text='x: SNR   y: ChamferDistance',
            value=2,
            variable=self.mode_v)
        mode_radio_2.pack(padx=5, pady=5, anchor=tk.NW)

        # approximate curve
        self.cur_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='Approximate curve',
            font=("Arial",10,"bold"))
        self.cur_label.pack(anchor=tk.NW, side=tk.TOP)
        self.cur_order_v = tk.IntVar(value = 0)
        order_cmbx =  ttk.Combobox(self.scatter_frame,
            width=20,
            textvariable=self.cur_order_v,
            values=list(range(10)),
            state='readonly')
        order_cmbx.pack(anchor=tk.NW)

        # enter legend
        x_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='Enter xlabel in the text box below',
            font=("Arial",10,"bold"))
        x_label.pack(anchor=tk.NW, side=tk.TOP)

        self.xlabel_v = tk.StringVar(value = "X")
        self.xlabel_entry  = ttk.Entry(self.scatter_frame,
            width=30,
            textvariable=self.xlabel_v)
        self.xlabel_entry.pack(padx=5, pady=5,anchor=tk.NW, side=tk.TOP)

        # enter legend
        y_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='Enter ylabel in the text box below',
            font=("Arial",10,"bold"))
        y_label.pack(anchor=tk.NW, side=tk.TOP)

        self.ylabel_v = tk.StringVar(value = "Y")
        self.ylabel_entry  = ttk.Entry(self.scatter_frame,
            width=30,
            textvariable=self.ylabel_v)
        self.ylabel_entry.pack(padx=5, pady=5,anchor=tk.NW, side=tk.TOP)

        # enter legend
        legend_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='Enter legend in the text box below (commas-separated)',
            font=("Arial",10,"bold"))
        legend_label.pack(anchor=tk.NW, side=tk.TOP)

        self.legend_v = tk.StringVar(value = "")
        self.legend_entry  = ttk.Entry(self.scatter_frame,
            width=50,
            textvariable=self.legend_v)
        self.legend_entry.pack(padx=5, pady=5,anchor=tk.N, side=tk.TOP, fill=tk.X, expand=True)

        # enter marker_shape
        marker_label  = ttk.Label(self.scatter_frame,
            width=60,
            text='marker-shape (".","o","v","1","2","8","s","p","*","h","+","x","d","|")',
            font=("Arial",10,"bold"))
        marker_label.pack(anchor=tk.NW, side=tk.TOP)

        self.marker_v = tk.StringVar(value = "")
        self.marker_entry  = ttk.Entry(self.scatter_frame,
            width=50,
            textvariable=self.marker_v)
        self.marker_entry.pack(padx=5, pady=5,anchor=tk.N, side=tk.TOP, fill=tk.X, expand=True)


        # plot button
        sct_btn = tk.Button(self.scatter_frame,
            width=10,
            text='Scatter')
        sct_btn.bind("<ButtonPress>", self.push_button)
        sct_btn.pack(anchor=tk.SE, side='left')

        # set button
        add_btn = tk.Button(self.scatter_frame,
            width=10,
            text='Set')
        add_btn.bind("<ButtonPress>", self.push_button)
        add_btn.pack(anchor=tk.SE, side='left')

        # reset button
        reset_btn = tk.Button(self.scatter_frame,
            width=10,
            text='Reset')
        reset_btn.bind("<ButtonPress>", self.push_button)
        reset_btn.pack(anchor=tk.SE, side='left')

    def create_plot_frame(self):
        self.plot_frame = tk.Frame(self.sub_win, width=5*self.w//12, height=19*self.h/20)
        self.plot_frame.place(x=0,y=0)
        # self.control_frame.place(x=11*self.w//18,y=self.h//10)

        # select ax_x
        ax_x_label  = ttk.Label(self.plot_frame,
            width=60,
            text='  X',
            font=("Arial",10,"bold"))
        ax_x_label.pack(anchor=tk.NW, side=tk.TOP)
        self.x_v = tk.IntVar(value=500)
        x_scale = tk.Scale(self.plot_frame,
            length = 500,
            variable=self.x_v,
            from_=0.0,
            to=1000,
            resolution=1,
            orient=tk.HORIZONTAL,
            command=self.update_ax)
        x_scale.pack(anchor=tk.NW)

        # select ax_y
        ax_y_label  = ttk.Label(self.plot_frame,
            width=60,
            text='  Y',
            font=("Arial",10,"bold"))
        ax_y_label.pack(anchor=tk.NW, side=tk.TOP)
        self.y_v = tk.DoubleVar(value=0.05)
        y_scale = tk.Scale(self.plot_frame,
            length = 500,
            variable=self.y_v,
            from_=0.0,
            to=0.1,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            command=self.update_ax)
        y_scale.pack(anchor=tk.NW)

        # select marker-size
        m_size_label  = ttk.Label(self.plot_frame,
            width=60,
            text='marker size',
            font=("Arial",10,"bold"))
        m_size_label.pack(anchor=tk.NW, side=tk.TOP)
        self.m_size_v = tk.IntVar(value=2)
        m_scale = tk.Scale(self.plot_frame,
            length = 500,
            variable=self.m_size_v,
            from_=0,
            to=50,
            resolution=1,
            orient=tk.HORIZONTAL,
            command=self.update_ax)
        m_scale.pack(anchor=tk.NW)

        #  select log.txt
        lg_label  = ttk.Label(self.plot_frame,
            width=60,
            text='Select data',
            font=("Arial",10,"bold"))
        lg_label.pack(anchor=tk.NW, side=tk.TOP)

        self.lg_v = tk.StringVar()
        lg_cmbx =  ttk.Combobox(self.plot_frame,
            width=60,
            textvariable=self.lg_v,
            values=self.log_list,
            state='readonly')
        lg_cmbx.pack(anchor=tk.NW)

        # select plot mode
        self.mode_v = tk.IntVar(value = 1)
        mode_radio_1 = ttk.Radiobutton(self.plot_frame,
            text='x: Epoch    y: ChamferDistance',
            value=1,
            variable=self.mode_v)
        mode_radio_1.pack(padx=5, pady=5, anchor=tk.NW)

        mode_radio_2 = ttk.Radiobutton(self.plot_frame,
            text='x: SNR   y: ChamferDistance',
            value=2,
            variable=self.mode_v)
        mode_radio_2.pack(padx=5, pady=5, anchor=tk.NW)

        # enter legend
        x_label  = ttk.Label(self.plot_frame,
            width=60,
            text='Enter xlabel in the text box below',
            font=("Arial",10,"bold"))
        x_label.pack(anchor=tk.NW, side=tk.TOP)

        self.xlabel_v = tk.StringVar(value = "X")
        self.xlabel_entry  = ttk.Entry(self.plot_frame,
            width=30,
            textvariable=self.xlabel_v)
        self.xlabel_entry.pack(padx=5, pady=5,anchor=tk.NW, side=tk.TOP)

        # enter legend
        y_label  = ttk.Label(self.plot_frame,
            width=60,
            text='Enter ylabel in the text box below',
            font=("Arial",10,"bold"))
        y_label.pack(anchor=tk.NW, side=tk.TOP)

        self.ylabel_v = tk.StringVar(value = "Y")
        self.ylabel_entry  = ttk.Entry(self.plot_frame,
            width=30,
            textvariable=self.ylabel_v)
        self.ylabel_entry.pack(padx=5, pady=5,anchor=tk.NW, side=tk.TOP)

        # enter legend
        legend_label  = ttk.Label(self.plot_frame,
            width=60,
            text='Enter legend in the text box below (commas-separated)',
            font=("Arial",10,"bold"))
        legend_label.pack(anchor=tk.NW, side=tk.TOP)

        self.legend_v = tk.StringVar(value = "")
        self.legend_entry  = ttk.Entry(self.plot_frame,
            width=50,
            textvariable=self.legend_v)
        self.legend_entry.pack(padx=5, pady=5,anchor=tk.N, side=tk.TOP, fill=tk.X, expand=True)

        # enter marker_shape
        marker_label  = ttk.Label(self.plot_frame,
            width=60,
            text='marker-shape (".","o","v","1","2","8","s","p","*","h","+","x","d","|")',
            font=("Arial",10,"bold"))
        marker_label.pack(anchor=tk.NW, side=tk.TOP)

        self.marker_v = tk.StringVar(value = "")
        self.marker_entry  = ttk.Entry(self.plot_frame,
            width=50,
            textvariable=self.marker_v)
        self.marker_entry.pack(padx=5, pady=5,anchor=tk.N, side=tk.TOP, fill=tk.X, expand=True)


        # plot button
        plt_btn = tk.Button(self.plot_frame,
            width=10,
            text='Plot')
        plt_btn.bind("<ButtonPress>", self.push_button)
        plt_btn.pack(anchor=tk.SE, side='left')

        # set button
        add_btn = tk.Button(self.plot_frame,
            width=10,
            text='Set')
        add_btn.bind("<ButtonPress>", self.push_button)
        add_btn.pack(anchor=tk.SE, side='left')

        # reset button
        reset_btn = tk.Button(self.plot_frame,
            width=10,
            text='Reset')
        reset_btn.bind("<ButtonPress>", self.push_button)
        reset_btn.pack(anchor=tk.SE, side='left')

    def change_frame(self,window,mode):
        children = window.winfo_children()
        for child in children:
            child.destroy()
        if mode == 'Plot':
            self.create_plot_frame()
        elif mode == 'Scatter':
            self.create_scatter_frame()

    def reset_ax(self):
        self.ax.set_xlim(0,500)
        self.ax.set_ylim(0.02,0.05)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.grid(axis='both')
        
        self.y_min=0

    def push_button(self, event=None):
        mode = self.mode_v.get()
        if mode == 1:
            label = ['Epoch', 'Test Acc']
        elif mode == 2:
            label = ['SNR', 'Test Acc']
        if event is not None:
            if event.widget.cget('text') == 'Plot':
                self.draw_plot(label)
            elif event.widget.cget('text') == 'Scatter':
                self.draw_scatter()
            elif event.widget.cget('text') == 'Set':
                # set legend
                legend = self.legend_v.get().split(',')
                if len(legend) > 0:
                    try:                
                        self.ax.legend(legend)
                    except Exception as e:
                        print('Exception Ocuured (legend)')
                        print(e)
                # set marker
                marker = self.marker_v.get().split(',')
                marker_s = self.m_size_v.get()
                if len(marker)==1:
                    if marker[0]=='':
                        marker[0]='o'
                elif len(marker) < len(self.ax.lines):
                    for i in range(len(self.ax.lines)-len(marker)):
                        marker.append('o') 
                for i, ax_line in enumerate(self.ax.lines):
                    try:
                        ax_line.set_markersize(marker_s)
                        ax_line.set_marker(marker[i])
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
        self.canvas.draw()

    def draw_plot(self, label=['x','y']):
        marker_s = self.m_size_v.get()
        try:
            df = read_log(self.lg_v.get(), label)
            x = df[label[0]].values
            y = df[label[1]].values
            new_plot = self.ax.plot(x,y, marker='o', markersize=marker_s)
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
            print("Exception Occured (in draw scatter)")
            print("Select other log text")

    def draw_scatter(self, label=['Chamferdistance','Chamferdistance_in_categories']):
        marker_s = self.m_size_v.get()
        order = self.cur_order_v.get()
        try:
            df = read_log(self.lg_v.get(), label)
            x = df[label[0]].values
            y = df[label[1]].values
            # 近似曲線を作る
            if order != 0:
                linear_model=np.polyfit(x,y,order)
                linear_model_fn=np.poly1d(linear_model)
                x_s=np.arange(0.01,0.06,0.01)
                self.ax.plot(x_s,linear_model_fn(x_s),color="#000000")
            for (i, j) in zip(x, y):
                new_scatter = self.ax.scatter(i,j, marker='o', s=marker_s) # 点をplotする
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
            print("Exception Occured (in draw scatter)")

    def update_ax(self, event=None):
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