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
| `input_path` | str | *required* | Path to the input CSV file containing feature data |
| `--result_path` | str | `results` | Directory where all results and intermediate files will be saved |
| `--db_path` | str | `dataset/lipid_plus.db` | Path to the SQLite lipid spectral database |
| `--ms1_tol` | float | `10.0` | MS1 tolerance (units defined by `--is_ppm`) |
| `--ms2_tol` | float | `20.0` | MS2 fragment tolerance (units defined by `--is_ppm`) |
| `--ms2_threshold` | float | `0.7` | Minimum MS2 similarity score (0.0–1.0) to accept a match |
| `--similarity_method` | str | `weighted_dot_product` | Scoring method: `dot_product`, `weighted_dot_product`, `entropy_similarity`, or `unweighted_entropy_similarity` |
| `--is_ppm` | bool | `True` | Set to `True` for ppm tolerances, `False` for Dalton (Da) |
| `--n_jobs` | int | `4` | Number of parallel workers used for PLSF prediction |
| `--norm_int` | float | `3.0` | Min intensity threshold for MS2 peaks|
| `--adduct_model` | str | `model/adduct.joblib` | Path to the trained adduct prediction model file |
| `--class_model` | str | `model/class.joblib` | Path to the trained lipid class prediction model file |
| `--plsf_model` | str | `model/plsf.joblib` | Path to the trained PLSF chain composition model file |

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
|:---|:---|:---|:---|
| `csv_path` | str | *required* | Path to the input CSV file containing spectral data |
| `--result_path` | str | `.` | Path to the directory where results will be saved |
| `--db_path` | str | `lipid_plus.db` | Path to the lipid database file |
| `--ms1_tol` | float | `20` | MS1 tolerance for database search (units defined by `--is_ppm`) |
| `--ms2_tol` | float | `30` | MS2 tolerance for database search (Daltons) |
| `--method` | str | `weighted_dot_product` | Scoring method for spectral matching: `dot_product`, `weighted_dot_product`, `entropy_similarity`, `unweighted_entropy_similarity` |
| `--ms2_threshold` | float | `0.7` | MS2 score threshold for a match to be considered valid |
| `--is_ppm` | bool | `True` | Specify if MS1 tolerance is in ppm (`True`) or Da (`False`) |
| `--norm_int` | float | `3` | Min intensity threshold for MS2 peaks; if > 3, also normalizes database MS2 |

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
  --fc_threshold 1 
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


