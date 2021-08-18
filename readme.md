# Instruction

## Data

The dataset contains original dataset and processed data.

### Original Dataset

Original datasets are the untouched raw data from the databases or website.

- Land use data

  - Geomni building use
  - OS Greenspace

- Population data

  - UK-M-2020-PE.zip: Middle-2020 population estimates at local authority and region level for England and Wales, by age and sex.
  - World Pop: The 100m resolution gridded population estimates developed by WorldPop's open access dataset. 

- Google mobility data

  2020_GB_Region_Mobility_Report.csv: Google mobility data for the UK from 15th February 2020 to 31st December 2021.

- COVID statistics

  The COVID statistics in Barking and Dagenham, London

  - COVID cases: People tested positive cases by specimen date (Daily and Sum)
  - Death cases: Deaths within 28 days of positive test by date of death

- Others

  - Boundary of London: The shapefile of boundaries of London divided by borough.


### Processed Data

This folder includes data after basic data cleaning.

The grid.geojson is the environment of ABM model.

## Model (Python Codes)

The codes includes two separate folder contains model for lockdown and lockdown eased scenarios.

To run the code, you have to install the relevant libraries referenced in the head of codes.

Then, open terminal in the same directory and run 

```{Python}
mesa runserver
```

Then a local webpage will be open at browser. Click 'Start' to run then model or 'Step' to run step by step.

## Results

- No Lockdown (Lockdown eased scenario)

  This is the simulation results of lockdown eased scenario;

- With Lockdown (Lockdown scenario)

  This is the simulation results of lockdown scenario;

- Validation

  This is the comparison between simulation results of lockdown eased scenario and real world statistics;
