from skimage.io import imread

class ADEImage:
    def __init__(self, image, segmap, filename):
      self.img = image
      self.segmap = segmap
      self.filename = filename

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
    def from_filename(cls, filename):
      # TODO: query, import, construct ADEImage

      # view contents of filename (directory for ADEImage)
      # regex to separate photo filepath and segmap filepath(s)
      # import each

      return cls(image, segmap, filename)