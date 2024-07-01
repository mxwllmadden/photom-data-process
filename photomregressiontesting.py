import tkinter as tk, os, dataclasses, threading, sys
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from dataclasses import dataclass
from MSPhotomAnalysis import *
import scipy.io
from typing import List
import numpy as np
from scipy import stats


class Regression():
    def __init__(self, mat_data):
        self.mat_data = scipy.io.loadmat('MRKPFCREV 28 Run 1.mat')

        self.corrsig_ch0 = np.array(self.mat_data['corrsig_ch0'])
        self.corrsig_ch1 = np.array(self.mat_data['corrsig_ch1'])
        self.sig1_ch0 = np.array(self.mat_data['sig1_ch0'])
        self.sig1_ch1 = np.array(self.mat_data['sig1_ch1'])
        self.sig1_str = np.array(self.mat_data['sig1_str'])
        self.trial_length = self.corrsig_ch0[0]

    def bin_trials(self, signal, binsize):
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
        binned_signal = trimmed_signal.reshape((binsize * trial_length, num_binned_columns), order='F')
        binned_remainder = signal_remainder.reshape((remainder_columns*trial_length, 1), order='F')

        return binned_signal, binned_remainder

    def channel_regression(self, controlresidual, testresidual):
        # Initializes a blank array of the same dimensions of the control residual
        net_residual = np.zeros_like(controlresidual)
        num_trials = controlresidual.shape[1]
        # Perform regression to get residuals
        for i in range(num_trials):
            # If statement to prevent errors in linear regression calculation with all values = 0
            if np.all(controlresidual[:, i] == controlresidual[0, i]):
                net_residual[:, i] = np.zeros(testresidual[:, i].shape)
            else:
                # Actual regression, we only care about the slope and intercept for residual calculations
                slope, intercept, _, _, _ = stats.linregress(controlresidual[:, i], testresidual[:, i])
                net_residual[:, i] = testresidual[:, i] - (slope * controlresidual[:, i] + intercept)
        # Returns the resultant residuals between the control and test inputs
        return net_residual

    def studentize_residuals(self, residuals):
        # Residuals have normal distributions with zero mean but with different
        # variances at different values of the predictors. To place the residuals
        # on a comparable scale, they need to be studentized, which converts them
        # to z-scores

        # Initializes blank array
        studentized_residuals = np.zeros_like(residuals)
        n, m = residuals.shape

        # Loops through every row then column. It deletes the current value to exclude it from z-score calculation
        for j in range(m):
            for i in range(n):
                # Maybe need to include residual value in studentization mean calculation but not std
                temp_residuals = np.delete(residuals[:, j], i, axis=0)
                std_residuals = np.std(temp_residuals, axis=0, ddof=1)
                # This if statement exists for if there is an entire column of the same value
                # It would cause an error because the calculation would try to divide by 0
                if std_residuals == 0:
                    studentized_residuals[i, j] = 0
                else:
                    studentized_residuals[i, j] = (residuals[i, j] / std_residuals)

        return studentized_residuals

    def the_debininator(self, binned_signal, binned_signal_remainder, binsize):
        # This converts the binned signals back to initial array structure
        # Calculations to get the correct array sizes to ensure proper concatenation
        bin_length = binned_signal.shape[0]
        num_bintrials = binned_signal.shape[1]
        trial_length = bin_length // binsize
        total_trials = num_bintrials * binsize
        r_bin_length = binned_signal_remainder.shape[0]
        r_total_trials = r_bin_length // trial_length

        # Reshapes the arrays to have equal row lengths equal to the initial trial lengths
        net_res_reshaped = binned_signal.reshape((trial_length, total_trials), order='F')
        net_res_reshaped_r = binned_signal_remainder.reshape((trial_length, r_total_trials), order='F')
        # Combines the remainder array back into the primary array.
        net_res_debinned = np.concatenate([net_res_reshaped, net_res_reshaped_r], axis=1)
        return net_res_debinned

if __name__ == "__main__":
    reg = Regression('MRKPFCREV 28 Run 1.mat')

    corrsig_ch0_binned, corrsig_ch0_binned_r = reg.bin_trials(reg.corrsig_ch0, 10)
    corrsig_ch1_binned, corrsig_ch1_binned_r = reg.bin_trials(reg.corrsig_ch1, 10)
    sig1_ch0_binned, sig1_ch0_binned_r = reg.bin_trials(reg.sig1_ch0, 10)
    sig1_ch1_binned, sig1_ch1_binned_r = reg.bin_trials(reg.sig1_ch1, 10)

    ch0_res_binned = reg.channel_regression(corrsig_ch0_binned, sig1_ch0_binned)
    ch0_res_binned_r = reg.channel_regression(corrsig_ch0_binned_r, sig1_ch0_binned_r)
    ch1_res_binned = reg.channel_regression(corrsig_ch1_binned, sig1_ch1_binned)
    ch1_res_binned_r = reg.channel_regression(corrsig_ch1_binned_r, sig1_ch1_binned_r)

    ch0_res_studentized_b = reg.studentize_residuals(ch0_res_binned)
    ch0_res_studentized_b_r = reg.studentize_residuals(ch0_res_binned_r)
    ch1_res_studentized_b = reg.studentize_residuals(ch1_res_binned)
    ch1_res_studentized_b_r = reg.studentize_residuals(ch1_res_binned_r)

    net_res_b = reg.channel_regression(ch0_res_studentized_b, ch1_res_studentized_b)
    net_res_b_r = reg.channel_regression(ch0_res_studentized_b_r, ch1_res_studentized_b_r)

    net_res_b_s = reg.studentize_residuals(net_res_b)
    net_res_b_s_r = reg.studentize_residuals(net_res_b_r)

    net_res_debinned = reg.the_debininator(net_res_b_s, net_res_b_s_r, 10)

    # Create a dictionary with variable names and data
    data_dict = dict(net_res_b_s=net_res_b_s, net_res_b_s_r=net_res_b_s_r, net_res_debinned = net_res_debinned)

    # Save the dictionary to a .mat file
    scipy.io.savemat('residuals.mat', data_dict)
