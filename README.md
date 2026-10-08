# ph-dash-practice

Private working notes for the Programming Historian lesson
[Creating an Interactive Data Visualization Dashboard with Dash](https://programminghistorian.org/en/lessons/interactive-data-visualization-dashboard),
and the build of my own dashboard.

## Getting started
```bash
cd ~/Documents/GitHub/ph-dash-practice
source venv/bin/activate
jupyter lab
```
Choose the **Python (ph-dash)** kernel in each notebook.

## Notebooks
| # | Notebook | Lesson sections |
|---|---|---|
| 01 | `notebooks/01_setup.ipynb` | Prerequisites, virtual environment, installing libraries |
| 02 | `notebooks/02_data_retrieval_and_cleaning.ipynb` | Imports, API retrieval, preparing & cleaning data |
| 03 | `notebooks/03_building_the_dashboard.ipynb` | App instance, frontend, backend, testing |
| 04 | `notebooks/04_deployment.ipynb` | GitHub + Render deployment |
| 05 | `notebooks/05_second_example.ipynb` | Chronicling America pie-chart dashboard |
| 06 | `notebooks/06_my_dashboard.ipynb` | My own dataset and dashboard |

## Folders
- `tutorial_app/`: deployable tutorial apps (`app.py`, `app-rq2.py`), exported from notebooks 03 and 05
- `my_dashboard/`: my final `app.py`, exported from notebook 06, then copied to its own private deploy repo
- `data/`: datasets
- `archive/`: my first attempt at the lesson (before this repo existed)
