$Id: README.txt,v 1.2 2007/02/21 16:11:41 benno Exp $

Copyright (c) 2006, IT Services, ETH Zurich. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:  Silva Photo Gallery 1.1
  Author:     Benno Luthiger, based on the Silva CodeSource on 
              http://www.mat.ethz.ch/silva/silvaphotogallery/SilvaPhotoGallery.zexp
              Modified by Lorenz Textor

Silva Photo Gallery
  
  Silva Photo Gallery is derived from Silva CodeSource. 
  Silva Photo Gallery can be added in the ZMI as ordinary Zope object.
  With an instance of Silva Photo Gallery in the ZODB, you can reference
  it in a Silva Document. When published, this document displays the Silva
  Images contained in the same Silva Folder as photo gallery, i.e. as ordered
  list of thumbnails. You can show the Silva Images enlarged by clicking on 
  the thumbnails and can display the images as slide show.
 
Credits

  The basic idea of this code source comes from Marc Petitmermet/Lorenz Textor.
  SilvaPhotoGallery uses the Lightbox JS javascript (http://lokeshdhakar.com/projects/lightbox2/)
  and the enhanced version Slidebox (http://olivier.ramonat.free.fr/slidebox/). 
  Slidebox again uses the prototype library (http://prototype.conio.net/).
