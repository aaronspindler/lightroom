import osxphotos


def main():
    pd = osxphotos.PhotosDB(osxphotos.utils.get_last_library_path())

    # Gets a list of photos
    ps = pd.photos()
    photos = ps[:1][0]
    print(photos)
    path = photos.path if photos.israw else photos.path_raw
    print(path)


if __name__ == '__main__':
    main()
