# SynthText (Docker)

**Docker-enabled fork** of the official SynthText repository for generating synthetic text images as described in ["Synthetic Data for Text Localisation in Natural Images", Ankush Gupta, Andrea Vedaldi, Andrew Zisserman, CVPR 2016](http://www.robots.ox.ac.uk/~vgg/data/scenetext/).


**Synthetic Scene-Text Image Samples**
![Synthetic Scene-Text Samples](samples.png "Synthetic Samples")

## Getting Started

```bash
# Build Docker images
docker-compose build

# Run SynthText to generate samples
docker-compose run --rm synthtext python gen.py
```

This will download a data file (~56M) to the `data` directory. This data file includes:

  - **dset.h5**: This is a sample h5 file which contains a set of 5 images along with their depth and segmentation information. Note, this is just given as an example; you are encouraged to add more images (along with their depth and segmentation information) to this database for your own use.
  - **data/fonts**: three sample fonts (add more fonts to this folder and then update `fonts/fontlist.txt` with their paths).
  - **data/newsgroup**: Text-source (from the News Group dataset). This can be subsituted with any text file. Look inside `text_utils.py` to see how the text inside this file is used by the renderer.
  - **data/models/colors_new.cp**: Color-model (foreground/background text color model), learnt from the IIIT-5K word dataset.
  - **data/models**: Other cPickle files (**char\_freq.cp**: frequency of each character in the text dataset; **font\_px2pt.cp**: conversion from pt to px for various fonts: If you add a new font, make sure that the corresponding model is present in this file, if not you can add it by adapting `invert_font_size.py`).

This script will generate random scene-text image samples and store them in an h5 file in `results/SynthText.h5`.
If you want to visualize the results stored in  `results/SynthText.h5` later, run:

```bash
docker-compose run --rm synthtext python visualize_results.py
```

## Pre-generated Dataset

A dataset with approximately 800000 synthetic scene-text images generated with this code can be downloaded with following procedures.

### Download files
The 8,000 background images used in the paper, along with their segmentation and depth masks, can be downloaded from [here](https://academictorrents.com/details/2dba9518166cbd141534cbf381aa3e99a087e83c).

Place downloaded directory `bg_data/` in `downloads/bg_data/`.

| Filename               | Size | Description                                          | MD5 hash                         |
|:-----------------------| ----:|:-----------------------------------------------------|:---------------------------------|
| `bg_data/imnames.cp`   | 180K | Names of images which do not contain background text |                                  |
| `bg_data/bg_img.tar.gz`| 8.9G | Images (filter these using `imnames.cp`)             | 3eac26af5f731792c9d95838a23b5047 |
| `bg_data/depth.h5`     |  15G | Depth maps                                           | af97f6e6c9651af4efb7b1ff12a5dc1b |
| `bg_data/seg.h5`       | 6.9G | Segmentation maps                                    | 1605f6e629b2524a3902a5ea729e86b2 |

Note: I do not own the copyright to these images.

### Pack files to h5

```bash
# Extracts `bg_img.tar.gz` into the `bg_img/` directory
tar xf downloads/bg_data/bg_img.tar.gz -C downloads/bg_data

# Pack images + depth + segmentation into a single HDF5
docker-compose run --rm synthtext python pack_bgdata_to_h5.py -i downloads/bg_data -o data/dset_big.h5
```

### Generate Synth Images with the big backgrond images

```bash
docker-compose run --rm synthtext python gen.py --db_path data/dset_big.h5
```

## Cumstom Font

### Add Fonts

Place any font files (.ttf, .otf) in `data/fonts` and update `data/fonts/fontlist.txt` to write relative paths to the files.

### Update Font Size Model After Adding Fonts
After adding (or removing/replacing) fonts, regenerate the size conversion model `data/models/font_px2pt.cp`:

```bash
docker-compose run --rm synthtext python invert_font_size.py --viz
```

`--viz` saves diagnostic fit plots to `results/font_model_plots/` (useful to quickly check the linear fit quality).
