

import os
import tkinter as tk
from tkinter import filedialog as fd
import mri_quickgifs as mquick


class quickgifs_gui():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('MRI Quickgifs')

        self.frame_files = tk.Frame()
        #Create frame of input file information
        self.input_file_lbl = tk.Label(self.frame_files, text='Input Image File:')
        self.inputfile_var = tk.StringVar(self.window)
        self.input_file_entry = tk.Entry(self.frame_files, textvariable=self.inputfile_var)
        self.input_file_btn = tk.Button(self.frame_files, text='Open', command=self.gui_open_input)

       	self.out_dir_lbl = tk.Label(self.frame_files, text='Output Dir.:')
        self.outdir_var = tk.StringVar(self.window)
        self.out_dir_entry = tk.Entry(self.frame_files, textvariable=self.outdir_var)
        self.out_dir_btn = tk.Button(self.frame_files, text='Select', command=self.gui_select_outdir)

        self.input_file_lbl.grid(row=0, column=0, sticky='w')
        self.input_file_entry.grid(row=0, column=1, sticky='w')
        self.input_file_btn.grid(row=0, column=2, sticky='w')
        self.out_dir_lbl.grid(row=1, column=0, sticky='w')
        self.out_dir_entry.grid(rows=1, column=1, sticky='w')
        self.out_dir_btn.grid(rows=1, column=2, sticky='w')

        #Create frame for options
        self.frame_options = tk.Frame()
        self.dummytr_lbl = tk.Label(self.frame_options, text='Remove Initial TRs:')
        self.dummytr_var = tk.StringVar(self.window)
        self.dummytr_var.set('0')
        self.dummytr_entry = tk.Entry(self.frame_options, textvariable=self.dummytr_var)
        self.save_var = tk.IntVar()
        self.save_var.set(0)
        self.save_cbtn = tk.Checkbutton(self.frame_options, text='Save Intermedates', variable=self.save_var, onvalue=1, offvalue=0)

        self.dummytr_lbl.grid(row=0, column=0, sticky='w')
        self.dummytr_entry.grid(row=0, column=1, sticky='w')
        self.save_cbtn.grid(row=1, column=0, sticky='w')


        #Create frame for response buttons
        self.frame_responses = tk.Frame()
        self.go_btn = tk.Button(self.frame_responses, text='Go', command=self.gui_run_btn)
        self.quit_btn = tk.Button(self.frame_responses, text='Quit', command=self.gui_quit_btn)
        self.go_btn.grid(row=0, column=0, sticky='w')
        self.quit_btn.grid(row=0, column=1, sticky='w')


    def run_loop(self):
        self.window.mainloop()


    def gui_open_input(self):
    	print('Opening file selection dialogue...')
    	#Open file-selection dialogue to get a file path and name
    	input_filename = fd.askopenfilename(parent=self.window)
    	self.inputfile_var.set(input_filename)

    def gui_select_outdir(self):
        print('Opening directory selection dialogue...')
        output_dir = fd.askdirectory(parent=self.window)
        self.outdir_var.set(output_dir)

    def gui_quit_btn(self):
        #Close the GUI
        self.window.destroy()


    def gui_run_btn(self):
        #Pull variables from the GUI and check them
        try:
            raw_input_file = str(self.inputfile_var.get())
            cuttrs = int(self.dummytr_var.get())
            saveimages = int(self.save_var.get())
            output_dir = str(self.outdir_var.get())

            ###TODO: finish this###



if __name__ == '__main__':
    obj = quickgifs_gui()
    obj.run_loop()