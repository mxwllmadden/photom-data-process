# -*- coding: utf-8 -*-
"""
Perform Studentized Residual Regression from organized trace data
"""

from typing import Dict, Type
import numpy as np
from scipy import stats
import pickle
import matplotlib.pyplot as plt

from MSPhotom.data import MSPData

"""
TODO - 7/9/24 - MM

1- Docstrings for all functions

2- unit tests for all functions

3- Mockup VIEW (gui)

4- Integrate VIEW with CONTROLLER and allow main function (regression_main)
to interact/alter view for progressbar or similar.
"""




def regression_main(data: MSPData, controller=None):
    """
    Perform regression on the data traces organized by runs and return regressed signals.

    Args:
        data (MSPData): The data object containing traces organized by runs.
        controller (optional): Controller object to update data if provided.

    Returns:
        list: List of dictionaries containing regressed signals for each run.
    """
    all_regressed_signals = []
    all_corrsig_graph_dictionary = []
    all_ch0_graph_dictionary = []
    traces_by_run = data.traces_by_run_signal_trial

    # Iterate through each run in the nested dictionary
    for run_key, run_dict in traces_by_run.items():
        # print(f"Processing run: {run_key}")
        # Assign the nested dictionary (traces within each run) to `traces`
        traces = run_dict

        regressed_signals, corrsig_graph_dictionary, ch0_graph_dictionary = regression_func(traces)  # CHANGE THIS TO dict_run_signal
        all_regressed_signals.append(regressed_signals)
        all_corrsig_graph_dictionary.append(corrsig_graph_dictionary)
        all_ch0_graph_dictionary.append(ch0_graph_dictionary)

    data.regressed_signals = all_regressed_signals
    if controller is not None:
        controller.update_data(data)
    return all_regressed_signals, all_corrsig_graph_dictionary, all_ch0_graph_dictionary


def regression_func(traces):
    """
       Perform regression analysis on traces to remove correction fibers and channels.

       Args:
           traces (dict): Dictionary of traces keyed by signal names.

       Returns:
           dict: Dictionary containing residuals for each region and channel combination.
    """
    # Gathers all information needed to do regression
    region_names = [key.split('_')[1] for key in traces.keys()
                    if key.split('_')[1] != 'corrsig']

    channel_names = [key.split('_')[2] for key in traces.keys()]

    channel_names_ch0_removed = [key.split('_')[2] for key in traces.keys()
                                 if key.split('_')[2] != 'ch0']

    # Removes duplicate channel and region names
    unique_channels = unique_list(channel_names)
    print(unique_channels)
    unique_regions = unique_list(region_names)
    print(unique_regions)
    unique_channels_ch0_removed = unique_list(channel_names_ch0_removed)

    # Initializes blank dictionaries to be filled by regression
    regions_correction_fiber_regressed_b = {}
    regions_correction_fiber_regressed_b_r = {}
    corrsig_graph_dictionary = {}
    ch0_graph_dictionary = {}
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
            target_trace_b, target_trace_b_r = bin_trials(
                target_trace, binsize)
            # This Calculates the studentized residuals which regresses the correction fiber out
            res_studentized_b, corrsig_residuals_b, corrsig_linebestfit_b = studentized_residual_regression(
                control_trace_b, target_trace_b)
            res_studentized_b_r, corrsig_residuals_b_r, corrsig_linebestfit_b_r = studentized_residual_regression(
                control_trace_b_r, target_trace_b_r)
            debinned_reg_residuals = debin_me(corrsig_residuals_b, corrsig_residuals_b_r, binsize)
            debinned_line_bestfit = debin_me(corrsig_linebestfit_b, corrsig_linebestfit_b_r, binsize)

            corrsig_graph_dictionary[f'{region}_{channel}_residuals'] = debinned_reg_residuals
            corrsig_graph_dictionary[f'{region}_{channel}_bestfit'] = debinned_line_bestfit

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
            res_studentized_b, ch0_residuals_b, ch0_linebestfit_b = studentized_residual_regression(
                control_channel_b, target_channel_b)
            res_studentized_b_r, ch0_residuals_b_r, ch0_linebestfit_b_r = studentized_residual_regression(
                control_channel_b_r, target_channel_b_r)
            # Debins the residuals to create a unified dataset
            debinned_region_residuals = debin_me(res_studentized_b, res_studentized_b_r, binsize)

            debinned_reg_residuals2 = debin_me(ch0_residuals_b, ch0_residuals_b_r, binsize)
            debinned_line_bestfit2 = debin_me(ch0_linebestfit_b, ch0_linebestfit_b_r, binsize)

            ch0_graph_dictionary[f'{region}_{channel}_residuals'] = debinned_reg_residuals2
            ch0_graph_dictionary[f'{region}_{channel}_bestfit'] = debinned_line_bestfit2

            # Saves the output residuals into a dictionary
            region_residuals_ch0_regressed[f'{region}_{channel}'] = debinned_region_residuals

    return region_residuals_ch0_regressed, corrsig_graph_dictionary, ch0_graph_dictionary


