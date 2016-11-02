# Chesstakov

A deep neural network based chess program.

## Steps:

1. Run:

```
cat *.pgn | pgn-extract -s -D -#3000
```

to generate pgn files, each containing 3000 games.

2. Run parser.py to extract at most 10 random position from each game. For
each pgn file, a new HDF5 file will be created.

3. Run concat_h5.py to generate merge all HDF5 files into one.

4. Run generate_training_dataset.py.

5. Run board_selection_tranining.py.