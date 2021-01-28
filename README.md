# catalog-server

`catalog-server` exposes [extcats](https://github.com/MatteoGiomi/extcats) and [catsHTM](https://github.com/maayane/catsHTM) catalogs via a REST API.

A [Unit](https://unit.nginx.org)-based container is available at [ampelproject/catalog-server](https://hub.docker.com/r/ampelproject/catalog-server).

## Examples

Cone search for nearest source in a single catalog
```shell
> curl -s -X POST --header "Content-Type: application/json" http://localhost:8500/cone_search/nearest --data '{"ra_deg": 0, "dec_deg": 0, "catalogs": [{"name": "PS1", "use": "catsHTM", "rs_arcsec": 600}]}' | jq
[
  {
    "body": {
      "RA": 9.596099480145143e-05,
      "Dec": -5.788890609722272e-05,
      "ErrRA": 0.001,
      "ErrDec": 0.001,
      "MeanEpoch": 55989.22180556,
      "posMeanChi2": 1.3364,
      "gPSFMag": -999,
      "gPSFMagErr": -999,
      "gpsfLikelihood": null,
      "gMeanPSFMagStd": -999,
      "gMeanPSFMagNpt": 0,
      "gMeanPSFMagMin": -999,
      "gMeanPSFMagMax": -999,
      "rPSFMag": 22.0139,
      "rPSFMagErr": 0.186498,
      "rpsfLikelihood": null,
      "rMeanPSFMagStd": -999,
      "rMeanPSFMagNpt": 1,
      "rMeanPSFMagMin": 22.0139,
      "rMeanPSFMagMax": 22.0139,
      "iPSFMag": 21.7694,
      "iPSFMagErr": 0.022677,
      "ipsfLikelihood": null,
      "iMeanPSFMagStd": 0.045144,
      "iMeanPSFMagNpt": 4,
      "iMeanPSFMagMin": 21.7291,
      "iMeanPSFMagMax": 21.8282,
      "zPSFMag": 21.201,
      "zPSFMagErr": 0.036762,
      "zpsfLikelihood": null,
      "zMeanPSFMagStd": 0.073169,
      "zMeanPSFMagNpt": 2,
      "zMeanPSFMagMin": 21.1278,
      "zMeanPSFMagMax": 21.2013,
      "yPSFMag": -999,
      "yPSFMagErr": -999,
      "ypsfLikelihood": null,
      "yMeanPSFMagStd": -999,
      "yMeanPSFMagNpt": 0,
      "yMeanPSFMagMin": -999,
      "yMeanPSFMagMax": -999
    },
    "dist_arcsec": 23.116053641503775
  }
]
```

Veto search against multiple catalogs:
```shell
> curl -s -X POST --header "Content-Type: application/json" http://localhost:8500/cone_search/any --data '{"ra_deg": 0.00549816, "dec_deg": -0.00331679, "catalogs": [{"name": "GAIADR2", "use": "catsHTM", "rs_arcsec": 3}, {"name": "varstars", "use": "extcats", "rs_arcsec": 3}]}' | jq
[
  false,
  false
]
````
