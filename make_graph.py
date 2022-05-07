# %%
import pandas as pd
import matplotlib.pyplot as plt
import re
import os.path as osp
from glob import glob
# from pprint import pprint


def read_log(txt_path: str, header: list) -> pd.DataFrame :
    data = []
    with open(txt_path) as f:
        for result in f:
            # Epoch, Loss, Test Acc の値を抜き出す
            result = result.rstrip('\n')
            result_key = re.split(', |: ', result)[0::2]
            result_val = re.split(', |: ', result)[1::2]
            tmp_dict = dict(zip(result_key, result_val))
            tmp_list = []
            # str -> int,float
            try:
                tmp_list = [ str2num( tmp_dict[k] ) for k in header]
                # data.append([int(result_list[0]), float(result_list[1]), float(result_list[2])])
                data.append(tmp_list)
            except Exception as e:
                # print(e)
                pass
    df = pd.DataFrame(data, columns=header)
    return df

def str2num(t: str) -> float: # or int
    if t.isdecimal():
        return int(t)
    else:
        try:
            n = float(t)
            return n
        except ValueError:
            return



if __name__ =="__main__":
    log_list = glob("./logs/*.txt")
    print(pd.DataFrame(log_list))
    num = input('select an input (Enter number)')
    txt_path = log_list[int(num)]
    header = ['Epoch', 'Loss', 'Test Acc']

    # plot
    df = read_log(txt_path, header)
    fig, ax = plt.subplots()
    ax.plot('Epoch', 'Test Acc', marker='o', markersize=2, data = df)
    plt.show

    plt.savefig('./plot_fig/{}.png'.format(osp.splitext(osp.basename(txt_path))[0]))

# %%
