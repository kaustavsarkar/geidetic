# AIN

AIN attempts to simplify searching through the documents. This is a simple GUI tool which any person
should be able to install on their own systems and use it.

The purpose of keeping it a desktop is to ensure the data is safe, and it can utilise the resources of the
client system. It actually takes a lot of pressure off of the developers to keep it hosted somewhere.

## Requirements

- Python
- Vite
- Bun

### Why Vite and Bun?

I have used the CRA for my previous projects and have noticed how slow these things work. The up times and compilation times
are huge. And not to mention, it fills up my Swap Memory like anything which makes me restart my system everytime. So
consider this an experiment with Vite and Bun to see how they perform with a growing application.

#### Updates
- [22-04-2024] So far so good. Compilation is good. Does not slow down my computer.

## Installation

- **Step 0 :** Ensure that you are running this on a linux distribution. (AIN is currently tested only on linux machines)

  (Though the code written should ideally work on all distros)

- **Step 1 :** Clone this repo:

```bash
git clone https://github.com/kaustavsarkar/geidetic.git
```

- **Step 2 :** Ensure everything is done inside virtual environment

```bash
cd geidetic
python3 -m venv .venv
source .venv/bin/activate
```

- **Step 3 :** Move to the repo and install the requirements

```bash
pip install -r requirements.txt
pip install pipenv
```

- **Step 4 :** Install the ain package

```bash
cd ..
pipenv install -e .
```

## Basic Usage

To launch entire GUI:

```bash
bun start
```

To launch only React Frontend:

```bash
bun run dev
```

## TODO:

https://github.com/dzc0d3r/pywebview-react-boilerplate/tree/main

## Roadmap:

A very high level roadmap.

- [ ] Develop a simple search tool with Whoosh.
- [ ] Work on UX and reliability
- [ ] Work to ensure the performance is good.
- [ ] Integrate with an LLM.
