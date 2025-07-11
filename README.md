# WebServicesManager

**A script set for web services management.**

## Dependencies

- [astral uv: Python package manager](https://docs.astral.sh/uv/)

## Usage

- First clone the repository
  ```bash
  # the remote repository where located on my cloud server
  git clone https://gitea.virtualguard101.com/virtualguard101/webscripts.git
  cd webscripts
  ```

- Initialize Python virtual environment and install dependencies
  ```bash
  uv venv --python=3.12
  uv pip install -r requirement.txt
  ```

- Launch the manager with `main.py`

  >[!IMPORTANT]
  >If you have some reasons have to waste using uv, you should create virtual environment and install the dependencies manually, otherwise, it is recommended to use uv to manage those because of its convenience.

  ```bash
  uv run main.py
  ```

  Add `-h` as parameter to find usage:
  ```bash
  uv run main.py -h
  usage: main.py [-h] {register,list,operate} ...

  =====> Web Services Manager <=====

  positional arguments:
    {register,list,operate}
      register            Register a new service
      list                List all services
      operate             Service operations to carry out

  options:
    -h, --help            show this help message and exit
  ```

## TODO

- [ ] Add the function that can remove services
