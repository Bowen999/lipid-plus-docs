# Installation
### Clone the project folder and download database 
Download the source code at [https://github.com/Bowen999/LIPID-PLUS/releases](https://github.com/Bowen999/LIPID-PLUS/releases) or run the command below:
```bash
git clone https://github.com/Bowen999/LIPID-PLUS.git
cd LIPID-PLUS
mkdir -p dataset
wget -O dataset/lipid_plus.db https://github.com/Bowen999/LIPID-PLUS/releases/download/v0.0.0/lipid_plus.db

# (if no wget，use curl)
# curl -L -o dataset/lipid_plus.db https://github.com/Bowen999/LIPID-PLUS/releases/download/v0.0.0/lipid_plus.db
```

### Install the dependencies 

```
conda create -n lipid_plus python=3.12 -y
conda activate lipid_plus

pip install -r requirements.txt
```


# Quick Start

### Using the All-in-One Identification Pipeline

The easiest way to run the complete identification pipeline (database search + machine learning prediction) with default settings:

```bash
python run.py feature_df.csv
```
&nbsp;


The usage of the pipeline with custom parameters can be found in the `Advanced Usage` section.  

The pipeline will generate several files in the `results/` directory.   
**Main result file**: `results/final_annotations.csv` contains the complete lipid annotations result, search/prediction are recorded in `name` column.
&nbsp;
```text
results/
├── identification_result.csv     # Final merged output (Database + ML predictions)
├── process_files/
├──── processed_feature_table.csv   # Normalized and unfolded MS2 data (Step 0)
├──── db_matched_df.csv             # Lipids identified by database search (Step 1)
├──── dark_lipid.csv                # Unknown lipids sent to prediction pipeline
├──── adduct_predictions.csv        # Intermediate adduct predictions (Step 2)
├──── class_predictions.csv         # Intermediate class predictions (Step 3)
└──── final_annotations.csv         # Final ML chain composition predictions (Step 4)
```

&nbsp;

### Lipidomics Analysis Report Generation
An interactive, shareable, and fully customized dynamic lipidomics HTML report (see [example](https://bowen999.github.io/lipid-plus-docs/example_report.html)) can be generated from the previous identification results (identification_result.csv). An example is shown below:

```
python code/report_generate.py \
  --input_path results/identification_result.csv \
  --groups 0h 2h 4h 8h \
  --group_1 0h \
  --group_2 8h \
  --p_value_threshold 0.1 \
  --fc_threshold 1
```
&nbsp;
**Note: To run this process, the input file must contain at least 3 groups along with intensity or concentration values, and user must adjust the `groups, group_1, and group_2` parameters to match the experimental design.**

&nbsp;

| Parameter | Type | Description |
| :--- | :--- | :--- | :--- |
| `--input_path` | `String` | The file path to the identification result|
| `--groups` | `List` | Space-separated list of all group prefixes present in the CSV columns (e.g., `Control Treated`). |
| `--group_1` | `String`| The first group for differential analysis. Must be in `--groups`. |
| `--group_2` | `String` | The second group for differential analysis. Must be in `--groups`. |

# Advanced Usage

## Identification Pipeline
If you need different settings:

```bash
# Custom result directory
python run.py feature_df.csv --result_path my_results/

# Different MS tolerance
python run.py feature_df.csv \
    --ms1_tol 10 \
    --ms_2tol 20 \
    --ms2_threshold 0.8 \
    --n_jobs -1
```
&nbsp;

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `input_path` | `str` | *(Required)* | Path to input CSV file |
| `--adduct_model` | `str` | `'model/adduct.joblib'` | Path to trained adduct prediction model |
| `--class_model` | `str` | `'model/class.joblib'` | Path to trained class prediction model |
| `--plsf_model` | `str` | `'model/plsf.joblib'` | Path to trained PLSF model |
| `--result_path` | `str` | `'results'` | Directory to save all results |
| `--db_path` | `str` | `'dataset/lipid_plus.db'` | Path to lipid database file |
| `--ms1_tol` | `float` | `0.005` | MS1 tolerance for database search and prediction (in ppm)|
| `--ms2_tol` | `float` | `0.01` | MS2 tolerance for database search nd prediction (in ppm)|
| `--is_ppm`|  `bool`| `True`| If True, tolerances (--ms1_tol, --ms2_tol) are in ppm; if False, in Da|
| `--MS2_threshold` | `float` | `0.7` | Minimum MS2 similarity score for database match |
|`--n_jobs`|`int`|`4`|Number of parallel workers to use for the PLSF prediction|

Your input_path CSV must contain:
- `precursor_mz`: Precursor mass-to-charge ratio
- `adduct`: Adduct type (e.g., `[M+H]+`, `[M+Na]+`, `[M-H]-`).
- `MS2`: MS/MS spectrum as string representation of list, e.g., `"[[100.0, 1500], [200.5, 3000]]"`

*If you only have `ion_mode` (e.g., `Positive` and `Negative`), you can use `Adduct Prediction` to predict adduct (see Advanced Usage - Adduct Prediction)*

## Database Search
Searches a spectral database to identify known lipids based on precursor m/z and MS2 similarity.
Similarity caculation based on [MSEntropy](https://github.com/YuanyueLi/MSEntropy?tab=readme-ov-file), including **dot product, weighted dot product, entropy similarity, and unweighted entropy similarity**.

#### Command

```bash
python code/db_search.py feature_df.csv \
    --result_path results/ \
    --db_path lipid.db \
    --MS1_tol 0.005 \
    --MS2_tol 0.01 \
    --MS2_threshold 0.7 \
    --method weighted_dot_product \
    --is_ppm False
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `csv_path` | str | *required* | Path to input CSV file |
| `--result_path` | str | `.` | Output directory |
| `--db_path` | str | `lipid_plus.db` | Path to SQLite database |
| `--MS1_tol` | float | `0.005` | MS1 tolerance (Da or ppm) |
| `--MS2_tol` | float | `0.01` | MS2 fragment tolerance (Da) |
| `--method` | str | `weighted_dot_product` | Scoring method: `dot_product`, `weighted_dot_product`, `entropy_similarity`, `unweighted_entropy_similarity` |
| `--MS2_threshold` | float | `0.7` | Minimum MS2 score (0-1) to accept a match |
| `--is_ppm` | bool | `False` | Use ppm for MS1 tolerance (True) or Da (False) |

#### Input Requirements

Your CSV must contain:
- `precursor_mz`: Precursor mass-to-charge ratio
- `adduct`: Adduct type (e.g., `[M+H]+`, `[M+Na]+`, `[M-H]-`)
- `MS2`: MS/MS spectrum as string representation of list, e.g., `"[[100.0, 1500], [200.5, 3000]]"`

#### Output Files
**annotated_df.csv**: Successfully matched lipids with database annotations
   * Contains all original columns plus:
   * `name`, `formula`, `class`, `category` (from database)
   * `mass_diff_ppm`: Mass accuracy
   * 3 Spectral similarity scores
   
**dark_lipid.csv**: Unknown lipids that didn't match the database
   * These will be processed by the prediction steps

---

## Adduct Prediction

Predicts the adduct type for unknown lipids using a trained machine learning model.

#### Command
To perform adduct prediction, you must first expand the MS2 column into `mz_*` columns.

```bash
python code/process_ms2.py feature_df.csv --output_path input.csv
```

then:

```bash
python code/adduct_predict.py input.csv model/adduct.joblib \
    --output_path results/adduct_predictions.csv
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | str | *required* | Input CSV file |
| `model_path` | str | *required* | Path to trained adduct model (.joblib) |
| `--output_path` `-o` | str | `adduct_predict.csv` | Output file path |

#### Input Requirements

The CSV must contain:
- `precursor_mz`: Precursor m/z (will be rounded to 2 decimals)
- `ion_mode`: Ion mode (`positive` or `negative`)
- `mz_*` columns: Binary features (0/1) indicating presence of fragment ions

#### Output Columns

Original columns plus:
- `predicted_adduct`: Predicted adduct type
- `adduct_confidence`: Prediction confidence (0-1), if available
---


## Class Prediction

The lipid class is first determined by possible exact masses (the head-group mass is fixed, while the tail-chain masses are discontinuous) and by MS2 fragments or neutral losses to narrow down the candidate range. Then, within this possible range, machine learning is applied for further prediction.


#### Command
To perform adduct prediction, you must first expand the MS2 column into `mz_*` columns.
```bash
python code/process_ms2.py feature_df.csv --output_path input.csv
```

then:

```bash
python code/class_predict.py input.csv model/class.joblib \
    --output_path results/class_predictions.csv \
    --ms1_tol 10 \
    --ms2_tol 20
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | str | *required* | Input CSV file |
| `model_path` | str | *required* | Path to trained class model (.joblib) |
| `--output_path` `-o` | str | `class_pred.csv` | Output file path |
| `--ms1_tol` | float | `10.0` | MS1 tolerance for rule-based matching (ppm) |
| `--ms2_tol` | float | `20.0` | MS2 tolerance for rule-based matching (ppm) |
| `--no-rules` | flag | `False` | Skip rule-based classification, use ML only |

#### Input Requirements

The CSV must contain:
- `precursor_mz`: Precursor m/z
- `ion_mode`: Ion mode
- `adduct` or `predicted_adduct`: Adduct type
- `mz_*` columns: Fragment features
- `MS2` or `MS2_norm`: MS/MS spectrum (for rule-based classification)

#### Two-Stage Process

1. **Rule-Based Classification**: Uses chemical knowledge (exact mass and fragmentation patterns)
   - High confidence for lipids with characteristic fragments
   - Marks successfully classified lipids (only has one possible class under applied rules) with `prediction_source = 'rule-based'`

2. **ML-Based Prediction**: If exact mass and fragment patterns overlap is not only one,
   - Uses machine learning model
   - Marks predictions with `prediction_source = 'model-based'`

#### Output Columns

Original columns plus:
- `predicted_class`: Predicted lipid class (e.g., PC, PE, TG, Cer)
- `prediction_source`: `'rule-based'` or `'model-based'`
- `class_confidence`: Confidence score (0-1)
- `category`: Lipid category (e.g., Glycerophospholipids, Sphingolipids)
- `num_chain`: Number of fatty acid chains
- `classes_mz`: Possible classes from precursor mass (rule-based)
- `classes_ms2`: Possible classes from MS2 fragments (rule-based)

#### Example

```bash
# Default (hybrid approach)
python code/class_predict.py results/with_adducts.csv class.joblib \
    -o results/with_classes.csv

# Strict tolerances (low-resolution data)
python code/class_predict.py input.csv class.joblib \
    -o output.csv --ms1_tol 20 --ms2_tol 30
```
---

## PLSF Prediction

Predicts detailed fatty acid chain compositions (number of carbons and double bonds in each chain).

#### Command
```bash
python code/predict_plsf.py input.csv model/plsf.joblib \
    --output_path results/final_output.csv
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_path` | str | *required* | Path to trained PLSF model (.joblib) |
| `input_path` | str | *required* | Input CSV file |
| `-o` `--output_path` | str | `result.csv` | Output file path |
|`n-jobs`|int|2| CPU cores number are used |
#### Input Requirements

The CSV must contain:
- `precursor_mz`: Precursor m/z (rounded to 2 decimals)
- `adduct` or `predicted_adduct`: Adduct type
- `class` or `predicted_class`: Lipid class
- `num_chain`: Number of fatty acid chains (1-4)
- `mz_*` columns: Fragment features

#### Special Handling

- **Single-chain lipids** (`num_chain=1`): Direct mass calculation instead of model
- **Unknown adducts/classes**: Marked as invalid, predictions set to NaN
- **Confidence scores**: Combined from PLSF, class, and adduct predictions

#### Output Columns

Cleaned output with:
- `name`: Combined lipid name (e.g., "PC 16:0_18:1")
- `precursor_mz`, `ion_mode`, `adduct`, `class`, `category`
- `num_chain`: Number of chains
- `pred_confidence`: Average confidence across all prediction steps
- `plsf_rank1`, `plsf_rank2`, `plsf_rank3`: Top 3 chain composition predictions

#### Name Format
The `name` column combines class and chain information:
- Format: `{Class} {C1}:{DB1}_{C2}:{DB2}_{C3}:{DB3}_{C4}:{DB4}`
- Chains sorted by length (descending)
- Zero chains (0:0) are omitted
- Examples:
  - `PC 16:0_18:1` (PC with C16:0 and C18:1)
  - `TG 16:0_18:1_18:2` (TG with three chains)
  - `Cer 18:1_16:0` (Ceramide with two chains)
---

## Alternative: Formula Annotation

#### Command

```bash
python code/formula_annotation.py input.csv \
    --output_path results/formulas/ \
    --ms1_tol 10 \
    --ms2_tol 20
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | str | *required* | Input CSV file |
| `--output_path` | str | `result/process_file` | Output directory |
| `--ms1_tol` | float | `15.0` | MS1 tolerance for formula annotation (ppm) |
| `--ms2_tol` | float | `20.0` | MS2 tolerance for formula annotation (ppm) |

#### What It Does

1. Converts CSV to MGF format
2. Uses [MsBuddy](https://github.com/Philipbear/msbuddy) to predict molecular formulas
3. Applies class-specific rules for re-rank formulas 
4. Generates formula candidates

#### Output Files

- `input.mgf`: MGF format for MsBuddy
- `buddy_result.csv`: Raw MsBuddy predictions
- `formula_result.csv`: Processed formulas with class rules applied

#### Output Columns

- `predicted_formula`: Top-ranked molecular formula
- `formula_rank_1` to `formula_rank_5`: Top 5 formula candidates
- All original input columns

#### Example

```bash
# High-resolution data (tight tolerances)
python formula_annotation.py data.csv \
    --output_path results/formulas/ \
    --ms1_tol 5 \
    --ms2_tol 10
```

---

## Report Generation

```
python code/report_generate.py \
  --input_path results/identification_result.csv \
  --groups 0h 2h 4h 8h \
  --group_1 0h \
  --group_2 8h \
  --p_value_threshold 0.1 \
  --fc_threshold 1 \
```
&nbsp;

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--input_path` | `String` | **Required** | The file path to the identification result|
| `--groups` | `List` | **Required** | Space-separated list of all group prefixes present in the CSV columns (e.g., `Control Treated`). |
| `--group_1` | `String` | **Required** | The first group for differential analysis. Must be in `--groups`. |
| `--group_2` | `String` | **Required** | The second group for differential analysis. Must be in `--groups`. |
| `--output_path` | `String` | `results` | Directory where the final HTML report and material files will be saved. |
| `--confidence` |`Float`| `0.8` | Confidence threshold for filtering.|
| `--int_threshold` | `Integer` | `3000` | Intensity threshold. |
| `--p_value_threshold` | `Float` |`0.05`|The significance threshold for P-values in the Volcano plot.|
| `--fc_threshold` | `Float` | `1.2` | The fold-change threshold for determining significant lipids. |
| `--keep_cols` | `List` | `index name precursor_mz adduct MS2_norm` | Specific columns to retain for the interactive Mass Spec table in the report. |
---


# FAQ
## Directory Structure

For the simplest usage, organize your files as follows:

```
your_project/
├── run.py                          # The main pipeline script
├── model/                          # Model directory
│   ├── adduct.joblib              # Adduct prediction model
│   ├── class.joblib               # Class prediction model
│   └── plsf.joblib                # PLSF model
├── dataset/                        # Database directory
│   └── lipid.db                   # Reference database
├── code/                           # All step scripts
│   ├── db_search.py               # Step 1: Database search
│   ├── adduct_predict.py          # Step 2: Adduct prediction
│   ├── class_predict.py           # Step 3: Class prediction
│   ├── predict_plsf.py            # Step 4: PLSF prediction
│   ├── formula_annotation.py      # Alternative workflow
│   └── ......
├── feature_df.csv                  # Your input data
└── results/                        # Output directory (created automatically)
```
&nbsp;
With this structure, you can simply run:
```bash
python run.py feature_df.csv
```

## Input data format

### Required Columns
Your input CSV file must contain these columns:

```csv
index,precursor_mz,ion_mode,adduct,MS2,mz_100,mz_101,...
F000001,760.5851,positive,[M+H]+,"[[184.07, 5000], [104.11, 2000]]",1,0,...
F000002,788.6164,positive,[M+H]+,"[[184.07, 8000], [506.36, 1500]]",1,0,...
```

#### Column Descriptions

| Column | Type | Description | Required For |
|--------|------|-------------|--------------|
| `index` | str | Unique identifier | All steps |
| `precursor_mz` | float | Precursor mass-to-charge ratio | All steps |
| `ion_mode` | str | `positive` or `negative` | Adduct prediction |
| `adduct` | str | Adduct type (e.g., `[M+H]+`) | DB search, class prediction, PLSF prediction |
| `MS2` | str/list | MS/MS spectrum as `[[mz, intensity], ...]` | DB search, class prediction |



## What is PLSF
The **Primary Lipid Structural Features (PLSF)** are the fundamental parts of a lipid structure that can be **reliably identified** using conventional tandem mass spectrometry.

PLSFs specifically include:
* **Lipid Class**: for example, `PC`
* **Composition of Each Chain**: for example, `18:2_16:1`


For example, the complete lipid name `PC 10:0/18:2(9Z, 12Z)` is simplified to its PLSF: `PC 10:0_18:2`.  

This representation avoids the ambiguity and false positives associated with predicting complete structures, which is often unsuitable for lipids, its fixed and simple format makes it also more suitable for machine learning.


## Class
Lipid class information can be found in [LIPID MAPS](https://www.lipidmaps.org/data/classification/lipid_cns.html). Following are classes that support by LIPID+:

| Class  | Category | Number of Tail | Full Name of Class                       | Full Name of Category    |
| :----- | :------- | :-------- | :--------------------------------------- | :----------------------- |
| CAR    | FA       | 1         | Acyl carnitine                           | Fatty Acyls              |
| FA     | FA       | 1         | Fatty Acid                               | Fatty Acyls              |
| NAE    | FA       | 1         | N-acyl ethanolamine                      | Fatty Acyls              |
| WE     | FA       | 1         | Wax Ester                                | Fatty Acyls              |
| DG     | GL       | 2         | Diacylglycerol                           | Glycerolipids            |
| DGDG   | GL       | 2         | Digalactosyldiacylglycerol               | Glycerolipids            |
| MG     | GL       | 3         | Monoacylglycerol                         | Glycerolipids            |
| MGDG   | GL       | 2         | Monogalactosyldiacylglycerol             | Glycerolipids            |
| SQDG   | GL       | 2         | Sulfoquinovosyldiacylglycerol            | Glycerolipids            |
| TG     | GL       | 3         | Triacylglycerol                          | Glycerolipids            |
| BMP    | GP       | 2         | Bis(monoacylglycero)phosphate            | Glycerophospholipids     |
| CL     | GP       | 4         | Cardiolipin                              | Glycerophospholipids     |
| LPA    | GP       | 1         | Lysophosphatidic acid                    | Glycerophospholipids     |
| LPC    | GP       | 1         | Lysophosphatidylcholine                  | Glycerophospholipids     |
| LPC-O  | GP       | 1         | Lyso-alkylphosphatidylcholine            | Glycerophospholipids     |
| LPE    | GP       | 1         | Lysophosphatidylethanolamine             | Glycerophospholipids     |
| LPE-O  | GP       | 1         | Lyso-alkylphosphatidylethanolamine       | Glycerophospholipids     |
| LPG    | GP       | 1         | Lysophosphatidylglycerol                 | Glycerophospholipids     |
| LPI    | GP       | 1         | Lysophosphatidylinositol                 | Glycerophospholipids     |
| LPS    | GP       | 1         | Lysophosphatidylserine                   | Glycerophospholipids     |
| PA     | GP       | 2         | Phosphatidic acid                        | Glycerophospholipids     |
| PC     | GP       | 2         | Phosphatidylcholine                      | Glycerophospholipids     |
| PC-O   | GP       | 2         | Alkylphosphatidylcholine (PC-O)          | Glycerophospholipids     |
| PC-P   | GP       | 2         | Plasmenylcholine (PC-P)                  | Glycerophospholipids     |
| PE     | GP       | 2         | Phosphatidylethanolamine                 | Glycerophospholipids     |
| PE-O   | GP       | 2         | Alkylphosphatidylethanolamine (PE-O)     | Glycerophospholipids     |
| PE-P   | GP       | 2         | Plasmenylethanolamine (PE-P)             | Glycerophospholipids     |
| PG     | GP       | 2         | Phosphatidylglycerol                     | Glycerophospholipids     |
| PG-O   | GP       | 2         | Alkylphosphatidylglycerol (PG-O)         | Glycerophospholipids     |
| PG-P   | GP       | 2         | Plasmenylglycerol (PG-P)                 | Glycerophospholipids     |
| PI     | GP       | 2         | Phosphatidylinositol                     | Glycerophospholipids     |
| PMeOH  | GP       | 2         | Phosphatidylmethanol                     | Glycerophospholipids     |
| PS     | GP       | 2         | Phosphatidylserine                       | Glycerophospholipids     |
| DGCC   | SL       | 2         | Diacylglyceryl-N,N,N-trimethylhomoserine | Saccharolipids           |
| DGGA   | SL       | 2         | Diacylglycerylglucuronide                | Saccharolipids           |
| DGTS   | SL       | 2         | Diacylglyceryl hydroxymethyl-N,N,N-trimethyl-beta-alanine | Saccharolipids           |
| LDGCC  | SL       | 1         | Lyso-diacylglyceryl-N,N,N-trimethylhomoserine | Saccharolipids           |
| LDGTS  | SL       | 1         | Lyso-diacylglyceryl hydroxymethyl-N,N,N-trimethyl-beta-alanine | Saccharolipids           |
| Cer    | SP       | 2         | Ceramide                                 | Sphingolipids            |
| GalCer | SP       | 2         | Galactosylceramide                       | Sphingolipids            |
| GlcCer | SP       | 2         | Glucosylceramide                         | Sphingolipids            |
| HexCer | SP       | 2         | Hexosylceramide                          | Sphingolipids            |
| LacCer | SP       | 2         | Lactosylceramide                         | Sphingolipids            |
| PE_Cer | SP       | 3         | Phosphoethanolamine ceramide             | Sphingolipids            |
| PI_Cer | SP       | 3         | Phosphoinositol ceramide                 | Sphingolipids            |
| SM     | SP       | 2         | Sphingomyelin                            | Sphingolipids            |
| CE     | ST       | 1         | Cholesterol Ester                        | Sterol Lipids            |
| ST     | ST       | 1         | Sterol                                   | Sterol Lipids            |

## Data Source
The **LIPID+** dataset is aggregated from the following MS libraries and resources:  

* [**MS-DIAL Lipidome Atlas**](https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-020-0531-2/MediaObjects/41587_2020_531_MOESM5_ESM.zip)
* [**GNPS (Global Natural Products Social Molecular Networking)**](https://external.gnps2.org/gnpslibrary)
* [**PNNL Lipid Library (Pacific Northwest National Laboratory Lipid Library)**](https://gnps.ucsd.edu/ProteoSAFe/gnpslibrary.jsp?library=PNNL-LIPIDS-POSITIVE)
* [**MassBank**](https://massbank.eu)
* [**MoNA (MassBank of North America)**](https://mona.fiehnlab.ucdavis.edu)
* [**MassSpecGym**](https://huggingface.co/datasets/roman-bushuiev/MassSpecGym)

For metabolite MS databases (GNPS, MassBank, MoNA, MassSpecGym), spectra were filtered by matching the **[first InChIKey block](https://en.wikipedia.org/wiki/International_Chemical_Identifier)** to structures in lipid databases including [**LIPID MAPS**](https://www.lipidmaps.org), [**SwissLipids**](https://www.swisslipids.org) and [**MS-DIAL Lipid Database**](https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-020-0531-2/MediaObjects/41587_2020_531_MOESM5_ESM.zip)



# Release Note
#### Last Updated: Dec 28, 2025, Version: 1.0.1

* **Dec 28, 2025**: Fixed some garbled text issues in visualizations.