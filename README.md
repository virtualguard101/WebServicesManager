# WebServicesManager

**A script set for web services management.**

## Usage

- First clone the repository
  ```bash
  # the remote repository where located on my cloud server
  git clone https://gitea.virtualguard101.com/virtualguard101/webscripts.git
  cd webscripts
  ```

- Launch the manager with `main.py`
  ```bash
  ./main.py
  ```

  Add `-h` as parameter to find usage:
  ```bash
  ./main.py -h
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