def unique_list(iterable):
    """
    Return unique elements from an iterable while preserving order.

    Args:
        iterable (iterable): Iterable object to extract unique elements from.

    Returns:
        list: List of unique elements in the same order as first encountered.
    """
    new_list = []
    for obj in iterable:
        if obj not in new_list:
            new_list.append(obj)
    return new_list


def bin_trials(signal, binsize):
    """
    Bin trials of a signal into groups for noise reduction.

    Args:
        signal (numpy.ndarray): Array of signals where trials are columns.
        binsize (int): Number of trials to bin together.

    Returns:
        tuple: Tuple containing binned signal and remainder trials signal.
    """
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
        binned_signal = trimmed_signal.reshape(
            (binsize * trial_length, num_binned_columns), order='F')
        binned_remainder = signal_remainder.reshape(
            (remainder_columns * trial_length, 1), order='F')

    return binned_signal, binned_remainder


def studentized_residual_regression(X, Y):
    """
    Calculate studentized residuals from regression of X on Y.

    Args:
        X (numpy.ndarray): Independent variable array.
        Y (numpy.ndarray): Dependent variable array.

    Returns:
        numpy.ndarray: Array of studentized residuals.
    """

    # Does regression and studentization in 1 step because original arrays are needed for studentization
    num_trials = X.shape[1]
    # Initialize array to store studentized residuals
    studentized_residuals = np.zeros_like(Y)

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
        return studentized_residuals.flatten(), predicted_values, residuals
    else:
        return studentized_residuals, predicted_values, residuals


def debin_me(binned_signal, binned_signal_remainder, binsize):
    """
    Debin binned signals back to the original structure.

    Args:
        binned_signal (numpy.ndarray): Binned signal array.
        binned_signal_remainder (numpy.ndarray): Remainder of binned signals.
        binsize (int): Number of trials originally binned together.

    Returns:
        numpy.ndarray: Debinarized signal array.
    """
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
        net_res_reshaped = binned_signal.reshape(
            (trial_length, total_trials), order='F')
        net_res_reshaped_r = binned_signal_remainder.reshape(
            (trial_length, r_total_trials), order='F')
        net_res_debinned = np.concatenate(
            [net_res_reshaped, net_res_reshaped_r], axis=1)
    return net_res_debinned

def clear_canvas(canvas):
    for widget in canvas.winfo_children():
        widget.destroy()


def plot_line_and_residuals(X, Y, label):
    slope, intercept, _, _, _ = stats.linregress(X, Y)
    predicted_values = slope * X + intercept
    residuals = Y - predicted_values

    plt.figure(figsize=(10, 6))
    plt.plot(X, Y, 'o', label=f"{label} Data")
    plt.plot(X, predicted_values, 'r', label=f"{label} Line of Best Fit")
    for i in range(len(X)):
        plt.plot([X[i], X[i]], [Y[i], predicted_values[i]], 'k--')

    plt.legend()
    plt.title(f"{label} Residuals Plot")
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()


def plot_corrsigres(data, g_run, g_channel, g_region, g_trial):
    traces = data.traces_by_run_signal_trial[g_run]
    X = np.arange(traces[f'sig_corrsig_{g_channel}'].shape[0])
    Y = traces[f'sig_{g_region}_{g_channel}'][:, g_trial]

    plot_line_and_residuals(X, Y, "Corrsig")


def plot_ch0res(data, g_run, g_channel, g_region, g_trial):
    traces = data.traces_by_run_signal_trial[g_run]
    X = np.arange(traces[f'sig_{g_region}_ch0'].shape[0])
    Y = traces[f'sig_{g_region}_{g_channel}'][:, g_trial]

    plot_line_and_residuals(X, Y, "Channel 0")

if __name__ == "__main__":
    with open('exampledata.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    binsize = 10
    regression_main(loaded_data)
    g_run = 'F://12-07-23/MRKPFCREV 28 Run 1'
    g_channel = 'ch1'
    g_region = 'PTA'
    g_trial = 20

    plot_ch0res(loaded_data, g_run, g_channel, g_region, g_trial)
    plot_corrsigres(loaded_data, g_run, g_channel, g_region, g_trial)



