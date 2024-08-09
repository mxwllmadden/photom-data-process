# -*- coding: utf-8 -*-
"""
Contains Controller Class for the App

Define all app behavior/events in this class.
"""


from tkinter import filedialog
import os
from PIL import Image, ImageTk
import threading
from typing import List, Tuple
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tkk
from MSPhotom.data import MSPData, DataManager
from MSPhotom.gui.main import AppView
from MSPhotom import analysis
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class MSPApp:
    def __init__(self):
        """
        Initialize an instance of the MSPhotom App.

        Returns
        -------
        None.

        """
        self.view = AppView()
        self.data = MSPData()

        # Setup Events
        self.view.image_tab.fileselectbutton.config(
            command=self.get_image_directory)
        self.view.image_tab.loadbutton.config(
            command=self.load_runs)
        self.view.image_tab.regselbutton.config(
            command=self.region_selection)
        self.view.image_tab.processbutton.config(
            command=self.processimages)
        self.view.image_tab.reset_button.config(
            command=self.reset_data)

        self.view.data_tab.refresh_but.config(
            command=self.refresh_data_view)
        self.view.data_tab.sv_data_but.config(
            command=self.save_data)
        self.view.data_tab.load_data_but.config(
            command=self.load_data)

        self.view.regression_tab.reset_button.config(
            command=self.reset_regression)
        self.view.regression_tab.reset_graph_button.config(
            command=self.reset_graph)
        self.view.regression_tab.load_button.config(
            command=self.input_bin)

        self.view.regression_tab.regress_button.config(
            command=self.regress_fibers)
        self.view.regression_tab.input_run_button.config(
            command=self.input_run)
        self.view.regression_tab.input_graph_params.config(
            command=self.input_graph_params)
        self.view.regression_tab.graph_corrsig_button.config(
            command=self.update_canvas_with_plot_corrsig)
        self.view.regression_tab.graph_channel_button.config(
            command=self.update_canvas_with_plot_channel
        )
        self.refresh_data_view()
        self.view.update_state('IP - Parameter Entry')
        self.view.mainloop()

    def get_image_directory(self):
        """
        Get directory with filedialog then place directory path in corresponding text field.
        """
        self.view.image_tab.topdirectory.set(
            filedialog.askdirectory())

    def load_runs(self):
        """
        Scan target directory for appropriate run folders then display runs
        and update state and photometry data object.

        """
        # Pull the data we need from View
        target_directory = self.view.image_tab.topdirectory.get()
        date_start = self.view.image_tab.date_start
        date_end = self.view.image_tab.date_end
        date_start_num = datetonum(date_start.get())
        date_end_num = datetonum(date_end.get())

        ani_prefix = self.view.image_tab.ani_prefix.get()
        ani_start = self.view.image_tab.ani_start
        ani_end = self.view.image_tab.ani_end

        img_prefix = self.view.image_param_tab.img_prefix.get()
        img_per_trial_per_channel = self.view.image_param_tab.img_per_trial_per_channel
        num_interpolated_channels = self.view.image_param_tab.num_interpolated_channels
        roi_names = [var.get() for var in self.view.image_param_tab.roi_names]
        roi_names = [name.replace('_', '') for name in roi_names]
        
        # Check to ensure user input is appropriate
        if not os.path.exists(target_directory):
            self.view.image_tab.topdirectory.set('BAD PATH')
            return

        if (date_end_num is None) and (date_end_num is None):
            date_start.set("ERROR")
            date_end.set("ERROR")
            return

        if not (ani_start.get().isdigit() and ani_end.get().isdigit()):
            ani_start.set('ERROR')
            ani_end.set('ERROR')
            return
        ani_start = int(ani_start.get())
        ani_end = int(ani_end.get())

        if not img_per_trial_per_channel.get().isdigit():
            img_per_trial_per_channel.set('ERROR')
            return
        img_per_trial_per_channel = int(img_per_trial_per_channel.get())

        if not num_interpolated_channels.get().isdigit():
            num_interpolated_channels.set('ERROR')
            return
        num_interpolated_channels = int(num_interpolated_channels.get())
        
        # Generate candidate run path and filter to only existing paths
        candidate_date_paths = [target_directory+"/"+numtodate(date)
                                for date in range(date_start_num, date_end_num+1)]
        candidate_date_paths = [path for path in candidate_date_paths
                                if os.path.exists(path)]

        candidate_run_paths = [f'{path}/{ani_prefix} {ani_num} Run {run_num}'
                               for run_num in range(50)
                               for ani_num in range(ani_start, ani_end+1)
                               for path in candidate_date_paths]

        run_paths = [path for path in candidate_run_paths
                     if os.path.exists(path)]

        filetree_entries = [(path.split('/')[-2], path.split('/')[-1])
                            for path in run_paths]

        animal_names = list(set([path.split('/')[-1] for path in run_paths]))

        # Update View
        self.view.updatefiletreedisplay(filetree_entries)
        self.view.update_state('IP - Create Fiber Masks')

        # Update Data
        self.data.target_directory: str = target_directory
        self.data.img_date_range: Tuple[str, str] = (date_start.get(),
                                                     date_end.get())
        self.data.animal_names: List[str] = animal_names
        self.data.run_path_list: List[str] = run_paths
        self.data.img_prefix: str = img_prefix
        self.data.img_per_trial_per_channel: int = img_per_trial_per_channel
        self.data.num_interpolated_channels: int = num_interpolated_channels
        self.data.roi_names: List[str] = roi_names


    def region_selection(self):
        """
        Generate a popup region selection window and define its behavior.
        """
        self.view.update_state('None')
        self.data_regsel = {'ROIs':
                            ['Background Fiber', 'Correction Fiber']
                            +
                            [roi.get() for roi in
                             self.view.image_param_tab.roi_names
                             if roi.get() != ''],
                            'roi_cursor': 0,
                            'displayimg': self.region_selection_get_image(),
                            'mask_coords': []
                            }
        popout = self.view.popout_regsel(reg_names=self.data_regsel['ROIs'],
                                         img=self.data_regsel['displayimg'])
        
        popout.bind('<Destroy>', self.region_selection_prematureclose)
        self.view.regsel.selectioncanvas.bind(
            "<B1-Motion>", self.region_selection_drag)
        self.view.regsel.confirmbutton.config(
            command=self.region_selection_button_select)

    def region_selection_get_image(self):
        """
        Load an image from the first runpath to use as a backdrop for region/fiber
        selection.
        """
        frpath = self.data.run_path_list[0]
        imprefix = self.data.img_prefix
        impath = f'{frpath}/{imprefix}_2.tif'
        with Image.open(impath) as im:
            return ImageTk.PhotoImage(im)

    def region_selection_prematureclose(self, event):
        """
        Reset view state if window is closed prematurely.
        """
        if event.widget == event.widget.winfo_toplevel():
            self.view.update_state('IP - Create Fiber Masks')
            self.data_regsel = None

    def region_selection_drag(self, event):
        """
        Allow user to move selection oval on left mouse click+drag
        """
        selcanvs = self.view.regsel.selectioncanvas
        selectoval = self.view.regsel.selectoval
        selcanvs.moveto(selectoval, event.x-50, event.y-50)

    def region_selection_button_select(self):
        """
        On selection of region, store information and display selected fiber.
        Proceeds to next fiber/region when done or closes region selection window
        and updates data and view correspondingly
        """
        selcanvs = self.view.regsel.selectioncanvas
        selectoval = self.view.regsel.selectoval
        currentregionstrvar = self.view.regsel.currentregion
        # Get location of oval
        x, y, dx, dy = selcanvs.coords(selectoval)
        # Leave behind a marker for the location
        new_circle_marker = selcanvs.create_oval(x, y, dx, dy,
                                                 outline='blue', width=3)
        # Save the coordinates
        self.data_regsel['mask_coords'].append((x, y, dx, dy))
        # Iterate to next region
        self.data_regsel['roi_cursor'] += 1
        if self.data_regsel['roi_cursor'] >= len(self.data_regsel['ROIs']):
            # Time to quit and dump all data_regsel into data
            self.data.fiber_labels = self.data_regsel['ROIs']
            self.data.fiber_coords = self.data_regsel['mask_coords']
            self.view.regsel.container.destroy()
            self.view.update_state('IP - Ready to Process')
        else:
            currentregionname = self.data_regsel['ROIs'][
                self.data_regsel['roi_cursor']]
            # Set the label for the current region
            currentregionstrvar.set(f'Currently selecting {currentregionname}')

    def processimages(self):
        """
        Update view and start image processing in another thread
        """
        # Update View
        self.view.update_state('IP - Processing Images')
        # Create and initialize the thread for image loading/processing
        pross_thread = threading.Thread(target=analysis.imageprocess.process_main,
                                        args=(self.data,
                                              self),
                                        daemon=True)
        pross_thread.start()

    def reset_data(self):
        """
        Remove data object and create new. Update state accordingly.
        """
        # Update View
        self.view.update_state('IP - Parameter Entry')

        # Recreate Data
        self.data = MSPData()

    def refresh_data_view(self):
        """
        Refresh the inspection window with current information about the data
        object
        """
        self.view.data_tab.update(self.data.__dict__)

    def save_data(self):
        """
        Save data object to file in pickle format
        """
        file = filedialog.asksaveasfilename(defaultextension='.pkl',
                                            filetypes=[
                                                ('Python Pickle', '*.pkl')],
                                            title='Save Data')
        if file is not None:
            manage = DataManager(self.data)
            manage.save(file)

    def load_data(self):
        """
        Load data from pickle file
        
        UNSAFE! Depickling allows the execution of arbitrary code. You should
        NEVER open a pickle file from a non-trusted source.
        """
        file = filedialog.askopenfilename(defaultextension='.pkl',
                                          filetypes=[
                                              ('Python Pickle', '*.pkl')],
                                          title='Load Data')
        if file is not None:
            manage = DataManager(self.data)
            self.data = MSPData(**manage.load(file).__dict__)
        self.set_state_based_on_data()
        # This logic is here to clear the graph plot is a new pickle file is loaded
        for widget in self.view.regression_tab.graphcanvas.winfo_children():
            widget.destroy()


    def reset_regression(self):
        """
        Remove data object and create new. Update state accordingly.
        """
        # Update View
        regression_attributes = [
            'bin_size','regressed_traces_by_run_signal_trial','graph_of_choice',
            'graph_run_selected', 'graph_ch_selected', 'graph_reg_selected',
            'graph_trial_selected'
        ]

        for attr in regression_attributes:
            if hasattr(self.data, attr):
                setattr(self.data, attr, None)
        for widget in self.view.regression_tab.graphcanvas.winfo_children():
            widget.destroy()
        self.view.regression_tab.runprog['value'] = 0
        print("Graph canvas cleared")
        self.view.update_state('RG - Processing Done Ready to Input Bin')



    def reset_graph(self):
        """
        Remove data object and create new. Update state accordingly.
        """
        regression_attributes = [
            'graph_of_choice', 'graph_run_selected', 'graph_ch_selected',
            'graph_reg_selected', 'graph_trial_selected'
        ]

        for attr in regression_attributes:
            if hasattr(self.data, attr):
                setattr(self.data, attr, None)

        # Clear the graphcanvas
        for widget in self.view.regression_tab.graphcanvas.winfo_children():
            widget.destroy()
        print("Graph canvas cleared")

        # Update View
        self.view.update_state('RG - Regression Done Ready to Graph')

    def input_bin(self):
        bin_size = self.view.regression_tab.bin_size
        if not bin_size.get().isdigit():
            bin_size.set('ERROR')
            return
        bin_size = int(bin_size.get())
        self.view.regression_tab.num_regs = self.data.num_regions
        self.view.regression_tab.num_runs = self.data.num_runs
        self.view.update_state('RG - Ready to Regress')
        self.data.bin_size: int = bin_size

    def regress_fibers(self):
        # Update View
        # in between
        self.view.update_state('RG - Regressing')
        # Create and initialize the thread for image loading/processing
        regress_thread = threading.Thread(target=analysis.regression.regression_main,
                                        args=(self.data,
                                              self),
                                        daemon=True)
        regress_thread.start()
        run_options = list(self.data.traces_by_run_signal_trial.keys())
        self.view.regression_tab.run_selector['values'] = run_options
        # Set default value
        if run_options:
            self.view.regression_tab.run_selector.set(run_options[0])
        else:
            self.view.regression_tab.run_selector.set("")
        # in function
    def input_run(self):
        run_selected = self.view.regression_tab.run_select
        run_selected_value = run_selected.get()  # Get the actual string value from StringVar

        try:
            reg_options = list(self.data.roi_names)
        except TypeError:
            reg_options = ""

        try:
            ch_options = list(self.data.ch_names_by_run[run_selected_value])
        except KeyError:
            ch_options = []  # Handle the case where the run_selected_value is not found

        self.view.regression_tab.reg_selector['values'] = reg_options
        self.view.regression_tab.ch_selector['values'] = ch_options

        # Set default value
        if ch_options:
            self.view.regression_tab.ch_selector.set(ch_options[0])
        else:
            self.view.regression_tab.ch_selector.set("")

        if reg_options:
            self.view.regression_tab.reg_selector.set(reg_options[0])
        else:
            self.view.regression_tab.reg_selector.set("")

        self.view.update_state('RG - Ready for Params')
        self.data.graph_run_selected = run_selected_value

    def input_graph_params(self):
        reg_selected = self.view.regression_tab.reg_select
        ch_selected = self.view.regression_tab.ch_select
        inputted_trial = self.view.regression_tab.trial_select
        if not inputted_trial.get().isdigit():
            inputted_trial.set('ERROR')
        inputted_trial = int(inputted_trial.get())
        self.view.update_state('RG - Graph Selection')
        self.data.graph_reg_selected = reg_selected.get()
        self.data.graph_ch_selected = ch_selected.get()
        self.data.graph_trial_selected = inputted_trial

    def update_canvas_with_plot_corrsig(self):
        # Get the Figure object from the plot function
        fig = self.corrsig_test_graph()

        # Set the figure size to fit the canvas
        fig.set_size_inches(self.view.regression_tab.graphcanvas.winfo_width() / fig.get_dpi(),
                            self.view.regression_tab.graphcanvas.winfo_height() / fig.get_dpi())

        # Create a FigureCanvasTkAgg object from the Figure with the graphcanvas as master
        fig.subplots_adjust(left=0.12, right=.95, top=.945, bottom=0.11, wspace=0.4, hspace=0.4)
        canvas = FigureCanvasTkAgg(fig, master=self.view.regression_tab.graphcanvas)
        canvas.draw()  # Draw the plot

        # Clear any existing widgets in the graphcanvas
        self.view.regression_tab.graphcanvas.delete("all")

        # Get the Tkinter widget from the FigureCanvasTkAgg object
        canvas_widget = canvas.get_tk_widget()

        # Pack the widget into the graphcanvas
        canvas_widget.pack(fill=tkk.BOTH, expand=True)

        # Ensure the graphcanvas is set to the correct size
        self.view.regression_tab.graphcanvas.config(width=330, height=330)
        self.view.update_state('RG - Graphing Done')

    def update_canvas_with_plot_channel(self):
        # Get the Figure object from the plot function
        fig = self.channel_test_graph()

        # Set the figure size to fit the canvas
        fig.set_size_inches(self.view.regression_tab.graphcanvas.winfo_width() / fig.get_dpi(),
                            self.view.regression_tab.graphcanvas.winfo_height() / fig.get_dpi())

        # Create a FigureCanvasTkAgg object from the Figure with the graphcanvas as master
        fig.subplots_adjust(left=0.12, right=.95, top=.945, bottom=0.11, wspace=0.4, hspace=0.4)
        canvas = FigureCanvasTkAgg(fig, master=self.view.regression_tab.graphcanvas)
        canvas.draw()  # Draw the plot

        # Clear any existing widgets in the graphcanvas
        self.view.regression_tab.graphcanvas.delete("all")

        # Get the Tkinter widget from the FigureCanvasTkAgg object
        canvas_widget = canvas.get_tk_widget()

        # Pack the widget into the graphcanvas
        canvas_widget.pack(fill=tkk.BOTH, expand=True)

        # Ensure the graphcanvas is set to the correct size
        self.view.regression_tab.graphcanvas.config(width=330, height=330)
        self.view.update_state('RG - Graphing Done')

    def corrsig_test_graph(self):
        graph_run = self.data.graph_run_selected
        graph_reg = self.data.graph_reg_selected
        graph_ch = self.data.graph_ch_selected
        graph_trial = self.data.graph_trial_selected

        trace_key = f'sig_{graph_reg}_{graph_ch}'
        corrsig_key = f'sig_corrsig_{graph_ch}'

        trace_data = self.data.traces_by_run_signal_trial[graph_run][trace_key]
        corrsig_data = self.data.traces_by_run_signal_trial[graph_run][corrsig_key]
        trial_data_y = trace_data[graph_trial - 1, :]
        trial_data_x = corrsig_data[graph_trial - 1, :]

        plt.style.use('fivethirtyeight')
        fig = Figure(figsize=(7, 5))
        ax = fig.add_subplot(111)
        ax.scatter(trial_data_x, trial_data_y)

        ax.set_xlabel('Corrsig-Fiber Values', fontsize=8)
        ax.set_ylabel(f'{graph_reg}-Fiber Trace Values', fontsize=8)
        ax.set_title(f'{graph_reg}-Fiber Against Corr-Fiber in {graph_ch}(Trial: {graph_trial})', fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=6)
        ax.tick_params(axis='both', which='minor', labelsize=4)

        return fig

    def channel_test_graph(self):
        graph_run = self.data.graph_run_selected
        graph_reg = self.data.graph_reg_selected
        graph_ch = self.data.graph_ch_selected
        graph_trial = self.data.graph_trial_selected
        trace_key = f'{graph_reg}_{graph_ch}'
        ch0_key = f'{graph_reg}_ch0'

        trace_data = self.data.corrsig_reg_results[graph_run][trace_key]
        ch0_data = self.data.corrsig_reg_results[graph_run][ch0_key]
        trial_data_y = trace_data[:, graph_trial - 1]
        trial_data_x = ch0_data[:, graph_trial - 1]

        # plt.scatter(trial_data_x, trial_data_y, label='Data Points')
        plt.style.use('fivethirtyeight')
        fig = Figure(figsize=(7, 5))
        ax = fig.add_subplot(111)
        ax.scatter(trial_data_x, trial_data_y)

        # Add labels and legend
        ax.set_xlabel(f'Ch0 {graph_reg}-Fiber Residual Values', fontsize=8)
        ax.set_ylabel(f'{graph_ch} {graph_reg}-Fiber Residual Values', fontsize=8)
        ax.set_title(f'{graph_ch} Against Ch0 For {graph_reg}-Fiber(Trial: {graph_trial})', fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=6)
        ax.tick_params(axis='both', which='minor', labelsize=4)

        return fig

    def set_state_based_on_data(self):
        """
        Based on the stored data in data object, update view.
        """
        humaninputs = multikey(self.data.__dict__,
                               'target_directory',
                               'img_date_range',
                               'img_prefix',
                               'img_per_trial_per_channel',
                               'num_interpolated_channels',
                               'roi_names')
        fileload = multikey(self.data.__dict__,
                            'animal_names',
                            'run_path_list')
        regionselect = multikey(self.data.__dict__,
                                'fiber_labels',
                                'fiber_coords')
        processingdone = multikey(self.data.__dict__,
                                  'fiber_masks',
                                  'traces_raw_by_run_reg',
                                  'traces_by_run_signal_trial')
        readytoregress = multikey(self.data.__dict__,
                                  'bin_size')
        regressiondone = multikey(self.data.__dict__,
                                  'regressed_traces_by_run_signal_trial')
        runinputs = multikey(self.data.__dict__,
                                'graph_run_selected')
        graphinputs = multikey(self.data.__dict__,
                               'graph_ch_selected',
                               'graph_reg_selected',
                               'graph_trial_selected')

        if not all(val is None for val in graphinputs):
            self.view.update_state('RG - Graph Selection' )
            return
        if not all(val is None for val in runinputs):
            self.view.update_state('RG - Ready for Params')
            return
        if not all(val is None for val in regressiondone):
            self.view.update_state('RG - Regression Done Ready to Graph')
            return
        if not all(val is None for val in readytoregress):
            self.view.update_state('RG - Ready to Regress')
            return
        if not all(val is None for val in processingdone):
            self.view.update_state('RG - Processing Done Ready to Input Bin')
            return
        if not all(val is None for val in regionselect):
            self.view.update_state('IP - Ready to Process')
            return
        if not all(val is None for val in fileload):
            self.view.update_state('IP - Create Fiber Masks')
            return
        if not all(val is None for val in humaninputs):
            self.view.update_state('IP - Parameter Entry')
            return

