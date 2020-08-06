import numpy as np
import pandas as pd
import glob
from os.path import join
import sys
from skimage.io import imsave, imread_collection, imread
from . import ADEIndex as ind_class
from . import ADESubset
from .exceptions import QueryPhrasesFormatError

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
Sets all semantic regions of a segmap that are NOT listed on objects whitelist
to 0 (the value that indicates "unknown" content)

Renumbers remaining semantic content with pixel codes from 1 to n, where n 
is the number of distinct objects in the whitelist

Saves segmaps to ADE20K_2016_07_26/whitlelisted/folder_path/segmap

@return - 2-tuple: (path to the new segmap, path to folder containing new segmap)
'''
def _knockout_segmap(initial_segmap, folder_path, whitelist):
    
    r = initial_segmap[:,:,0]
    g = initial_segmap[:,:,1]

    r = r.astype(np.uint16)
    g = g.astype(np.uint16)

    object_map =  np.floor((r / 10)) * 256 + g
    whether_values_are_zero = object_map == 0
    # to fix MATLAB indexing
    object_map[whether_values_are_zero] = 1

    # get unique image labels in the decoded segmap (list of contained objects)
    unique_obj_codes = np.unique(object_map)
    # if object is not in our list of approved objects, then set all pixels of this object to 0
    num_approved_words_in_img = 0
    for code in unique_obj_codes:
        # the MATLAB indexing fix described above /should/ prevent this from being a key error
        img_object_name = index.object_name_list['objectnames'].loc[code - 1]

        approved_code = False
        # Checking if current object is on our list of approved words
        for word_index, word in enumerate(whitelist):
            # This "in" is checking list containment (img_object_name.split(", ")) is a list of strings
            if word in img_object_name.split(", "):
                # This objectname matches the current whitelist word
                num_approved_words_in_img += 1
                parts_of_object_map_with_this_object = object_map == code
                object_map[parts_of_object_map_with_this_object] = num_approved_words_in_img
                approved_code = True
                break

        if approved_code:
            # print(img_object_name + " is approved")
            pass
        else:
            # Current code is not on the whitelist
            parts_of_object_map_with_this_object = object_map == code
            object_map[parts_of_object_map_with_this_object] = 0

    # Now, object_map has nonzero pixel values only for objects that we care about
    object_map = object_map.astype(np.float64)

    npy_segmap = np.array(object_map)

    # Normalize segmap values from 0 to 255

    npy_segmap *= 255.0/npy_segmap.max()

    generic_filename, ext = os.path.splitext(filename)

    if whether_training:
        f = os.path.join(train_dir, filename)
        npy_path = os.path.join(train_dir,generic_filename)
        #print("Resized segmap is ", resized_segmap)
        #print("Shape is ", resized_segmap.shape)
        imsave(f, resized_segmap)
        #print("Saving training segmap " + f)
    else:
        f = os.path.join(test_dir, filename)
        npy_path = os.path.join(test_dir,generic_filename)
        imsave(f, resized_segmap)
        #print("Saving testing segmap " + f)

'''
# Getting Images

Functions that query the dataset and return ADESubset objects,
which store real images and the corresponding segmentation maps,
imported as Numpy arrays.
'''

'''
@param phrases - list of 2-tuples, each specifying a real-world object or list of 
                real-world objects to require at least n of from each image 
                in the returned ADESubset object

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

@param withParts - boolean

                  If True, an image's "parts" segmaps (used to indicate
                  z-axis occlusion) will be returned from get_filepaths()
                  and imported into a list of segmaps for the corresponding
                  image

