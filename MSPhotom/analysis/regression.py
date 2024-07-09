# -*- coding: utf-8 -*-
"""
Perform Studentized Residual Regression from organized trace data
"""
import tkinter as tk, os, dataclasses, threading, sys
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from dataclasses import dataclass
import scipy.io
from typing import List
import numpy as np
from scipy import stats
import imageprocess
from dataclasses import dataclass
import pickle

from MSPhotom.data import MSPData

def regression_main(data, controller=None):
    """
    FUNCTION1-MAIN
        FOR EACH RUN_SIGNALS IN TRACES:
            REGRESSED_SIGNALS = FUNC_REGRESS(RUN_SIGNALS)
        ABOVE GIVES DICT OF TRACES (key=RUN, value=EACH TRACE)
        ENTER INTO DATA OBJECT
        
    FUNCTION2-REGRESS INSIDE EACH RUN(RUN_SIGNALS : DICT)
        GET LIST OF REGIONS
        GET LIST OF CHANNELS
        FOR CH IN CHANNELS
            FOR REG IN REGIONS(NOT INCLUDING CORRSIG):
                bare array rowxcol (order might be different) trialxtime -> binxtime
                REGRESS CORRSIG_CH FROM REGION_CH
                (1 - BIN TRIALS ACCORDING TO BINSIZE)
                (2 - RUN STANDARD REGRESSION STUFF, including studentization etc etc)
        ABOVE GIVES traces by region by channel (corr_sig is gone)
        FOR REGION:
            FOR CH IN REGION (NOT INCLUDING 0):
                REGRESS REGION_CH0 from REGION_CH_N
                (1 - RUN STANDARD REGRESSION STUFF)
                (2 - UNBIN TRIALS ACCORDING TO BINSIZE)
        ABOVE GIVES 1 trace per region
                
        RETURN NEW REGRESSED SIGNALS FOR THIS RUN
    """

    all_regressed_signals = []
    traces_by_run = data.traces_by_run_signal_trial

    # Iterate through each run in the nested dictionary
    for run_key, run_dict in traces_by_run.items():
        #print(f"Processing run: {run_key}")
        # Assign the nested dictionary (traces within each run) to `traces`
        traces = run_dict

        regressed_signals = regression_func(traces)
        all_regressed_signals.append(regressed_signals)

    data.regressed_signals = all_regressed_signals
    if controller is not None:
        controller.update_data(data)
    return all_regressed_signals

