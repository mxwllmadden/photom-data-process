# -*- coding: utf-8 -*-
"""
Perform Studentized Residual Regression from organized trace data
"""

from typing import Dict, Type
import numpy as np
from scipy import stats
import pickle
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
import pandas as pd
from MSPhotom.data import MSPData
from MSPhotom.analysis.testing_regression import FakeMSPData

"""
TODO - 7/9/24 - MM

1- Docstrings for all functions

2- unit tests for all functions

3- Mockup VIEW (gui)

4- Integrate VIEW with CONTROLLER and allow main function (regression_main)
to interact/alter view for progressbar or similar.

TODO - 7/16/24 - MM

Go through notes below and clean/alter accordingly.

Be EXPLICIT with data. Use np.NaN when no value is produced. When there is no remainder
when binning, use None or similar (or at least an explicit exclusion/handling of the empty array).
Check inputs and outputs of functions (binsize, etc)

Remember that you need to have code that will work with NaN input (remove/mask prior to regression calculation)


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
    all_regressed_signals = [] #TODO: RENAME TO LIST OR BETTER, USE DICTIONARY -MM 7.16.24
    all_corrsig_graph_dictionary = []
    all_ch0_graph_dictionary = []
    traces_by_run = data.traces_by_run_signal_trial

    # Iterate through each run in the nested dictionary
    for run_key, run_dict in traces_by_run.items():
        # print(f"Processing run: {run_key}")
        # Assign the nested dictionary (traces within each run) to `traces`
        traces = run_dict

        regressed_signals = regression_func(traces)  # CHANGE THIS TO dict_run_signal
        all_regressed_signals.append(regressed_signals)
        # all_corrsig_graph_dictionary.append(corrsig_graph_dictionary)
        # all_ch0_graph_dictionary.append(ch0_graph_dictionary)

    data.regressed_signals = all_regressed_signals
    if controller is not None:
        controller.update_data(data)
    return all_regressed_signals


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
        control_trace_b, control_trace_b_r = bin_trials(control_trace, binsize) # TODO: binsize is undefined -MM 7.16.24

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
            res_studentized_b = calculate_studentized_residuals_3(
                control_trace_b, target_trace_b)
            res_studentized_b_r = calculate_studentized_residuals_3(
                control_trace_b_r, target_trace_b_r)
            # debinned_reg_residuals = debin_me(corrsig_x_values, corrsig_x_values_r, binsize)
            # debinned_line_bestfit = debin_me(corrsig_y_values, corrsig_y_values_r, binsize)

            # corrsig_graph_dictionary[f'{region}_{channel}_residuals'] = debinned_reg_residuals
            # corrsig_graph_dictionary[f'{region}_{channel}_bestfit'] = debinned_line_bestfit

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
            res_studentized_b = calculate_studentized_residuals_3(
                control_channel_b, target_channel_b)
            res_studentized_b_r = calculate_studentized_residuals_3(
                control_channel_b_r, target_channel_b_r)
            # Debins the residuals to create a unified dataset
            debinned_region_residuals = debin_me(res_studentized_b, res_studentized_b_r, binsize)


            # ch0_graph_dictionary[f'{region}_{channel}_residuals'] = debinned_reg_residuals2
            # ch0_graph_dictionary[f'{region}_{channel}_bestfit'] = debinned_line_bestfit2

            # Saves the output residuals into a dictionary
            region_residuals_ch0_regressed[f'{region}_{channel}'] = debinned_region_residuals

    return region_residuals_ch0_regressed


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


def bin_trials(signal : np.ndarray, binsize):
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
    signal_remainder = signal[:, trimmed_signal_length:]

    # Reshapes the arrays into properly binned data with the remaining trials in a new array
    if remainder_columns == 0:
        binned_signal = trimmed_signal.reshape(
            (binsize * trial_length, num_binned_columns), order='F')
        return binned_signal, None

    # This step might be unnecessary but it confirms the arrays are the right size
    binned_signal = trimmed_signal.reshape(
        (binsize * trial_length, num_binned_columns), order='F')
    binned_remainder = signal_remainder.reshape(
        (remainder_columns * trial_length, 1), order='F')
    return binned_signal, binned_remainder


def calculate_studentized_residuals(X, Y):
    # This logic is here to quickly exit the function if their is no binned remainder
    try:
        num_trials = X.shape[1]
    except AttributeError:
        return None
    studentized_residuals = np.full(Y.shape, np.nan, dtype=np.float64)

    for i in range(num_trials):
        try:
            valid_mask = ~np.isnan(X[:, i]) & ~np.isnan(Y[:, i])
            X_valid = X[valid_mask, i]
            Y_valid = Y[valid_mask, i]

            if len(X_valid) < 2 or len(Y_valid) < 2:
                continue

            # Converting to a dataframe for `ols` usage
            data = {'X': X_valid, 'Y': Y_valid}
            dataframeinternal = pd.DataFrame(data)
            # print(dataframeinternal)
            # Building simple linear regression model
            model = ols('Y ~ X', data=dataframeinternal).fit()
            # print(model.summary())
            # Producing studentized residuals
            outlier_test_result = model.outlier_test()
            # print(outlier_test_result)
            studentized_residuals[valid_mask, i] = outlier_test_result['student_resid']
        except (ValueError, np.linalg.LinAlgError):
            pass

    return studentized_residuals.flatten() if studentized_residuals.ndim == 1 else studentized_residuals

def calculate_studentized_residuals_2(X, Y):
    # This logic is here to quickly exit the function if their is no binned remainder
    try:
        num_trials = X.shape[1]
    except AttributeError:
        return None
    studentized_residuals = np.full(Y.shape, np.nan, dtype=np.float64)
    internally_studentized_residuals= np.full(Y.shape, np.nan, dtype=np.float64)
    for i in range(num_trials):
        mean_X = np.nanmean(X[:, i])
        mean_Y = np.nanmean(Y[:, i])
        n = len(X)
        diff_mean_sqr = np.dot((X[:, i] - mean_X), (X[:, i] - mean_X))
        beta1 = np.dot((X[:, i] - mean_X), (Y[:, i] - mean_Y)) / diff_mean_sqr
        beta0 = mean_Y - beta1 * mean_X
        y_hat = beta0 + beta1 * X[:, i]
        residuals = Y[:, i] - y_hat
        h_ii = (X[:, i] - mean_X) ** 2 / diff_mean_sqr + (1 / n)
        Var_e = np.sqrt(sum((Y[:, i] - y_hat) ** 2) / (n - 2))
        SE_regression = Var_e * ((1 - h_ii) ** 0.5)
        internally_studentized_residuals[:, i] = residuals / SE_regression
        r = internally_studentized_residuals[:, i]
        n = len(r)
        studentized_residuals[:, i] = [r_i * np.sqrt((n - 2 - 1) / (n - 2 - r_i ** 2)) for r_i in r]

    return studentized_residuals.flatten() if studentized_residuals.ndim == 1 else studentized_residuals

def calculate_studentized_residuals_3(X, Y):
    # This logic is here to quickly exit the function if their is no binned remainder
    try:
        num_trials = X.shape[1]
    except AttributeError:
        return None
    studentized_residuals = np.full(Y.shape, np.nan, dtype=np.float64)
    internally_studentized_residuals= np.full(Y.shape, np.nan, dtype=np.float64)
    for i in range(num_trials):
        mean_X = np.nanmean(X[:, i])
        mean_Y = np.nanmean(Y[:, i])
        n = len(X)
        diff_mean_sqr = np.dot((X[:, i] - mean_X), (X[:, i] - mean_X))
        beta1 = np.dot((X[:, i] - mean_X), (Y[:, i] - mean_Y)) / diff_mean_sqr
        beta0 = mean_Y - beta1 * mean_X
        y_hat = beta0 + beta1 * X[:, i]
        residuals = Y[:, i] - y_hat
        h_ii = (X[:, i] - mean_X) ** 2 / diff_mean_sqr + (1 / n)
        MSE = sum((Y[:, i] - y_hat) ** 2) / (n-2)
        SE_regression = ((MSE * (1 - h_ii)) ** 0.5)
        internally_studentized_residuals[:, i] = residuals / SE_regression
        r = internally_studentized_residuals[:, i]
        n = len(r)
        studentized_residuals[:, i] = [r_i * np.sqrt((n - 2 - 1) / (n - 2 - r_i ** 2)) for r_i in r]

    return studentized_residuals.flatten() if studentized_residuals.ndim == 1 else studentized_residuals


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

    # Combines the remainder array back into the primary array.

    # Reshapes the arrays to have equal row lengths equal to the initial trial lengths
    net_res_reshaped = binned_signal.reshape(
        (trial_length, total_trials), order='F')
    if binned_signal_remainder == None:
        return net_res_reshaped

    r_bin_length = binned_signal_remainder.shape[0]
    r_total_trials = r_bin_length // trial_length

    net_res_reshaped_r = binned_signal_remainder.reshape(
        (trial_length, r_total_trials), order='F')
    net_res_debinned = np.concatenate(
        [net_res_reshaped, net_res_reshaped_r], axis=1)
    return net_res_debinned


def plot_line_and_residuals(X, Y, predicted_values, label):

    plt.figure(figsize=(10, 6))
    plt.plot(X, Y, 'o', label=f"{label} Data")
    plt.plot(X, predicted_values, 'r', label=f"{label} Line of Best Fit")
    # for i in range(len(X)):
    #    plt.plot([X[i], X[i]], [Y[i], predicted_values[i]], 'k--')

    plt.legend()
    plt.title(f"{label} Residuals Plot")
    plt.xlabel('Traces')
    plt.ylabel('Studentized Residual Distance(Z-Scores)')
    plt.show()


# def plot_corrsigres(corrsig_graph_dictionary, g_region, g_channel, g_trial):
#     residuals_key = f'{g_region}_{g_channel}_residuals'
#     bestfit_key = f'{g_region}_{g_channel}_bestfit'
#
#     residuals = corrsig_graph_dictionary[residuals_key][:, g_trial]
#     bestfit = corrsig_graph_dictionary[bestfit_key][:, g_trial]
#
#     X = np.arange(len(residuals))
#     Y = residuals + bestfit  # Recreate the original data points
#
#     plot_line_and_residuals(X, Y, bestfit, label="Corrsig")
#
#
# def plot_ch0res(ch0_graph_dictionary, g_region, g_channel, g_trial):
#     residuals_key = f'{g_region}_{g_channel}_residuals'
#     bestfit_key = f'{g_region}_{g_channel}_bestfit'
#
#     residuals = ch0_graph_dictionary[residuals_key][:, g_trial]
#     bestfit = ch0_graph_dictionary[bestfit_key][:, g_trial]
#
#     X = np.arange(len(residuals))
#     Y = residuals + bestfit  # Recreate the original data points
#
#     plot_line_and_residuals(X, Y, bestfit, label="Channel 0")
def save_list_to_csv(data_list, prefix):
    for idx, run_data in enumerate(data_list):
        for signal_name, signal_data in run_data.items():
            # Convert numpy array to pandas DataFrame
            df = pd.DataFrame(signal_data)
            # Define the CSV filename
            csv_filename = f"{prefix}_run{idx+1}_{signal_name}.csv"
            # Save to CSV
            df.to_csv(csv_filename, index=False)
            print(f"Saved {signal_name} to {csv_filename}")


if __name__ == "__main__":
    with open('fake_data_with_peaks.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    print(loaded_data.traces_by_run_signal_trial.keys())

    binsize = 1
    all_regressed_signals = regression_main(loaded_data)

    save_list_to_csv(all_regressed_signals, 'regressed3')


