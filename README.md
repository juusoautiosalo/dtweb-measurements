# dtweb-measurements
Python scripts for measuring the performance of Digital Twin Web servers and registries.
As Digital Twin Web standards are still under development,
[Twinbase](https://github.com/twinbase/twinbase) servers are used for example measurements.

## Operating system
Any Linux terminal should work directly or with minor modifications.

Scripts were developed and tested on Windows 10 with [WSL2](https://www.omgubuntu.co.uk/how-to-install-wsl2-on-windows-10) terminal (4.19.84-microsoft-standard) with Python 3.8.5
  - To install python virtual environment: `sudo apt-get install python3-venv`

## Install

Clone source code
```sh
git clone https://github.com/juusoautiosalo/dtweb-measurements.git
```

Create and activate virtual environment (recommended)
```sh
python3 -m venv env
source env/bin/activate
```

> To deactivate virtual environment:
> ```sh
> deactivate
> ```

Install with pip
```sh
pip install -r requirements.txt
```
> While installing, you may get `ERROR: Failed building wheel for asks`.
> It's okay and these scripts still work.

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
>
> Note: This takes approximately 3 minutes with the default parameters!
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