def regression_func(traces):
    #Gathers all information needed to do regression
    region_names = [key.split('_')[1] for key in traces.keys()
                    if key.split('_')[1] != 'corrsig']

    channel_names = [key.split('_')[2] for key in traces.keys()]

    channel_names_ch0_removed = [key.split('_')[2] for key in traces.keys()
                                if key.split('_')[2] != 'ch0']

    # Removes duplicate channel and region names
    unique_channels = unique_list(channel_names)
    unique_regions = unique_list(region_names)
    unique_channels_ch0_removed = unique_list(channel_names_ch0_removed)

    # Initializes blank dictionaries to be filled by regression
    regions_correction_fiber_regressed_b = {}
    regions_correction_fiber_regressed_b_r = {}
    region_residuals_ch0_regressed = {}

    # This first for loop regresses the correction fiber out
    for channel in unique_channels:
        # Assigns the control trace
        control_trace = traces[f'sig_corrsig_{channel}']
        # Transposes the array to have trials as columns instead of rows
        control_trace = np.transpose(control_trace)
        # bins the control trace
        control_trace_b, control_trace_b_r = bin_trials(control_trace, binsize)

        # For each unique region, the correction fiber is regressed out of the binned traces
        for region in unique_regions:
            # Assigns the target trace for regression
            target_trace = traces[f'sig_{region}_{channel}']
            target_trace = np.transpose(target_trace)
            # Bins the target trace by binsize
            # _b = binned & _r = remainder trials
            target_trace_b, target_trace_b_r = bin_trials(target_trace, binsize)
            # This Calculates the studentized residuals which regresses the correction fiber out
            res_studentized_b = studentized_residual_regression(control_trace_b,target_trace_b)
            res_studentized_b_r = studentized_residual_regression(control_trace_b_r, target_trace_b_r)
            # Saves the studentized residuals to a dictionary for further regression
            regions_correction_fiber_regressed_b[f'{region}_{channel}_b'] = res_studentized_b
            regions_correction_fiber_regressed_b_r[f'{region}_{channel}_b_r'] = res_studentized_b_r

    # This for loop regresses ch0 out to output residuals for each region by channel
    for region in unique_regions:
        # Assigns ch0 as the control channel to be regressed out
        control_channel_b = regions_correction_fiber_regressed_b[f'{region}_ch0_b']
        control_channel_b_r = regions_correction_fiber_regressed_b_r[f'{region}_ch0_b_r']

        for channel in unique_channels_ch0_removed:
            # Identifies the target channel for regression
            target_channel_b = regions_correction_fiber_regressed_b[f'{region}_{channel}_b']
            target_channel_b_r = regions_correction_fiber_regressed_b_r[f'{region}_{channel}_b_r']
            # Regresses the control channel from the target channel
            res_studentized_b = studentized_residual_regression(control_channel_b,target_channel_b)
            res_studentized_b_r = studentized_residual_regression(control_channel_b_r, target_channel_b_r)
            # Debins the residuals to create a unified dataset
            debinned_region_residuals = debin_me(res_studentized_b, res_studentized_b_r, binsize)
            # Saves the output residuals into a dictionary
            region_residuals_ch0_regressed[f'{region}_{channel}'] = debinned_region_residuals

    return region_residuals_ch0_regressed

def unique_list(iterable):
    new_list = []
    for obj in iterable:
        if obj not in new_list:
            new_list.append(obj)
    return new_list


