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

### Examples

Measure time for fetching the hosting URL of an example DTID.
```sh
python3 measure.py 
```

Create a twin tree with depth 3 and width 2
```sh
python3 create-twins-tree.py 3 2
```