get_images returns an ADESubset object that contains images that:
  
  # Include objects specified by phrase

  - contain at least 1 instance of an object name that contains the input phrase.
    (Some object "names" are lists of synonyms --> phrase matches to an object
     as long as phrase is contained in that object's list of synonyms)

  # Exclude objects specified by whitelist

  - to use a subset of the objects identified in the dataset, regions of the
    segmentation maps that contain unwanted objects are set to value 0, which
    indicates "unknown" semantic content

'''
def get_images(phrases, whitelist=None, withParts=False):

  # TODO:
  # get list of filenames that match
  # iterate over filenames, import images, construct ADESubset object
    # REMEMBER TO USE ADEImage classmethod to construct objects from filepaths
    # ^^ NO don't do that because imread_collection handles caching across many images better

  if whitelist is None:
    img_paths, segmap_paths, folder_paths = get_filepaths(phrases, whitelist, withParts)
    imgs = imread_collection(img_paths)
    # This could be a problem: segmaps has sublists for images with _parts_* maps
    # --> MAKE SURE TO TEST FOR THIS
    segmaps = imread_collection(segmap_paths)

    return ADESubset(imgs, img_paths, segmaps, segmap_paths, folder_paths)
  else:
    whitelisted_folder_paths = []
    for i, folder in enumerate(folder_paths):
      new_segmap_path, whitelisted_folder_path = _knockout_segmap(segmaps[i], folder, whitelist)
      segmaps[i] = imread(new_segmap_path)
      segmap_paths[i] = new_segmap_path
      whitelisted_folder_paths.append(whitelisted_folder_path)

    return ADESubset(imgs, img_paths, segmaps, segmap_paths, folder_paths, whitelisted_folder_paths)


'''
Same inputs as get_images(), see above for description

Returns list of complete filepaths to images,
list of complete filepaths to segmentation maps (with corresponding 
indices between image-segmap pairs),
and list of filepaths to folders

Images and segmentation maps occur only once, but if two distinct images
occur in the same folder in the dataset, that folder will occur multiple times
in the list of folder paths (so that corresponding indices can be used
between the three returned lists)

For images that have multiple segmentation map files, get_filepaths() returns
a list of those segmap filepaths for the entry corresponding to that image

(Most useful for preparing a subset of the data to pass to TF, Torch, or some
other graph-based data processing routine with unique image import statements)

If whitelist is defined:
  Creates ADE20K_2016_07_26/whitlelisted/folder_path/segmap within 
  ADE20K_2016_07_26/, which contains images in with semantic content is removed
  according to whitelist 

  Returns an additional (fourth) parameter: whitelisted_folder_paths

  The ith entry of whitelisted_folder_paths is the path to the folder within
  ADE20K_2016_07_26/whitlelisted/ that contains the ith entry of image_paths
'''
def get_filepaths(phrases, whitelist=None, withParts=False):
  image_paths = []
  segmap_paths = []
  folder_paths = []

  # Allow for a single tuple as input, when the tuple is not enclosed in a list
  if isinstance(phrases, tuple):
    print('Converting input tuple to 1-elem list of a single tuple')
    phrases = [phrases]

  if not isinstance(phrases, list):
    print('Input to get_filepaths is not a valid list of tuples.')
    message = "Query phrases must be lists of tuples of the form " +\
              "described in the documentation. Instead, the input phrases had" +\
              " type " + str(type(phrases))
    raise QueryPhrasesFormatError(message)

  print('Phrases is: ', phrases)
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

    object_cols_that_match = pd.DataFrame()
    for p in phrase_group:
      # get all columns that match to any phrases in the current phrase_group
      cols_to_add = index.object_image_matrix.loc[:,\
                    [string for string in index.object_image_matrix.columns\
                      if p in string.split(", ")]]
      print('cols to add is: ', cols_to_add)
      print('p is: ', p)

      object_cols_that_match = pd.concat([object_cols_that_match, cols_to_add], axis=1)

    print('obj cols that match is: ', object_cols_that_match)
    group_totals = object_cols_that_match.sum(axis=1)
    print('group totals is: ', group_totals)

    image_rows_for_this_group = group_totals.loc[group_totals >= group_freq]

    image_paths_for_this_group = []
    folder_paths_for_this_group = []
    for ind, item in image_rows_for_this_group.iteritems():
      imagepath = index.image_index.loc[ind, 'filename']
      folderpath = index.image_index.loc[ind, 'folder']
      # if imagepath == 'ADE_train_00002222.jpg':
      #   print(folderpath)
      #   return
      
      image_paths_for_this_group.append(imagepath)
      folder_paths_for_this_group.append(folderpath)

    # print('img paths for this group: ', image_paths_for_this_group, type(image_paths_for_this_group))

    # Empty sets/lists are false
    # if not bool(folder_paths):
    #   folder_paths = set(image_paths_for_this_group)
    # else:
    #   # Across groups, conditions are joined with AND --> set intersection
    #   folder_paths = folder_paths.intersection(set(image_paths_for_this_group))
    if not bool(image_paths):
      image_paths = image_paths_for_this_group
      image_paths_check = set(image_paths_for_this_group)
      folder_paths = folder_paths_for_this_group
    else:
      # Across groups, conditions are joined with AND --> set intersection
      # This is an array of booleans:
      indices_of_matched_imgs = np.isin(image_paths, image_paths_for_this_group)
      # with open("result.txt", "w") as output:
      #   output.write('Existing paths:\n')
      #   for i in image_paths_check:
      #     output.write(i + '\n')

      #   output.write('New group:\n')
      #   for i in image_paths_for_this_group:
      #     output.write(i + '\n')

      #   output.write('Matching indices:\n')
      #   for i in indices_of_matched_imgs:
      #     output.write(str(i) + '\n')
      num_matches = np.sum(indices_of_matched_imgs)
      print('num matches is ', num_matches)
                                                # must cast image_paths to a list for isin to work right
      # Logical indexing:
      print('image paths length is: ', len(image_paths))
      r = input('paused for input (1/4)')
      image_paths = list(np.array(image_paths)[indices_of_matched_imgs])
      print('image paths length is: ', len(image_paths))
      r = input('paused for input (2/4)')

      image_paths_check = image_paths_check.intersection(set(image_paths_for_this_group))
      print(len(image_paths))
      print(len(image_paths_check))
      print(image_paths_check)
      # assert(image_paths == image_paths_check)

      print('folder_paths length is: ', len(folder_paths))
      r = input('paused for input (3/4)')
      folder_paths_arr = np.array(folder_paths)
      print(folder_paths_arr)
      print(folder_paths_arr.shape)
      print(indices_of_matched_imgs.shape)
      for ind, elem in enumerate(indices_of_matched_imgs):
        if elem:
          print(ind)
      folder_paths_matches = folder_paths_arr[indices_of_matched_imgs]
      print(folder_paths_matches)
      folder_paths = list(folder_paths_matches)
      print(folder_paths)

      # folder_paths = list(np.array(list(folder_paths))[indices_of_matched_imgs])
      print('folder_paths length is: ', len(folder_paths), folder_paths)

      r = input('paused for input (4/4)')

      assert(image_paths != folder_paths)
      assert(len(image_paths) == len(folder_paths))

  # Get segmap paths by RegEx-ing on image paths
  for i, path in enumerate(image_paths):
    # Remove .jpg suffix
    image_name = path[:-4]

    seg_matches = glob.glob(join(sys.path[0], folder_paths[i], image_name + '_seg.png'))

    if withParts:
      # Sorting makes _parts_1 occur before _parts_2 in each image list
      parts_matches = sorted(glob.glob(join(sys.path[0], folder_paths[i], image_name + '_parts_*.png')))
      # Extending in this way assures primary segmap is always at index 0 for the given image
      seg_matches.extend(parts_matches)

    segmap_paths.append(seg_matches)

  if whitelist is None:
    print('whitelist is none')
    return image_paths, segmap_paths, folder_paths
  else:
    whitelisted_folder_paths = []
    for i, folder in enumerate(folder_paths):
      new_segmap_path, whitelisted_folder_path = _knockout_segmap(segmaps[i], folder, whitelist)
      segmap_paths[i] = new_segmap_path
      whitelisted_folder_paths.append(whitelisted_folder_path)

    return image_paths, segmap_paths, folder_paths, whitelisted_folder_paths


  # TODO: implement this
  # these paths will be paths to a new dataset directory 
  #  (determine where to place this after looking closely at the default directory)
  return image_paths, segmap_paths, folder_paths

'''
Reports which objects in the dataset will match to an input string passed
to get_filepaths() or get_images()

@param object_lookup_string - a string

@return The list of objects (in the format recorded in the dataset) that would
        match to the input string if the input was one of the lookup strings
        passed to get_filepaths() or get_images()

NOTE: Many objects have multiple, synonymous names in the dataset. As a result,
      this function may return single strings that contain multiple 
      terms, with the terms within the string separated by a comma. Since 
      the dataset treats these words as synonyms, querying the dataset should
      give the same result for any choice from such a list of synonyms.

      DO NOT include multiple synonyms in a single query. This package "splits
      on" commas when dealing with synonyms. Including a comma in a query term
      will likely cause the query to match to ZERO object names.
        
'''
def check_object_matches(object_lookup_string):
  matches = []
  for ind, row in index.object_name_list.iterrows():
      object_col_name = row['objectnames']
      if object_lookup_string in object_col_name.split(", "):
        matches.append(object_col_name)

  # Empty lists are false
  if not matches:
    print(object_lookup_string + " has NO matches to object names in the dataset.")
  else:
    print(object_lookup_string + " matches to THESE " + str(len(matches)) 
          + " object names: ")
    print(matches)