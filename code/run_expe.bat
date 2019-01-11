FOR %%D IN (0 2 4 6 8 10 12 14 16 18 20) DO START /WAIT python experiments.py 1 80 0.8 0.5 %%I

FOR %%F IN (0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95 1.0) DO START /WAIT python experiments.py 1 80 %%F 0.5 0

FOR %%E IN (0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0) DO START /WAIT python experiments.py 1 80 0.8 %%E 0
