## 2024-06-25 - math.dist vs math.sqrt
**Learning:** `math.dist` in Python is significantly faster (~2.5x) than manually calculating the distance with `math.sqrt` and arithmetic operations due to being implemented directly in C, and faster than `math.hypot` (~1.5x) because it directly takes sequences rather than requiring unpacking/calculating differences in Python.
**Action:** Replace manual distance calculations (like in `tank.py`) with `math.dist`.
