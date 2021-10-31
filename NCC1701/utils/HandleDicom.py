#!/usr/bin/env python

"""
This module helps to handle DICOM files
Can read individual files or even a complete folder
Also, helps the them to be converted to 2D or even 1D, and also back to 3D

"""

import os
import tkinter as tk
from tkinter import filedialog
import numpy as np
from vtk.util import numpy_support
import vtk
import pydicom
from pydicom.dataset import Dataset, FileDataset

__author__ = "Soumick Chatterjee"
__copyright__ = "Copyright 2018, Soumick Chatterjee & OvGU:ESF:MEMoRIAL"
__credits__ = ["Soumick Chatterjee"]

__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "soumick.chatterjee@ovgu.de"
__status__ = "Finished, but untested"

def ChooseFileNRead(Read3D=True):
    """Choose a DICOM file using file dialog box and read it as an array
    Using: PyDICOM""" 
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if(Read3D):
        return FileRead3D(file_path)
    else:
        return FileRead2D(file_path)

def FileRead3D(file_path):
    """Read a DICOM file (3D) using given file path as an array
    Using: PyDICOM""" 
    dcm = pydicom.dcmread(file_path)
    data = dcm.pixel_array
    if (np.shape(np.shape(data))[0] == 3): #If channel data not present
        data = np.expand_dims(data, 3)
    return data

def FileRead2D(file_path):
    """Read a DICOM file (2D) using given file path as an array
    Using: PyDICOM""" 
    dcm = pydicom.dcmread(file_path)
    data = dcm.pixel_array
    if (np.shape(np.shape(data))[0] == 2): #If channel data not present
        data = np.expand_dims(data, 2)
    return data

def ChooseFolderNRead():
    """Choose a folder using file dialog box and read all the DICOM files (slices of a same image) inside that folder as 3D array
    Using: VTK"""
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return FolderRead(folder_path)

def FolderRead(folder_path):
    """Read DICOM files inside the given folder path, and read them as one 3D array
    Using: VTK"""
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(folder_path)
    reader.Update()
    # Load dimensions using `GetDataExtent`
    _extent = reader.GetDataExtent()
    ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1, 1]
    # Load spacing values
    ConstPixelSpacing = reader.GetPixelSpacing()
    # Get the 'vtkImageData' object from the reader
    imageData = reader.GetOutput()
    # Get the 'vtkPointData' object from the 'vtkImageData' object
    pointData = imageData.GetPointData()
    # Get the `vtkArray` (or whatever derived type) which is needed for the `numpy_support.vtk_to_numpy` function
    arrayData = pointData.GetArray(0)
    # Convert the `vtkArray` to a NumPy array
    ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
    # Reshape the NumPy array to 3D using 'ConstPixelDims' as a 'shape'
    data = ArrayDicom.reshape(ConstPixelDims, order='F')
    if (np.shape(np.shape(data))[0] == 3): #If channel data not present
        data = np.expand_dims(data, 3)
    return data

def ChooseFileNSave(data):
    """Choose a DICOM file using file dialog box to save it
    Using: PyDICOM""" 
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename()
    FileSave(data, file_path)

def FileSave(data, file_path):
    """Save a DICOM file using given file path from an array
    Using: PyDICOM"""
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.1.3.10'
    file_meta.MediaStorageSOPInstanceUID = "1.2.3"
    file_meta.ImplementationClassUID = "1.2.3.4"
    ds = FileDataset(file_path, {}, 
                 file_meta=file_meta, preamble=b"\0" * 128)
    ds.PixelData = data.tobytes()
    ds.save_as(file_path)

def Dicom3Dto2D(Dicom3D):
    """Converts From 3D DICOM to 2D
    Preserves channel info"""
    Dicom2D = Dicom3D.reshape(np.shape(Dicom3D)[0], np.shape(Dicom3D)[1] * np.shape(Dicom3D)[2], np.shape(Dicom3D)[3])
    return Dicom2D

def Dicom2Dto3D(Dicom2D):
    """Converts From 2D DICOM to 3D
    Preserves channel info"""
    Dicom3D = Dicom2D.reshape(np.shape(Dicom2D)[0],np.shape(Dicom2D)[0],int(np.shape(Dicom2D)[1]/np.shape(Dicom2D)[0]), np.shape(Dicom2D)[2])
    return Dicom3D

def Dicom2Dto1D(Dicom2D): 
    """Converts From 2D DICOM to 1D
    No Sperate channel info left. It's now all merged together"""
    Dicom1D = Dicom2D.reshape(np.shape(Dicom2D)[0] * np.shape(Dicom2D)[1] * np.shape(Dicom2D)[2])
    return Dicom1D

def Dicom1Dto2D(Dicom1D, height, n_channel):
    """Converts From 1D DICOM to 2D
    No of Channel introduced seperately"""
    Dicom2D = Dicom1D.reshape(height,int((np.shape(Dicom1D)[0]/height)/n_channel), n_channel)
    return Dicom2D

