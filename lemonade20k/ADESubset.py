from skimage.io import imread

# Corresponding image-segmap-filename entries have the same index in all 3 lists
class ADESubset:
    def __init__(self, images, image_paths, segmaps, segmap_paths, folder_paths,
     whitelisted_folder_paths=None):
      
      self.imgs = images
      self.img_paths = image_paths
      self.segmaps = segmaps
      self.segmap_paths = segmap_paths
      self.folder_paths = folder_paths
      self.whitelisted_folder_paths = whitelisted_folder_paths

    '''  
    This method is NOT used in get_images() because image caching is handled
    better by skimage.io.imread_collection() than by repeated calls to
    skimage.io.imread()

    This method is NOT intended for constructing a large number of ADEImage
    objects, since doing so requires importing a large number of images, and
    images can take up a lot of memory
    --> Use get_images() (from funcs.py) to import a large number of images
    '''
    @classmethod
    def from_filename(cls, filenames):
      # TODO: query, import, construct ADEImage

      # view contents of filename (directory for ADEImage)
      # regex to separate photo filepath and segmap filepath(s)
      # import each

      return cls(images, segmaps, filenames)