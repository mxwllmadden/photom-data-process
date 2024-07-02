# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 16:11:29 2024

@author: mbmad
"""


from tkinter import filedialog
import os
from PIL import Image, ImageTk
import threading
from typing import List, Tuple

from MSPhotom.data import MSPData, DataManager
from MSPhotom.gui.main import AppView
from MSPhotom.utils import numtodate, datetonum
from MSPhotom import analysis


class MSPApp:
    def __init__(self):
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

        self.refresh_data_view()
        self.view.mainloop()

    def get_image_directory(self):
        self.view.image_tab.topdirectory.set(
            filedialog.askdirectory())

    def load_runs(self):
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
        frpath = self.data.run_path_list[0]
        imprefix = self.data.img_prefix
        impath = f'{frpath}/{imprefix}_2.tif'
        with Image.open(impath) as im:
            return ImageTk.PhotoImage(im)

    def region_selection_prematureclose(self, event):
        if event.widget == event.widget.winfo_toplevel():
            self.view.update_state('IP - Create Fiber Masks')
            self.data_regsel = None

    def region_selection_drag(self, event):
        selcanvs = self.view.regsel.selectioncanvas
        selectoval = self.view.regsel.selectoval
        selcanvs.moveto(selectoval, event.x-50, event.y-50)

    def region_selection_button_select(self):
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
        # Update View
        self.view.update_state('IP - Processing')
        # Create and initialize the thread for image loading/processing
        pross_thread = threading.Thread(target=analysis.imageprocess.process_main,
                                        args=(self.data,
                                              self),
                                        daemon=True)
        pross_thread.start()

    def reset_data(self):
        # Update View
        self.view.update_state('IP - Parameter Entry')

        # Recreate Data
        self.data = MSPData()

    def refresh_data_view(self):
        self.view.data_tab.update(self.data.__dict__)

    def save_data(self):
        file = filedialog.asksaveasfilename(defaultextension='.pkl',
                                            filetypes=[
                                                ('Python Pickle', '*.pkl')],
                                            title='Save Data')
        if file is not None:
            manage = DataManager(self.data)
            manage.save(file)

    def load_data(self):
        file = filedialog.askopenfilename(defaultextension='.pkl',
                                          filetypes=[
                                              ('Python Pickle', '*.pkl')],
                                          title='Load Data')
        if file is not None:
            manage = DataManager(self.data)
            self.data = manage.load(file)
        self.set_state_based_on_data()

    def set_state_based_on_data(self):
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
        if not all(val is None for val in processingdone):
            self.view.update_state('RG - Ready for Regression')
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
    result = []
    for arg in args:
        result.append(x[arg])
    return result


if __name__ == '__main__':
    MSPApp()
