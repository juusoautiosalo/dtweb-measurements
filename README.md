# dtweb-measurements
Python scripts for measuring the performance of DTWeb

## Install

<details>
<summary>Environment</summary>

- WSL2
- Python 3.8.5
  - To install python virtual environment: `sudo apt-get install python3-venv`

</details>

Create and activate virtual environment (recommended)
```sh
python3 -m venv env
source env/bin/activate
```

Install with pip
```sh
pip install -r requirements.txt
```

> To deactivate virtual environment:
> ```sh
> deactivate
> ```

## Usage

Run the scripts with python through a terminal.
Current directory must be this folder

### Examples

Measure time for fetching the hosting URL of an example DTID.
```sh
python3 measure.py 
```

Run and plot a series of measurements defined in `params.yaml` file
> If `params.yaml` doesn't exist, `params-example.yaml` is used instead
```sh
python3 run_measurements.py 
```

Replot the latest measurement
```sh
python3 replot_latest.py 
```

Create a twin tree with depth 3 and width 2
```sh
python3 create-twins-tree.py 3 2
```
