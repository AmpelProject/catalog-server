# test data

## minimongodumps/milliquas
- first 10 sources by id
- chosen because this catalog has both geoJSON and healpix indexes (geoJSON queries can't be used with mongomock)
- added extra doc `{"_id": "keys", "ra": "ra", "dec": "dec",}` to meta

## catsHTM2/ROSATfsc
- first chunk of 100 cells (754 sources)
- chosen because the index file is small
