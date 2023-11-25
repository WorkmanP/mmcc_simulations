import numpy as np
from math import ceil

def main():
    rands = [ceil(np.random.exponential((9.5))) for _ in range(100000)]
    rands2 = [1 + round(np.random.exponential(9+0.49)-0.49)for _ in range(100000)]

    print(f"rands (ceil) avg = {sum(rands)/len(rands)}")
    print(f"rands2 (adj) avg = {sum(rands2)/len(rands2)}")
    # vals = {}
    # for x in rands:
    #     try:             
    #         vals[x] += 1
    #     except KeyError:
    #         vals[x] = 1

    # output = {k: v for k, v in sorted(vals.items(), key=lambda item: item[0])} 

if __name__ == "__main__":
    main()