def multikey(x, *args):
    """
    Parameters
    ----------
    x : dict
        Dictionary to access multiple items.
    *args : TYPE
        Multiple keys to access within x.

    Returns
    -------
    result : TYPE
        List of values in order of supplied keys from within x.

    """
    result = []
    for arg in args:
        result.append(x[arg])
    return result

def datetonum(date: str):
    """
    Convert a date string in the format 'MM-DD-YY' to a numerical representation.

    Parameters
    ----------
    date : str
        Date string in the format 'MM-DD-YY'.

    Returns
    -------
    int
        Date in numerical format.

    """
    
    if len(date) != 8:
        return False
    if date[2] != "-" or date[5] != "-":
        return False
    mdyextract = [date[0:2], date[3:5], date[6:8]]
    if all(x.isdigit() for x in mdyextract):
        mdyextract = [int(i) for i in mdyextract]
        return ((mdyextract[1]) + (mdyextract[0]*40) + (mdyextract[2]*500))
    return False
    
def numtodate(numcode: int):
    assert isinstance(numcode, int), 'numtodate accepts integers only'
    y, d = divmod(numcode,500)
    m, d = divmod(d,40)
    return (str(m).zfill(2)+"-"+str(d).zfill(2)+"-"+str(y).zfill(2))

if __name__ == '__main__':
    MSPApp()

