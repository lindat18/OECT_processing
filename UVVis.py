# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 13:36:20 2018

@author: Raj
"""

import numpy as np
import pandas as pd
import os
import re

from matplotlib import pyplot as plt

'''
UV Vis spec-echem processing

Usage:
    
    >> steps, specs, potentials = UVVis.read_files(path_to_folder)
    >> data = UVVis.uv_vis(steps,specs,potentials)
    >> data.spec_echem_voltage() # spectra at each voltage in one dataFrame
    >> data.single_wl_time(0.8, 800) # wavelength vs time at a given bias

'''
def read_files(path):
    '''
    Takes a folder and finds the potential from all the "Steps" files
    NOTE: rename "steps" and "Stepspectra" to "steps(0)" and "stepspectra(0)", respectively
        
    Input
    -----
    path : str
        Folder path to where the data are contained. Assumes are saved as "steps"
    
    Returns
    -------
    stepfiles : list of strings
        For the "steps" (current)
    specfiles : list of string
        For the list of spectra files
    potentials : ndarray
        Numpy array of the potentials in filelist order
    '''
    
    
    filelist = os.listdir(path)
    stepfiles = [os.path.join(path, name)
                 for name in filelist if (name[-3:] == 'txt' and 'spectra' not in name)]
    specfiles = [os.path.join(path, name)
                 for name in filelist if (name[-3:] == 'txt' and 'spectra' in name)]
    
    ''' Need to "human sort" the filenames '''
    # https://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
    def natural_sort(l): 
        convert = lambda text: int(text) if text.isdigit() else text.lower() 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(l, key = alphanum_key)

    specfiles = natural_sort(specfiles)
    stepfiles = natural_sort(stepfiles)
    
    potentials = np.zeros([len(stepfiles)])

    pp = pd.read_csv(stepfiles[0], header=0, sep='\t')
    pot = [n for n in pp.columns if 'Potential' in n][0]

    for fl, x in zip(stepfiles, np.arange(len(potentials))):
    
        pp = pd.read_csv(fl, header=0, sep='\t')
        potentials[x] = np.round(pp[pot][0],2)
        
    return stepfiles, specfiles, potentials


class uv_vis(object):
    
    def __init__(self, steps, specs, potentials):
        '''
        steps : list
            List of step(current) files
            
        specs : list
            List of spectra files
            
        potentials : list
            List of voltages applied
            
        Class contains:
        --------------
        self.steps
        self.specs
        self.potentials
        self.spectra : pandas Dataframe
            The spectra at each voltage in a large dataframe
        self.vt : pandas Series
            The voltage spectra at a particular wavelength (for threshold measurement)
        self.time_spectra : pandas Series
            Normalized Time spectra at a given wavelength and potential over time
        self.time_spectra_raw : pandas Series
            Time spectra at a given wavelength and potential over time
        '''
        self.steps = steps
        self.specs = specs
        self.potentials = potentials
        
        self.wavelength = 800
        
        return
    
    def spec_echem_voltage(self, wavelength=800, which_run=-1):
        '''
        Takes the list of spectra files specfiles, then extracts the final spectra
        from each file and returns as a single dataframe
        
        Also extracts the absorbance vs voltage at a particular wavelength
        
        specfiles : list of str
            Contains paths to the specfiles
            
        potentials : list
            Contains correlated list of Gate voltages
            
        wavelength : int
            wavelength to extract voltage-dependent data on
            
        which_run : int, optional
            Which run to select and save. By default is the last (the final time slice)
            
        Returns
        -------
        df : pandas Dataframe
        
        vt: pandas Dataframe
            voltage at each bias
        
        '''  
        pp = pd.read_csv(self.specs[0], sep='\t')
        
        runs = np.unique(pp['Spectrum number'])
        per_run = int(len(pp)/runs[-1])
    #    last_run = runs[-1]
        wl = pp['Wavelength (nm)'][0:per_run]
        
        # Set up dataframe
        df = pd.DataFrame(index=wl)
        vt = []
    
        for fl,v in zip(self.specs, self.potentials):
            
            pp = pd.read_csv(fl, sep='\t')
            data = pp[pp['Spectrum number']==runs[which_run]]['Absorbance'].values
            df[v] = pd.Series(data, index=df.index)
    
        idx = df[v].index
        wl = idx.searchsorted(wavelength)
        vt = df.loc[idx[wl]]
        
        self._single_wl_voltage(wavelength)
        self.spectra = df
        
        return df, vt
    
    def _single_wl_voltage(self, wavelength=800):
        '''
        Extracts the absorbance vs voltage at a particular wavelength
        '''
        
        idx = self.df[v].index
        wl = idx.searchsorted(wavelength)
        self.vt = self.df.loc[idx[wl]]
        
        return 
    
    def _single_time_spectra(self,spectra_path):
        '''
        Plots the time-dependent spectra for a single dataframe
        
        spectra_path : str
            Path to a specific spectra file
        '''
        
        pp = pd.read_csv(spectra_path, sep='\t')
        
        runs = np.unique(pp['Spectrum number'])
        times = np.unique(pp['Time (s)'])
        times = times - times[0]
        per_run = int(len(pp)/runs[-1])
        wl = pp['Wavelength (nm)'][0:per_run]
        
        # Set up dataframe
        df = pd.DataFrame(index=wl)
        
        for k, t in zip(runs, times):
            
            data = pp[pp['Spectrum number']==k]['Absorbance'].values
            df[np.round(t,2)] = pd.Series(data, index=df.index)
        
        return df
    
    def single_wl_time(self, potential=0, wavelength=800):
        '''
        Extracts the time-dependent data from a single wavelength
        
        potential : float
            Find run corresponding to potential
            
        wavelength : int, float
            Wavelength to extract. This will search for nearest wavelength row
            
        Returns
        -------
        dfraw : Series
            Pandas Series of the time-series at that wavelength
        dfnorm : Series
            Normalzied data from 0 to 1
        
        '''
        spectra_path = self.specs[self.volt(potential)]
        df = self._single_time_spectra(spectra_path)
        
        idx = df.index
        wl = idx.searchsorted(wavelength)
        
        data = df.loc[idx[wl]] - np.min(df.loc[idx[wl]])
        data =  data / np.max(data)
       
        self.time_spectra = df.loc[idx[wl]]
        self.time_spectra_raw = pd.Series(data.values, index=df.loc[idx[wl]].index)
    
        return self.time_spectra, self.time_spectra_raw
    
    def volt(self,bias):
        '''
        returns voltage from potential list
        
        '''
        out = np.searchsorted(self.potentials, bias)
        
        return out
    
def plot_time(uv, ax=None):
    
    if ax == None:
        fig, ax = plt.subplots(nrows=1, figsize=(12, 6))
    uv.time_spectra.plot(ax=ax)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Normalize absorbance (a.u.)')
    
    return ax

def plot_spectra(uv, ax=None):
    
    if ax == None:
        fig, ax = plt.subplots(nrows=1, figsize=(12, 6))
        
    uv.spectra.plot(ax=ax)
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Absorbance (a.u.)')
    
    return ax

def plot_voltage(uv, ax=None):
    
    if ax == None:
        fig, ax = plt.subplots(nrows=1, figsize=(12, 6))
    
    ax.plot(uv.potentials*-1, uv.vt.values)
    ax.set_xlabel('Gate Bias (V)')
    ax.set_ylabel('Absorbance (a.u.)')
    
    return ax