# tkinter_matplotlib
Easy to use matplotlib with GUI

# ibuki_tkinter_matplotlib
グラフのプロットをGUIで使いやすく!  
![1](https://user-images.githubusercontent.com/101094516/167250324-2446efd3-0f65-4e7d-9968-034ebfae80e5.gif)
![2](https://user-images.githubusercontent.com/101094516/167250331-1dc23203-94d4-42c2-b65a-7752455119f5.gif)

## Dependency
Python3.  
matplotlib  
pandas  
tkinter  

## Setup
matplotlib  
pandas  
tkinter  
をインストールすれば使えると思います。

## Usage
```bash
git clone https://github.com/watalabo/ibuki_tkinter_matplotlib.git
python tkinter_plot.py
```

## Note
### txtファイルのフォーマット
下記のようなtxtファイルを入力としています。
```bash
Epoch: 001, Loss: 0.05872, Test Acc: 0.05206
Epoch: 002, Loss: 0.04845, Test Acc: 0.04544
Epoch: 003, Loss: 0.04506, Test Acc: 0.04344
Epoch: 004, Loss: 0.04335, Test Acc: 0.04260
```
や
```bash
Epoch: 500, Loss: 0.03146, Test Acc: 0.03142, SNR: 0
Epoch: 500, Loss: 0.02968, Test Acc: 0.03013, SNR: 5
```
### Application
ほかのデータを用いたい場合は、tkinter_plot.pyの下記の部分
```bash
if mode == 1:
    label = ['Epoch', 'Test Acc']
elif mode == 2:
    label = ['SNR', 'Test Acc']
```
を変更してください。

## Reference
<https://water2litter.net/rum/post/python_tkinter_matplotlib/>
