import osxphotos
from PIL import Image
from common.ml import load_model, predict

from common.preprocess import preprocess_img_for_ml_model

def main():
    fingerprints = set()
    photosdb = osxphotos.PhotosDB(osxphotos.utils.get_last_library_path())
    photos = photosdb.query(osxphotos.QueryOptions(not_missing=True, movies=False, photos=True, ))
    photos = photos[:100]
    
    model = load_model()
    
    for photo in photos:
        # fingerprint = photo.fingerprint
        # if fingerprint in fingerprints:
        #     print('Duplicate fingerprint: {}'.format(fingerprint))
        # if fingerprint != None:
        #     fingerprints.add(fingerprint)
        
        if photo.path[-3:] == 'arw':
            continue
        if photo.path[-4:] == 'heic':
            continue
        
        
        image = Image.open(photo.path)
        pp_img_np, pp_img = preprocess_img_for_ml_model(image)
        print(predict(model, pp_img))

if __name__ == '__main__':
    main()
