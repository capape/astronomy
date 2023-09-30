# Astronomy Utilities for AstroSabadell Supernovae Group 

Small utilities for astronomy

## Get latest supernovas and

Generate a PDF with latest supernovae reported in rocherster last n days with magnite less or equal to max-magnitude

getsupernovae.sh max-magnitude last-n-days

```
getsupernovae.sh 17 21
```

## Find objects and prepare a sequence to launch siril fotometry

Find fits processed files in path standard naming of supernovae group for an object and copy to target to generate a sequence

prepare-fotometry.sh object_name path_to_search target_path
    
```
prepare-fotometry.sh 2022aaad . fotometry/2022aaad
```    

## Generate report of supernovae files of supernovae group

Find in current folder files create with standard naming of supernovae group and create a terminal report

```
supernovas-data.sh 
``````
