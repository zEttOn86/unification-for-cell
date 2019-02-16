# 細胞のための天下統一プロジェクト

### 実行方法

1. `data/preprocessed` いかに，各スライスごとのbounding boxが書かれたcsvをおく

Example:

```
  data/preprocessed/bbox
        |
        |--- 3d_bbox_z0.csv
        |--- ...
        |--- 3d_bbox_zMM.csv
```

2. `data/raw/test/org` いかに，原画像を置く


3. 実行する

```
python main.py -i data\raw\test\org\Image_2~48_test.mhd -o results/Image_2~48_test.mhd -icfd data\preprocessed\bbox
```

## :punch::punch::punch::punch: がんばれーーーーー！！！ :punch::punch::punch::punch:
