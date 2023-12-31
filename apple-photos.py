import pathlib
import osxphotos
from PIL import Image
from common.ml import load_model, predict

from common.preprocess import preprocess_img_for_ml_model

def main():
    """
    This script has been shelved since there are limitations from apple on how unregistered applications can access and manipulate the photos library.
    Until this is resolved, this script will not be developed any further.
    """
    
    
    # SETTINGS
    ignore_certain_extensions = True
    # Current Possible Extensions
    # {'.jpeg': 56632, '.arw': 23449, '.dng': 5517, '.heic': 4841, '.png': 2237, '.JPG': 179, '.bmp': 5, '.webp': 1}
    excluded_extensions = ['.arw', '.heic', '.bmp', '.webp']
    
    
    print('Connecting to DB')
    photosdb = osxphotos.PhotosDB(osxphotos.utils.get_last_library_path())
    print('Loading Photos')
    photos = photosdb.query(osxphotos.QueryOptions(not_missing=True, movies=False, photos=True))
    print('Loaded {} photos'.format(len(photos)))
    
    fingerprints = {}

    model = load_model()
    
    for photo in photos:
        path = photo.path
        extension = pathlib.Path(path).suffix
        if extension in excluded_extensions and ignore_certain_extensions:
            continue
        fingerprint = photo.fingerprint
        if fingerprint != None:
            if fingerprint not in fingerprints:
                fingerprints[fingerprint] = []
            fingerprints[fingerprint].append(photo)
    
    print('Creating Album')
    album = osxphotos.PhotosAlbum('Bad Photos')
    print('Created Album')
    bad_photos = []
    # print out fingerprints with more than one photo
    for fingerprint in fingerprints[:1]:
        if len(fingerprints[fingerprint]) > 1:
            print('Fingerprint: {}'.format(fingerprint))
            is_first = True
            for photo in fingerprints[fingerprint]:
                print('  {}'.format(photo.path))
                if is_first:
                    is_first = False
                    continue
                bad_photos.append(photo)
            print()
    
    album.add_list(bad_photos)
        
        
        # image = Image.open(photo.path)
        # pp_img_np, pp_img = preprocess_img_for_ml_model(image)
        # print(predict(model, pp_img))

if __name__ == '__main__':
    main()
