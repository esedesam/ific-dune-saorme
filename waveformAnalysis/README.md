# ific-dune-saorme/waveformAnalysis

To work with the waveforms, we define some preprocessing steps.
The main issue is to number each waveform in the data file so they are easier to manage with.

## WFAnalysis_repo

Repository with several functions defined to read and analize waveforms and gain of the siPMs.

All the codes below have a set-up at the very start: path, data set name, saving options,...
Furthermore, all the codes preprocess the raw data (if needed) as first step.

## WFAnalysis_main

Code to count events, correct the baseline and obtain the charge and gain.

## WFAnalysis_main

Code to plot several waveforms of a set of data.

## WFGainAtRT

Code to analize the gain at room temperature.
A little baseline study is done to analize its effects on the gain value.
Here we need to separate individual peaks in each waveform and integrate them individually to get the charges.

## WFGainAtRT_gaussianMethod

Code to analize the gain at room temperature with the relation of gaussian fits parameters.

Author: Samuel Ortega

Last rev.: 13/06/2023
