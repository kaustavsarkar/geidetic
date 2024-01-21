# AIN

## Installation

- **Step 0 :** Ensure that you are running this on a linux distribution. (AIN is currently tested only on linux machines)

- **Step 1 :** Clone this repo:
    ```bash
    git clone https://github.com/kaustavsarkar/geidetic.git
    ```

- **Step 2 :** Move to the repo and install the requirements

    ```bash
    cd geidetic/ain
    pip install -r requirements.txt
    pip install pipenv
    ```

- **Step 3 :** Install the ain package
    
    ```bash
    cd ..
    pipenv install -e .
    ```

## Basic Usage

In a python file:

```python
from ain.app import App

app = App()
app.launch_explorer()
app.mainloop()

```

Try running the ```main.py``` file inside the ```/ain``` directory to run the basic demo

```bash
cd ain
python3 main.py
```

## TODO:
https://github.com/dzc0d3r/pywebview-react-boilerplate/tree/main