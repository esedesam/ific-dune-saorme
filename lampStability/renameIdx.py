from os import rename

dir = 'D:/ific-dune-saorme/lampStability/20230621_deuteriumPMT/'

for i in range(17, 38, 1):
    rename('%sdf_nofilter_0deg_180-300_10 (%d).txt' % (dir, i), '%sdf_nofilter_0deg_180-300_10 (%d).txt' % (dir, i - 1))