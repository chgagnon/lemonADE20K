import scipy.io as sio
import numpy as np
import pandas as pd
import sys
import os
import shutil

class ADEIndex:  

  def __init__(self, refreshCSVs=False):

    self.image_index = None
    self.object_name_list = None
    self.object_image_matrix = None
    self._CSVsExist = False

    _csv_folderpath = os.path.join(sys.path[0], 'csvIndexes')

    self.num_images_total = None

    if os.path.exists(_csv_folderpath)\
      and os.path.exists(os.path.join(_csv_folderpath, 'image_index.csv'))\
      and os.path.exists(os.path.join(_csv_folderpath, 'object_name_list.csv'))\
      and os.path.exists(os.path.join(_csv_folderpath,'object_image_matrix.csv')):

      print("Now loading data from CSV files")
      image_index = pd.read_csv(os.path.join(_csv_folderpath, 'image_index.csv'))
      object_name_list = pd.read_csv(os.path.join(_csv_folderpath, 'object_name_list.csv'))
      object_image_matrix = pd.read_csv(os.path.join(_csv_folderpath, 'object_image_matrix.csv'))
      self._CSVsExist = True

      self.num_images_total = image_index.shape[0]

    else:


      _mat_filename = os.path.join(sys.path[0], 'ADE20K_2016_07_26', 'index_ade20k.mat')

      try:
        _mat_contents = sio.loadmat(_mat_filename)
      except FileNotFoundError:
        print("index_ade20k.mat was not found, likely due to a problem during package setup.")
        print('You can resolve this error by manually placing index_ade20k.mat'
         + ' (available from https://groups.csail.mit.edu/vision/datasets/ADE20K/)'
         + ' into ./ADE20K_2016_07_26/')
        return
        # exit()

      print("No CSVs found - will save CSVs after loading MATLAB data")

      _matindex = _mat_contents['index'][0,0]

      # When read with scipy, the MATLAB index does NOT have a consistent row 
      # or column structure.
      # The columns are transposed occasionally because otherwise they don't fit
      # together - they're imported from MATLAB with a bunch of inconsistent 
      # dimensions.
      self.num_images_total = _matindex[_matindex.dtype.names[1]].size

      # putting image attributes in a DataFrame

      _filename_col_nested = pd.DataFrame(matindex['filename'].T, columns=['filename'])
      
      _filename_col = pd.DataFrame(columns=['filename'])

      for index, row in _filename_col_nested.iterrows():
        _filename_col.loc[index] = _filename_col_nested['filename'][index][0]

      _folder_col_nested = pd.DataFrame(_matindex['folder'].T, columns=['folder'])

      _folder_col = pd.DataFrame(columns=['folder'])
      for index, row in _folder_col_nested.iterrows():
        _folder_col.loc[index] = _folder_col_nested['folder'][index][0]

      # I don't know what this column is for (it's not documented on the dataset site)
      _typeset_col = pd.DataFrame(_matindex['typeset'], columns=['typeset'])

      # scene type of each image
      _scene_col = pd.DataFrame(_matindex['scene'].T, columns=['scene'])

      # putting the columns together
      _int_indexed_image_index = pd.concat([_filename_col, _folder_col, _typeset_col, _scene_col], axis=1)

      image_index = _int_indexed_image_index.set_index('filename')
      # Need filename col to be the index AND a query-able column
      # (because conversion to csv makes the index just an int)
      # self.image_index = pd.concat([self.image_index, filename_col], axis=1)

      # print(image_index.index)
      # print(image_index)
      # print(image_index['ADE_train_00011093.jpg'])

      # image_index.to_csv("csvIndexes/image_index.csv")

      # print(image_index['ADE_train_00011093.jpg'])

      # -------

      # Putting object attributes in a DataFrame

      object_name_list_nested = pd.DataFrame(matindex['objectnames'].T, columns=['objectnames'])

      object_name_list = pd.DataFrame(columns=['objectnames'])
      for index, row in object_name_list_nested.iterrows():
        object_name_list.loc[index] = object_name_list_nested['objectnames'][index][0]

      # ----

      # Extracting object frequency matrix (gives number of times each object
      # in the list of objects occurs in each image)
      # We could have gotten this ourselves from the text files in each 
      # image-segmap directory if we wanted, but the parsing format is not fun,
      # so I decided to stick with converting the MATLAB code

      # image filenames are rows, and words (object names) are columns

      object_image_matrix = pd.DataFrame(matindex['objectPresence'].T, 
                                        columns=object_name_list['objectnames'],
                                        index=filename_col['filename'])

      # object_cols_that_match = object_image_matrix.loc[:,[x for x in object_image_matrix.columns if 'vcr' in x]]
      # for (colName, colData) in object_cols_that_match.iteritems():
      #   image_rows_to_add = object_image_matrix.loc[object_image_matrix[colName] != 0]
      #   print(image_rows_to_add)

    print("CSVs exist: ", self.CSVsExist)
    if refreshCSVs or (self.CSVsExist == False):
      if os.path.exists(csv_folderpath):
        shutil.rmtree(csv_folderpath)
      os.mkdir(csv_folderpath)
      print("Now saving CSV files")
      self.save_all_CSVs()
      print("Your CSV files are now toasty and warm")

  # Function to produce all 3 CSV files
  # THE LAST ONE IS KINDA BIG (for a CSV) - around 300 MB
  def save_all_CSVs(self):
    self.image_index.to_csv(os.path.join(_csv_folderpath,"image_index.csv"))
    self.object_name_list.to_csv(os.path.join(_csv_folderpath, 'object_name_list.csv'))
    self.object_image_matrix.to_csv(os.path.join(_csv_folderpath,"object_image_matrix.csv"))