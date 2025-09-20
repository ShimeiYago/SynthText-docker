# Author: Ankush Gupta
# Date: 2015

"""
Visualize the generated localization synthetic
data stored in h5 data-bases
"""
from __future__ import division
import os
import os.path as osp
import numpy as np
import matplotlib.pyplot as plt 
import h5py 
from common import *



def viz_textbb(text_im, charBB_list, wordBB, lineBB=None, output_path=None, alpha=1.0, line_only=False):
    """
    text_im : image containing text
    charBB_list : list of 2x4xn_i bounding-box matrices
    wordBB : 2x4xm matrix of word coordinates
    output_path : path to save the visualization (if None, show instead)
    """
    plt.close(1)
    plt.figure(1, figsize=(12, 8))
    plt.imshow(text_im)
    H,W = text_im.shape[:2]

    if not line_only:
        # plot the character-BB:
        for i in range(len(charBB_list)):
            bbs = charBB_list[i]
            ni = bbs.shape[-1]
            for j in range(ni):
                bb = bbs[:,:,j]
                bb = np.c_[bb,bb[:,0]]
                plt.plot(bb[0,:], bb[1,:], 'r', alpha=alpha/2)

        # plot the word-BB:
        for i in range(wordBB.shape[-1]):
            bb = wordBB[:,:,i]
            bb = np.c_[bb,bb[:,0]]
            plt.plot(bb[0,:], bb[1,:], 'g', alpha=alpha)
            # visualize the indiv vertices:
            vcol = ['r','g','b','k']
            for j in range(4):
                plt.scatter(bb[0,j],bb[1,j],color=vcol[j])        

    # plot line-level BB only in line-only mode
    if line_only and (lineBB is not None):
        for i in range(lineBB.shape[-1]):
            bb = lineBB[:,:,i]
            bb = np.c_[bb,bb[:,0]]
            plt.plot(bb[0,:], bb[1,:], 'b', linewidth=2, alpha=alpha*0.9)


    plt.gca().set_xlim([0,W-1])
    plt.gca().set_ylim([H-1,0])
    if line_only:
        title = 'SynthText Visualization (Blue: line)'
    else:
        title = 'SynthText Visualization (Red: char, Green: word)'
    plt.title(title)
    plt.axis('off')  # 軸を非表示にして画像をクリーンに
    
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
        plt.close()
    else:
        plt.show(block=False)

def main(db_fname, line_only=False):
    db = h5py.File(db_fname, 'r')
    dsets = sorted(db['data'].keys())
    print ("total number of images : ", colorize(Color.RED, len(dsets), highlight=True))
    
    # 出力ディレクトリを作成
    output_dir = 'results/visualized'
    os.makedirs(output_dir, exist_ok=True)
    
    for k in dsets:
        rgb = db['data'][k][...]
        charBB = db['data'][k].attrs['charBB']
        wordBB = db['data'][k].attrs['wordBB']
        lineBB = db['data'][k].attrs['lineBB'] if 'lineBB' in db['data'][k].attrs else None
        txt = db['data'][k].attrs['txt']

        # 画像を保存
        output_path = osp.join(output_dir, f'{k}_visualization.png')
        viz_textbb(rgb, [charBB], wordBB, lineBB=lineBB, output_path=output_path, line_only=line_only)
        
        print ("image name        : ", colorize(Color.RED, k, bold=True))
        if not line_only:
            print ("  ** no. of chars : ", colorize(Color.YELLOW, charBB.shape[-1]))
            print ("  ** no. of words : ", colorize(Color.YELLOW, wordBB.shape[-1]))
        print ("  ** text         : ", colorize(Color.GREEN, txt))
        if line_only and (lineBB is not None):
            print ("  ** no. of lines: ", colorize(Color.YELLOW, lineBB.shape[-1]))
        print ("  ** saved to     : ", colorize(Color.BLUE, output_path))

        if 'q' in input("next? ('q' to exit) : "):
            break
    
    print(f"\nVisualization images saved to: {colorize(Color.GREEN, output_dir)}")
    db.close()

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Visualize SynthText results')
    parser.add_argument('--db', default='results/SynthText.h5', help='Path to SynthText h5 file')
    parser.add_argument('--line_bb', action='store_true', dest='line_bb', default=False, help='Show only line-level bounding boxes (if present)')
    args = parser.parse_args()
    main(args.db, line_only=args.line_bb)

