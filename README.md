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

[] Develop a simple search tool with Whoosh.
[] Work on UX and reliability
[] Work to ensure the performance is good.
[] Integrate with an LLM.

## Benchmark:

The jobs were run on a Linux system.

### CPU Details

```
Architecture:                       x86_64
CPU op-mode(s):                     32-bit, 64-bit
Byte Order:                         Little Endian
Address sizes:                      39 bits physical, 48 bits virtual
CPU(s):                             4
On-line CPU(s) list:                0-3
Thread(s) per core:                 2
Core(s) per socket:                 2
Socket(s):                          1
NUMA node(s):                       1
Vendor ID:                          GenuineIntel
CPU family:                         6
Model:                              142
Model name:                         Intel(R) Core(TM) i7-7500U CPU @ 2.70GHz
Stepping:                           9
CPU MHz:                            2900.000
CPU max MHz:                        3500.0000
CPU min MHz:                        400.0000
BogoMIPS:                           5799.77
L1d cache:                          64 KiB
L1i cache:                          64 KiB
L2 cache:                           512 KiB
L3 cache:                           4 MiB
NUMA node0 CPU(s):                  0-3
```

### 16 GB Ram

> As of 25th Feb 2024 the machine used for testing is 7 years old. :D

### Whoosh Indexer

We are using BufferedWriter to ensure we are able to write multiple docs with multiple
requests in the same session.

### Use case

We have a collection of pdfs, which are being parsed by the PyMUPDF and each page of the PDF
is being indexed into whoosh. Thus, average document size isn't much for whoosh.

### No performance optimisations done

The following test was done in the same order metrics are mentioned and not independently.

| Pages | Size (MB) | Time Taken | Index Size (MB) | Notes                                                                   |
| ----- | :-------: | ---------: | --------------- | ----------------------------------------------------------------------- |
| 711   |     3     |    0:00:17 | 4.8             |
| 1484  |    6.2    |    0:00:50 | 14.6            |
| 2867  |   12.1    |    0:02:17 | 31.7            |
| 24178 |   242.9   |    0:09:24 | **87.6**        | CPU consumption went about 100% for PDF parser and indexer was stopped. |

The machine running this tool needs to have a good CPU with multiple cores. The CPU went to about 99%
for **1045** files with **24178** pages having **242.9 MB** of data.

Recommendation would be to index anything less than 200MB, perhaps at most 150MB data at once for a machine with similar configuration and no optimisations.

### With performance optimisation mentioned in [Whoosh documentation](https://whoosh.readthedocs.io/en/latest/batch.html)

- Procs: 2
- Limitmb: 1024

> Not performing unbounded cache for the analyser. Stemmer has 50k words LRU cache.
> Following the articles, it seemed a good enough number if not large (as of Feb, 2924).
>
> [LinkedIn Article](https://www.linkedin.com/pulse/how-many-words-english-language-955-rule-etoninstitute/) by Eaton Institure
>
> [Merriam Webster](https://www.merriam-webster.com/help/faq-how-many-english-words) suggests 1MM words with variance of 250k
>
> [Wikipedia](https://en.wikipedia.org/wiki/List_of_dictionaries_by_number_of_words) agrees Merriam Webster.

| Pages | Size (MB) | Time Taken | Index Size | Notes |
| ----- | :-------: | ---------: | ---------- | ----- |
| 711   |     3     |    0:00:19 | 4.8        |
| 1484  |    6.2    |    0:00:48 | 14.6       |
| 2867  |   12.1    |    0:02:23 | 31.7       |
| 24169 |   242.9   |    0:12:03 | -          |

#### Observation

There is no observable performance benefit. Upon increase limitmb, there was no extra RAM used.
Infact with no optimisations, the tested use cases work better.
