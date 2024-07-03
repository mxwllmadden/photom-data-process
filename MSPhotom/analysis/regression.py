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


def regression_main(data, controller=None):
    #needs to handle multiple signals
    signal = data.traces_by_run_signal_trial
    binsize = data.binsize
    for ch in range(data.num_interpolated_channels):
        # If it is the first signal in the channel, assign it to the correction fiber
        if data.fiber_labels[0]:
            corrsig_binned, corrsig_binned_r = bin_trials(signal, binsize)
        else:
            for i in range(data.fiber_labels):
                binned_signal, binned_signal_r = bin_trials(signal, binsize)
        for ch in range(data.num_interpolated_channels):
            res_studentized_b = studentized_residual_regression(corrsig_binned, binned_signal)
            res_studentized_b_r = studentized_residual_regression(corrsig_binned_r, binned_signal_r)
    for i in len(signal):
        studentized_residual_regression()

    for ch in range(data.num_interpolated_channels):
        studentized_residual_regression(ch0_res_studentized_b, )
        studentized_residual_regression(ch0_res_studentized_b_r, )




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
    reg = Regression('MRKPFCREV 28 Run 1.mat')

    # Some notes on variable naming
    # ch0 = Purple/Isosbestic and ch1 = Blue/Dependent Color
    # _r = remainder trials binned together
    # _res = Residual
    # _b = Binned
    # _s = Studentized Residual
    # Currently does not deal with multiple signals. Can be easily added
    corrsig_ch0_binned, corrsig_ch0_binned_r = reg.bin_trials(reg.corrsig_ch0, 5)
    corrsig_ch1_binned, corrsig_ch1_binned_r = reg.bin_trials(reg.corrsig_ch1, 5)
    sig1_ch0_binned, sig1_ch0_binned_r = reg.bin_trials(reg.sig1_ch0, 5)
    sig1_ch1_binned, sig1_ch1_binned_r = reg.bin_trials(reg.sig1_ch1, 5)

    ch0_res_studentized_b = reg.studentized_residual_regression(corrsig_ch0_binned,
                                                                sig1_ch0_binned)  # Signal 1 Purple Residual
    ch0_res_studentized_b_r = reg.studentized_residual_regression(corrsig_ch0_binned_r, sig1_ch0_binned_r)
    ch1_res_studentized_b = reg.studentized_residual_regression(corrsig_ch1_binned,
                                                                sig1_ch1_binned)  # Signal 1 Blue Residual
    ch1_res_studentized_b_r = reg.studentized_residual_regression(corrsig_ch1_binned_r, sig1_ch1_binned_r)

    net_res_b_s = reg.studentized_residual_regression(ch0_res_studentized_b, ch1_res_studentized_b)  # Net Residual
    net_res_b_s_r = reg.studentized_residual_regression(ch0_res_studentized_b_r, ch1_res_studentized_b_r)

    net_res_debinned = reg.debin_me(net_res_b_s, net_res_b_s_r, 5)

    # Create a dictionary with variable names and data
    data_dict = dict(net_res_debinned=net_res_debinned)

    # Save the dictionary to a .mat file
    scipy.io.savemat('residuals.mat', data_dict)
