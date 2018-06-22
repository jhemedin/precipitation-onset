import os
os.system("ffmpeg -framerate 10 -pattern_type glob -i '/home/scarani/Desktop/output/goes/Mesoscale-1/*.png' -movflags faststart -pix_fmt yuv420p -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' -y '/home/scarani/Desktop/output/goes/animation.mp4'")