## Classes
Lipid class information can be found in [LIPID MAPS](https://www.lipidmaps.org/data/classification/lipid_cns.html). Following are classes that support by LIPID+:

| Class Abbreviation | Full Name of Class | Category Abbreviation | Full Name of Category | 
| ----- | ----- | ----- | ----- | 
| FA | Fatty Acids | FA | Fatty Acyls | 
| CAR | Acyl Carnitines | FA | Fatty Acyls | 
| NAE | N-acyl Ethanolamines | FA | Fatty Acyls | 
| WE | Wax Esters | FA | Fatty Acyls | 
| MG | Monoacylglycerols | GL | Glycerolipids | 
| DG | Diacylglycerols | GL | Glycerolipids | 
| TG | Triacylglycerols | GL | Glycerolipids | 
| MGDG | Monogalactosyldiacylglycerol | GL | Glycerolipids | 
| DGDG | Digalactosyldiacylglycerol | GL | Glycerolipids | 
| SQDG | Sulfoquinovosyldiacylglycerol | GL | Glycerolipids | 
| DGTS | Diacylglyceryl hydroxymethyl-N,N,N-trimethyl-β-alanine | GL | Glycerolipids | 
| DGCC | Diacylglyceryl-N,N,N-trimethylhomoserine | GL | Glycerolipids | 
| DGGA | Diacylglycerylglucuronide | GL | Glycerolipids | 
| LDGTS | Lyso-diacylglyceryl hydroxymethyl-N,N,N-trimethyl-β-alanine | GL | Glycerolipids | 
| LDGCC | Lyso-diacylglyceryl-N,N,N-trimethylhomoserine | GL | Glycerolipids | 
| PC | Phosphatidylcholine | GP | Glycerophospholipids | 
| PE | Phosphatidylethanolamine | GP | Glycerophospholipids | 
| PS | Phosphatidylerine | GP | Glycerophospholipids | 
| PG | Phosphatidylglycerol | GP | Glycerophospholipids | 
| PI | Phosphatidylinositol | GP | Glycerophospholipids | 
| PA | Phosphatidic acid | GP | Glycerophospholipids | 
| LPC | Lysophosphatidylcholine | GP | Glycerophospholipids | 
| LPE | Lysophosphatidylethanolamine | GP | Glycerophospholipids | 
| LPS | Lysophosphatidylserine | GP | Glycerophospholipids | 
| LPG | Lysophosphatidylglycerol | GP | Glycerophospholipids | 
| LPI | Lysophosphatidylinositol | GP | Glycerophospholipids | 
| LPA | Lysophosphatidic acid | GP | Glycerophospholipids | 
| PC-O | Alkyl-phosphatidylcholine | GP | Glycerophospholipids | 
| PE-O | Alkyl-phosphatidylethanolamine | GP | Glycerophospholipids | 
| PG-O | Alkyl-phosphatidylglycerol | GP | Glycerophospholipids | 
| LPC-O | Lyso-alkyl-phosphatidylcholine | GP | Glycerophospholipids | 
| LPE-O | Lyso-alkyl-phosphatidylethanolamine | GP | Glycerophospholipids | 
| PC-P | Phosphatidylcholine plasmalogen | GP | Glycerophospholipids | 
| PE-P | Phosphatidylethanolamine plasmalogen | GP | Glycerophospholipids | 
| PG-P | Phosphatidylglycerol plasmalogen | GP | Glycerophospholipids | 
| CL | Cardiolipin | GP | Glycerophospholipids | 
| BMP | Bis(monoacylglycero)phosphate | GP | Glycerophospholipids | 
| PMeOH | Phosphatidylmethanol | GP | Glycerophospholipids | 
| Cer | Ceramides | SP | Sphingolipids | 
| SM | Sphingomyelin | SP | Sphingolipids | 
| HexCer | Hexosylceramides (GlcCer/GalCer) | SP | Sphingolipids | 
| LacCer | Lactosylceramide | SP | Sphingolipids | 
| PE_Cer | Phosphoethanolamine ceramide | SP | Sphingolipids | 
| PI_Cer | Phosphoinositol ceramide | SP | Sphingolipids | 
| ST | Free Sterols (e.g., Cholesterol) | ST | Sterol Lipids | 
| CE | Cholesteryl Esters | ST | Sterol Lipids | 

## Class Rules

**Rules for assigning lipid classes based on characteristic MS/MS fragmentation patterns.**

| Class | Adduct | Type | m/z / NL | Comment |
| :--- | :--- | :--- | :--- | :--- |
| PC | [M+HCOO]⁻ | NLS | 60.0211 | Loss of methyl group + formic acid |
| PC | [M+CH3COO]⁻ | NLS | 74.0368 | Loss of methyl group + acetic acid |
| PC | [M+H]⁺ | PIS | 184.0733 | Protonated phosphocholine headgroup |
| LPC | [M+H]⁺ | PIS | 184.0733 | Protonated phosphocholine headgroup |
| LPC | [M+H]⁺ | PIS | 104.1070 | [C5H14NO]⁺ fragment; differentiates from PC |
| PE | [M+H]⁺ | NLS | 141.0194 | Loss of phosphoethanolamine headgroup |
| LPE | [M+H]⁺ | NLS | 141.0194 | Loss of phosphoethanolamine headgroup |
| PE | [M-H]⁻ | PIS | 140.0188 | Deprotonated phosphoethanolamine headgroup |
| PE | [M-H]⁻ | PIS | 196.0380 | [C5H11NO5P]⁻ |
| PS | [M+H]⁺ | NLS | 185.0089 | Loss of phosphoserine headgroup |
| PS | [M-H]⁻ | NLS | 87.0320 | Loss of serine moiety |
| PG | [M+H]⁺ | NLS | 172.0135 | Loss of glycerol phosphate headgroup |
| PG | [M+NH4]⁺ | NLS | 189.0402 | Loss of glycerol phosphate headgroup + NH3 |
| PI | [M-H]⁻ | PIS | 241.0119 | Inositol-1,2-cyclic monophosphate anion |
| PI | [M+NH4]⁺ | NLS | 277.0563 | Inositol-1,2-cyclic monophosphate cation + NH3 |
| PA | [M+NH4]⁺ | NLS | 115.0262 | Loss of NH3 + H3PO4 |
| MG | [M+H]⁺ | NLS | 18.0106 | Neutral loss of water (H2O) |
| MG | [M+H]⁺ | NLS | 92.0470 | Neutral loss of glycerol headgroup |
| CE | [M+Na]⁺ | NLS | 368.3441 | Loss of neutral cholestane molecule |
| CE | [M+H]⁺ | PIS | 369.3516 | Dehydrated cholesterol fragment |
| FA | [M-H]⁻ | NLS | 43.9898 | Loss of carbon dioxide (CO2) |
| NAE | [M+H]⁺ | PIS | 62.0600 | Protonated ethanolamine fragment |
| PC-O | [M+H]⁺ | PIS | 184.0733 | Protonated phosphocholine (indistinguishable from PC) |
| PE-O | [M+H]⁺ | NLS | 141.0194 | Loss of phosphoethanolamine (indistinguishable from PE) |

*Note:* "NL" indicates a Neutral Loss.       
<br />
<br />
<br />
**Constraints on the number of chemical elements permitted for different lipid classes.**

| Lipid Class | C (Carbon) | H (Hydrogen) | O (Oxygen) | P (Phosphorus) | N (Nitrogen) | 
 | ----- | ----- | ----- | ----- | ----- | ----- | 
| **PA, PA-O, PA-P** | 8-80 | 15-155 | 8 | 1 | 0 | 
| **PC, PC-O, PC-P** | 13-85 | 26-168 | 8 | 1 | 1 | 
| **PE, PE-O, PE-P** | 10-82 | 22-162 | 8 | 1 | 1 | 
| **PS, PS-O, PS-P** | 13-85 | 24-164 | 10 | 1 | 1 | 
| **PG, PG-O, PG-P** | 11-83 | 21-161 | 10 | 1 | 0 | 
| **PI, PI-O, PI-P** | 14-86 | 25-165 | 13 | 1 | 0 | 
| **CL** | 21-153 | 38-302 | 17 | 2 | 0 | 
| **BMP** | 14-86 | 25-165 | 13 | 1 | 0 | 
| **PMeOH** | 9-81 | 18-158 | 8 | 1 | 0 | 
| **LPA** | 5-42 | 11-83 | 7 | 1 | 0 | 
| **LPC, LPC-O, LPC-P** | 8-45 | 18-90 | 7 | 1 | 1 | 
| **LPE, LPE-O, LPE-P** | 5-42 | 14-84 | 7 | 1 | 1 | 
| **LPS** | 8-45 | 16-86 | 9 | 1 | 1 | 
| **LPG** | 6-43 | 15-85 | 9 | 1 | 0 | 
| **LPI** | 9-46 | 19-89 | 12 | 1 | 0 | 
| **MG, MG-O, MG-P** | 5-42 | 10-82 | 4 | 0 | 0 | 
| **DG, DG-O, DG-P** | 8-78 | 14-152 | 5 | 0 | 0 | 
| **TG, TG-O** | 11-114 | 18-222 | 6 | 0 | 0 | 
| **MGDG** | 14-84 | 24-164 | 10 | 0 | 0 | 
| **DGDG** | 20-90 | 34-174 | 15 | 0 | 0 | 
| **SQDG** | 14-84 | 24-164 | 12 | 0 | 0 | 
| **DGTS/LDGTS** | 18-88 | 35-173 | 7 | 0 | 1 | 
| **DGCC/LDGCC** | 18-88 | 34-172 | 8 | 0 | 1 | 
| **DGGA** | 17-87 | 32-170 | 9 | 0 | 1 | 
| **Cer, Cer-d** | 20-84 | 39-165 | 3 | 0 | 1 | 
| **Cer-t** | 20-84 | 39-167 | 4 | 0 | 1 | 
| **SM, SM-d** | 25-89 | 51-177 | 6 | 1 | 2 | 
| **SM-t** | 25-89 | 51-179 | 7 | 1 | 2 | 
| **PE_Cer** | 22-86 | 44-170 | 6 | 1 | 2 | 
| **HexCer/GalCer/GlcCer** | 26-90 | 49-177 | 8 | 0 | 1 | 
| **LacCer** | 32-96 | 59-189 | 13 | 0 | 1 | 
| **PI_Cer, PI_Cer-d** | 26-90 | 49-179 | 12 | 1 | 1 | 
| **PI_Cer-t** | 26-90 | 49-181 | 13 | 1 | 1 | 
| **ST** | 27-29 | 44-48 | 1 | 0 | 0 | 
| **CE** | 29-65 | 46-110 | 2 | 0 | 0 | 
| **SE** | 29-65 | 46-110 | 2 | 0 | 0 | 
| **FA** | 2-36 | 4-72 | 2 | 0 | 0 | 
| **WE** | 4-72 | 8-144 | 2 | 0 | 0 | 
| **CAR** | 9-43 | 19-85 | 4 | 0 | 1 | 
| **NAE** | 4-40 | 9-81 | 2 | 0 | 1 |



## prediction Confidence
The model outputs probabilities for each of the three components: adduct, class, and plsf. 
For rule-based class classification, the probability is 0.8 if it's the unique intersection of the exact mass and the MS/MS diagnostic ion.

`pred_confidence = (plsf × adduct × class) ^ (1/3)`
Each confidence value has a minimum floor of 0.01 applied before calculation. This prevents an extremely low value from making the final score near zero.

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
#### Last Updated: Dec 29, 2025, Version: 1.0.1
* **Dec 29, 2025**: Add example report.
* **Dec 28, 2025**: Fixed some garbled text issues in visualizations. Update the confidence calculation method.