def bin_trials(signal, binsize):
    # Take an arbitrary amount of trials and bin them together for less noisy processing
    trial_length = signal.shape[0]
    num_trials = signal.shape[1]

    # Calculates new amount of columns for reshaping the binned data
    num_binned_columns = (num_trials // binsize)
    remainder_columns = (num_trials % binsize)

    # Calculates the number of rows in the reshaped array
    trimmed_signal_length = binsize * num_binned_columns

    # Initializes new arrays to be reshaped
    trimmed_signal = signal[:, :trimmed_signal_length]
    signal_remainder = signal[:, trimmed_signal_length:num_trials]

    # Reshapes the arrays into properly binned data with the remaining trials in a new array
    if binsize == 1:
        # Goofy logic to deal with no binning
        binned_signal = signal
        binned_remainder = signal
    else:
        # This step might be unnecessary but it confirms the arrays are the right size
        binned_signal = trimmed_signal.reshape((binsize * trial_length, num_binned_columns), order='F')
        binned_remainder = signal_remainder.reshape((remainder_columns * trial_length, 1), order='F')

    return binned_signal, binned_remainder


def studentized_residual_regression(X, Y):
    # Does regression and studentization in 1 step because original arrays are needed for studentization
    num_trials = X.shape[1]
    studentized_residuals = np.zeros_like(Y)  # Initialize array to store studentized residuals

    # Loops through all the trials
    for i in range(num_trials):
        # This is here if a trial of all zeros gets through to prevent errors
        if np.all(X[:, i] == X[0, i]):
            studentized_residuals[:, i] = np.zeros(Y[:, i].shape)
        else:
            # This calculates residuals (These residuals 100% Match Matlab residuals)
            slope, intercept, _, _, _ = stats.linregress(X[:, i], Y[:, i])
            predicted_values = slope * X[:, i] + intercept
            residuals = Y[:, i] - predicted_values
            # Below does the steps for studentization
            # Calculate standard error of residuals
            Var_e = np.sqrt(np.sum(residuals ** 2) / (X.shape[0] - 2))
            # Calculate leverage values (h_ii) for studentization
            mean_X = np.mean(X[:, i])
            diff_mean_sqr = np.dot((X[:, i] - mean_X), (X[:, i] - mean_X))
            h_ii = (X[:, i] - mean_X) ** 2 / diff_mean_sqr + (1 / X.shape[0])
            # SE_regression should be equivalent to the bottom of the studentization formula "sqrt(MSE(i)(1−h_ii))"
            SE_regression = Var_e * np.sqrt(1 - h_ii)
            # Calculate studentized residuals
            studentized_residuals[:, i] = residuals / SE_regression

    # Flatten studentized residuals only if 1D (If there is only 1 trial or bin)
    if studentized_residuals.ndim == 1:
        return studentized_residuals.flatten()
    else:
        return studentized_residuals


def debin_me(binned_signal, binned_signal_remainder, binsize):
    # This converts the binned signals back to initial array structure
    # Calculations to get the correct array sizes to ensure proper concatenation
    bin_length = binned_signal.shape[0]
    num_bin_trials = binned_signal.shape[1]
    trial_length = bin_length // binsize
    total_trials = num_bin_trials * binsize
    r_bin_length = binned_signal_remainder.shape[0]
    r_total_trials = r_bin_length // trial_length

    # Combines the remainder array back into the primary array.
    if binsize == 1:
        net_res_debinned = binned_signal
    else:
        # Reshapes the arrays to have equal row lengths equal to the initial trial lengths
        net_res_reshaped = binned_signal.reshape((trial_length, total_trials), order='F')
        net_res_reshaped_r = binned_signal_remainder.reshape((trial_length, r_total_trials), order='F')
        net_res_debinned = np.concatenate([net_res_reshaped, net_res_reshaped_r], axis=1)
    return net_res_debinned

if __name__ == "__main__":
    with open('exampledata.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    binsize = 10
    regression_main(loaded_data)

# if __name__ == "__main__":
    # reg = Regression('MRKPFCREV 28 Run 1.mat')
    # regression_main(loaded_data)
    # Some notes on variable naming
    # ch0 = Purple/Isosbestic and ch1 = Blue/Dependent Color
    # _r = remainder trials binned together
    # _res = Residual
    # _b = Binned
    # _s = Studentized Residual
    # Currently does not deal with multiple signals. Can be easily added
    # corrsig_ch0_binned, corrsig_ch0_binned_r = reg.bin_trials(reg.corrsig_ch0, 5)
    # corrsig_ch1_binned, corrsig_ch1_binned_r = reg.bin_trials(reg.corrsig_ch1, 5)
    # sig1_ch0_binned, sig1_ch0_binned_r = reg.bin_trials(reg.sig1_ch0, 5)
    # sig1_ch1_binned, sig1_ch1_binned_r = reg.bin_trials(reg.sig1_ch1, 5)

    # ch0_res_studentized_b = reg.studentized_residual_regression(corrsig_ch0_binned,
    #                                                             sig1_ch0_binned)  # Signal 1 Purple Residual
    # ch0_res_studentized_b_r = reg.studentized_residual_regression(corrsig_ch0_binned_r, sig1_ch0_binned_r)
    # ch1_res_studentized_b = reg.studentized_residual_regression(corrsig_ch1_binned,
    #                                                             sig1_ch1_binned)  # Signal 1 Blue Residual
    # ch1_res_studentized_b_r = reg.studentized_residual_regression(corrsig_ch1_binned_r, sig1_ch1_binned_r)

    # net_res_b_s = reg.studentized_residual_regression(ch0_res_studentized_b, ch1_res_studentized_b)  # Net Residual
    # net_res_b_s_r = reg.studentized_residual_regression(ch0_res_studentized_b_r, ch1_res_studentized_b_r)

    # net_res_debinned = reg.debin_me(net_res_b_s, net_res_b_s_r, 5)

    # Create a dictionary with variable names and data
    # data_dict = dict(net_res_debinned=net_res_debinned)

    # Save the dictionary to a .mat file
    # scipy.io.savemat('residuals.mat', data_dict)