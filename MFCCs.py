#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 09:13:23 2017

@author: DavidVanDusen
"""
import numpy as np
from scipy.fftpack import dct

def mel2freq(melval):
    hzval = 700 * (np.expm1(melval/1127.01028));
    return hzval

def freq2mel(freq):
    melval = 1127.01028 * np.log(1 + (freq/700));
    return melval

def compute_mfccs_frames(frames, fs, hop_size,min_freq,
                  max_freq, num_mel_filts, n_dct):

    win_size = frames.shape[0]
    #Length of spectrogram window
    specLen = int(1+(win_size/2))
    #Sample overlap

    #Take the fft of every frame
    frames = np.fft.fft(frames,win_size,0)
    #Cut them down to size
    frames = np.abs(frames[0:specLen,:])
    
    #Convert to mel
    min_freq = freq2mel(min_freq)
    max_freq = freq2mel(max_freq)
    freqsVec = np.linspace(min_freq,max_freq,num_mel_filts+2)
    freqsVec = mel2freq(freqsVec[:])
    binHop = fs/win_size
    closestBins = np.round(freqsVec[:]/binHop)
    closestBins = closestBins[:]
    print(closestBins)

    melFiltBank = np.zeros([num_mel_filts,(frames.shape[0])])
    for i in range(0,num_mel_filts):
        startIndex = int(closestBins[i])
        midIndex = int(closestBins[i+1])
        endIndex = int(closestBins[i+2])
        melFiltBank[i,startIndex:midIndex+1] = np.linspace(0,1, midIndex-startIndex+1)
        melFiltBank[i,midIndex:endIndex+1] = np.linspace(1,0, endIndex-midIndex+1)
        melFiltBank[i,midIndex] = 1.0
        #normalize filters here
        melFiltBank[i,:] = melFiltBank[i,:]/np.sum(melFiltBank[i,:])
        
    melFiltered = np.matmul(melFiltBank,frames)
    melFiltered = 20*np.log10(melFiltered,where=True)
    melFiltered = dct(melFiltered,2,40,0)
    melFiltered = melFiltered[1:n_dct,:]
    melFiltered = melFiltered - np.min(melFiltered,axis=0)
    melFiltered = melFiltered/np.sum(melFiltered,axis=0) 
    melFiltered = np.nan_to_num(melFiltered)

    mfcc_fs = hop_size/fs
    
    return melFiltered, mfcc_fs
