# Font sources

Downloaded for this project on 2026-09-25 (UTC). Fonts are included as downloaded, with their internal metadata unchanged; only local filenames were simplified. Their authors retain their rights. This project's Python code does not relicense the font files. Font-embedded copyright/license strings and SHA-256 hashes are recorded in `dataset/generation_report.json`.

| Local filename | Font | Source page | Download source |
|---|---|---|---|
| `DastNevis.otf` | Dast Nevis | [FontPack](https://github.com/Hamid-Najafi/FontPack), [handwriting description](https://irfont.blogfa.com/tag/فونت-دست-نویس) | [Original OTF](https://raw.githubusercontent.com/Hamid-Najafi/FontPack/master/Persian/Dast%20Nevis.OTF) |
| `Far_Khodkar.ttf` | Far.Khodkar | [Font description](https://fontchi.com/fonts/far-khodkar/) | [Original TTF](https://raw.githubusercontent.com/Hamid-Najafi/FontPack/master/Persian/Far_khodkar.ttf) |
| `Dima_DastNevis.ttf` | Dima Dast Nevis | [Farsgraphic](https://farsgraphic.com/27026/dima-dast-nevis-font/) | TTF extracted from that page's linked Dima Dast Nevis RAR archive |
| `Digi_Darya_Bold.ttf` | Digi Darya Bold | [Free handwriting fonts](https://diakographic.ir/5fontdastnevis/) | [Publisher-linked download page](https://s30.picofile.com/file/8476309468/Digi_Darya_Bold.ttf.html) |
| `Digi_Almas_Bold.ttf` | Digi Almas Bold | [Free handwriting fonts](https://diakographic.ir/5fontdastnevis/) | [Publisher-linked download page](https://s30.picofile.com/file/8476309500/Digi_Almas_Bold.ttf.html) |

All five files passed Unicode coverage checks for the 32 Persian letters. Preview grids were reviewed. Far_DastNevis and pHalls Khodkar were also examined but omitted because their rendered letter sets duplicate included fonts; they are not counted as extra handwriting styles.

Dima Dast Nevis is described by its source as combining formal and handwriting styles; the other fonts supply more visibly informal pen/marker styles. No Arial, Times, Vazir, Sahel, or other ordinary body-text font was added to increase the font count.

## Additions for the revised package — 2026-10-30

| Local filename | Source repository / file | Role |
|---|---|---|
| `IranNastaliq.ttf` | https://github.com/farsi-fonts/fonts-irannastaliq — `IranNastaliq.ttf` | Persian Nastaliq calligraphy |
| `Gulzar-Regular.ttf` | https://github.com/google/fonts/tree/main/ofl/gulzar — `Gulzar-Regular.ttf` | Urdu Nastaliq auxiliary style; coverage checked against the 32 Persian letters |
| `NotoNastaliqUrdu.ttf` | https://github.com/google/fonts/tree/main/ofl/notonastaliqurdu — `NotoNastaliqUrdu[wght].ttf` | Urdu Nastaliq auxiliary style; default variable-font weight, not a separate writer per weight |

Gulzar design source: https://github.com/googlefonts/Gulzar

Noto upstream: https://github.com/notofonts/nastaliq

The additions are calligraphic fonts, not scans of ordinary Persian handwriting. The previous five font files are preserved. Different filenames, font weights, and augmented images do not count as independent writers. Downloaded files' hashes and embedded rights metadata are recorded in `dataset_augmented/generation_report.json`. Separate downloaded license texts are in `licenses/`; the original five font files retain their embedded notices and original provenance above. No blanket redistribution license is asserted for the original five fonts; check each rights holder's terms before republishing the font files.

## Model documentation

- https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html
- https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html
- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
- https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
