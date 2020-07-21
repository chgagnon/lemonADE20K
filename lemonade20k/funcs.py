import numpy as np
from skimage.io import imsave
from . import ADEIndex as ind_class
from . import ADEImage

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
@param phrases - list of 2-tuples, each specifying a real-world object or list of 
                real-world objects to require at least n of from each image 
                in the returned list of ADEImage objects

                The first entry in the tuple must be a string 
                (real-world object name), and the second entry is an integer 
                that indicates the minimum number of occurrences of that object 
                in any image that will be returned
  
                e.g. 

                get_images((['beach', 'house', 'VCR'], 2)) returns all 
                images that have at least 2 instances of a beach OR a house 
                or a VCR

                get_images([(['car'], 1), (['microwave oven'], 3)])
                    --> each image has at least 1 car AND at least 3 
                        microwave ovens

                To collect a subset of the dataset with different integer
                numbers required for objects that involve OR-wise selection,
                make multiple calls to get_images(), like so:

                get_images([[['boots', 'telephone'], 6], [['couch'], 1]])
                    --> each image has at least 6 (boots OR telephone) AND at 
                        least 1 couch

                get_images((['lime'], 11))
                    --> each image has at least 11 limes

                --> concatenating these two results gives images with:
  (at least 6 (boots OR telephone) AND at least 1 couch) OR (at least 11 limes)


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

  img_paths, segmap_paths, folder_paths = get_filepaths(phrases, whitelist)
  imgs = imread_collection(img_paths)
  segmaps = imread_collection(segmap_paths)

  ade_imgs = []


  # TODO:
  # get list of filenames that match
  # iterate over filenames, import images, construct ADEImage objects
    # REMEMBER TO USE ADEImage classmethod to construct objects from filepaths


  if whitelist is None:
    return ade_imgs
  else:

    # take imported segmaps, and knock out everything absent from the whitelist

  return None



'''
Same inputs as get_images(), see above for description
Returns list of complete filepaths to images and
list of complete filepaths to segmentation maps (with corresponding 
indices between image-segmap pairs)

For images that have multiple segmentation map files, get_filepaths() returns
a list of those segmap filepaths for the entry corresponding to that image

(Most useful for preparing a subset of the data to pass to TF, Torch, or some
other graph-based data processing routine with unique image import statements)

Creates directory within [decide where to put this after looking at ADE
directory setup more closely] to store images in with semantic content removed
according to whitelist 
'''
def get_filepaths(phrases, whitelist=None):
  folder_paths = []

  # Allow for a single tuple as input, when the tuple is not enclosed in a list
  if isinstance(phrases, tuple):
    phrases = [phrases]

  # phrase_group is a single string or a list of strings, group_freq is an int
  for (phrase_group, group_freq) in phrases:
    if not isinstance(group_freq, int):
      print('Now skipping the condition specified by' +\
             str((phrase_group, group_freq)) + ' because the frequency\
             of the phrase or phrase group was not an int.')
      continue

    # convert phrase_group to a list (this does NOT handle cases that will cause errors later)
    if isinstance(phrase_group, str):
      phrase_group = [phrase_group]

    object_cols_that_match = []
    for p in phrase_group:
        # get all columns that match to any phrases in the current phrase_group
        object_cols_that_match.append(\
          index.object_image_matrix.loc[:,\
            [string for string in index.object_image_matrix.columns\
              if p in string.split(", ")]])

    group_totals = object_cols_that_match.sum(axis=1)

    image_rows_for_this_group = group_totals.loc[group_totals >= group_freq]
    image_paths_for_this_group = set()
    for ind, row in image_rows_for_this_group.iterrow():
      filepath = index.image_index.loc[ind, 'folder']
      image_paths_for_this_group.add(filepath)

    # Empty lists are false
    if not folder_paths:
      folder_paths.append(image_paths_for_this_group)
    else:
      # Across groups, conditions are joined with AND --> set intersection
      folder_paths = set(folder_paths).intersection(set(image_paths_for_this_group))

  if whitelist is None:
    return None, None, folder_paths
  else:
    # knockout everything absent from whitelist

  # TODO: implement this
  return None, None, folder_paths