# Class Declaration of ADEImage, the main object representing an ADE object.
class ADEImage:
    # TODO: Add the other things that we want to include here
    def __init__(self, image, segmap, filename):
      self.img = image
      self.segmap = segmap
      self.filename = filename

    @classmethod
    def from_filename(cls, filename):
      # TODO: query, import, construct ADEImage

      return cls(image, segmap, filename)