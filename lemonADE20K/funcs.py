from . import ADEIndex as ind_class

index = ind_class.ADEIndex()

'''
Delete and remake CSV indexes for the dataset
'''
def refresh_csv_tables():
  index = ind_class.ADEIndex(True)

'''
# Getting Metadata Tables

Getter functions for Pandas columns of particular dataset attributes in the
MATLAB index
'''
def _get_column(df, name):
  return df.loc[:,[name]]

def get_filename_column():
  return _get_column(index.image_index, 'filename')

def get_foldername_column():
  return _get_column(index.image_index, 'folder')

def get_typeset_column():
  return _get_column(index.image_index, 'typeset')

def get_scene_column():
  return _get_column(index.image_index, 'scene')

'''
List distinct objects included in the ADE20K dataset (in entries with multiple
words, all words in the entry are treated as the same object, and all share the
same encoding in the segmentation maps), returned as Pandas column
'''
def get_list_of_object_names():
  return index.object_name_list

'''
Return Pandas DataFrame containing counts of how frequently each object occurs 
in each image. Each (row, column) entry corresponds to an (image, object) pair.
Rows are labeled by image filename.
'''
def get_object_image_matrix():
  return index.object_image_matrix

'''
# Getting Images

Functions that query the dataset and return collections of ADEImage objects,
which store real images and the corresponding segmentation maps,
imported as Numpy arrays.
'''

'''
@param phrases - list of strings (or list of 2-tuples) 
                specifying real-world object or list of real-world objects to
                require at least 1 of from each image in the returned list of
                ADEImage objects

                If phrase is a 2-tuple or list of 2-tuples, the first entry in
                the tuple must be a string (real-world object name), and 
                the second entry is an integer that indicates the minimum number 
                of occurrences of that object in any image that will be returned

@param whitelist - list of strings or None (default)
                    
                   If None, no semantic content is removed from the segmentation
                   maps (equivalent to whitelisting all objects)

get_images returns collection of ADEImage objects that:
  
  # Include objects specified by phrase

  - contain at least 1 instance of an object name that contains the input phrase.
    (Some object "names" are lists of synonyms --> phrase matches to an object
     as long as phrase is contained in that object's list of synonyms)

  # Exclude objects specified by whitelist

  - to use a subset of the objects identified in the dataset, regions of the
    segmentation maps that contain unwanted objects are set to value 0, which
    indicates "unknown" semantic content

'''
def get_images(phrases, whitelist=None):
  ade_imgs = []
  # TODO:
  # get list of filenames that match
  # iterate over filenames, import images, construct ADEImage objects
  return None

# !!!!!!!!!
# TODO:
# add capability to group a set of objects together, and place a minimum number of
# occurrences on objects from that set





'''
Same inputs as get_images(), see above for description
Returns list of complete filepaths to images and
list of complete filepaths to segmentation maps (with corresponding indices
between image-segmap pairs)

(Most useful for preparing a subset of the data to pass to TF, Torch, or some
other graph-based data processing routine with unique image import statements)

Creates directory within [decide where to put this after looking at ADE
directory setup more closely] to store images in with semantic content removed
according to whitelist 
'''
def get_filepaths(phrases, whitelist=None):

  # TODO: implement this
  return None, None
