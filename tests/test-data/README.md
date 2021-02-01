# test data

## minimongodumps/milliquas
- first 10 sources by id
- chosen because this catalog has both geoJSON and healpix indexes (geoJSON queries can't be used with mongomock)
- added extra doc `{"_id": "keys", "ra": "ra", "dec": "dec",}` to meta

## minimongodumps/TNS
- 12 sources reported within 1 degree of 0,0
- chosen because it has no explicit ra/dec fields (just geoJSON index)
- mongodump -o /mnt -d TNS -c srcs --query '{pos: {$geoWithin: {$centerSphere: [[0,0], 0.017453292519943295]}}}'
- mongodump -o /mnt -d TNS -c meta

## catsHTM2/ROSATfsc
- first chunk of 100 cells (754 sources)
- chosen because the index file is small
