# E*Trade Option Premium ROI Calculator

This Python application calculates the Option Premium ROI using the ETRADE API endpoints.

## Table of Contents

* [Requirements](#requirements)
* [Setup](#setup)
* [Running Code](#running-code)

## Requirements

In order to run this sample application you need the following three items:

1. Python 3 - this sample application is written in Python and requires Python 3. If you do not
already have Python 3 installed, download it from

   [`https://www.python.org/downloads/`](https://www.python.org/downloads/).

2. An [E*TRADE](https://us.etrade.com) account

3. E*TRADE consumer key and consumer secret.


## Setup

1. Edit [`config.ini`](etrade_options/config.ini)
with your consumer key and consumer secret; copy these from your application's keys' section

3. Create the virtual environment by running the Python's venv command; see the command syntax below

```
$ python3 -m venv venv
```

4. Activate the Python virtual environment

```
$ source venv/bin/activate
```

5. Use pip to install dependencies for the sample application

```
$ pip install -r requirements.txt
```

6. Run the application

```
$ cd etrade_options
$ python3 get_option_chain.py -t riot -s 30 -c Put -e 10

Current Stock Price: 39.86
Option                    % from strike    ITM     dte   roi / annual roi     breakeven    lastPrice    bid x ask     bid x ask Size     volume    openInterest   delta / (% chance worthless)     theta       IV
-----------------------  ---------------  -----  -----  ------------------  -----------  -----------  -------------  ----------------  --------  --------------  ------------------------------  -------  -------
RIOT Feb 12 '21 $30 Put      -24.74%        n        3   0.83% / 101.39%          29.75         0.28   0.25 / 0.30        5 / 2            4343            1677          -0.07 / (93%)             -0.16  225.99%
RIOT Feb 19 '21 $30 Put      -24.74%        n       10   3.77% / 137.48%          28.87         1.17   1.13 / 1.25        2 / 10           5588            1515          -0.15 / (85%)             -0.15  196.60%
RIOT Feb 26 '21 $30 Put      -24.74%        n       17   6.67% / 143.14%          28.00         2.15   2.00 / 2.37        5 / 7             250              46          -0.19 / (81%)             -0.14  195.49%
RIOT Mar 05 '21 $30 Put      -24.74%        n       24   9.70% / 147.52%          27.09         3.00   2.91 / 3.30        83 / 6            125             292          -0.21 / (79%)             -0.12  197.80%
RIOT Mar 12 '21 $30 Put      -24.74%        n       31   12.17% / 143.25%         26.35         4.01   3.65 / 4.10       13 / 20            109              53          -0.22 / (78%)             -0.11  196.15%
RIOT Mar 19 '21 $30 Put      -24.74%        n       38   15.00% / 144.08%         25.50         4.65   4.50 / 4.65        2 / 2             978             288          -0.22 / (78%)             -0.10  195.66%
RIOT Mar 26 '21 $30 Put      -24.74%        n       45   16.67% / 135.19%         25.00         5.40   5.00 / 6.00        4 / 1             147              29          -0.23 / (77%)             -0.09  199.30%
RIOT Jun 18 '21 $30 Put      -24.74%        n      129   31.67% / 89.60%          20.50         9.50  9.50 / 10.10      660 / 376           180             220          -0.21 / (79%)             -0.05  180.07%
RIOT Sep 17 '21 $30 Put      -24.74%        n      220   42.00% / 69.68%          17.40        13.06  12.60 / 14.20     616 / 592            21              12          -0.18 / (82%)             -0.03  179.34%
RIOT Jan 21 '22 $30 Put      -24.74%        n      346   50.83% / 53.62%          14.75        15.30  15.25 / 15.65      33 / 421           839             630          -0.16 / (84%)             -0.02  164.38%
```
