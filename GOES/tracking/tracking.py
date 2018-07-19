# %%  
# Instantiate tracks object and view parameter defaults
tracks_obj = Cell_tracks(field='reflectivity')

# Adjust size parameter
tracks_obj.params['FIELD_THRESH'] = -273
tracks_obj.params['FLOW_MARGIN'] = 10000
tracks_obj.params['GS_ALT'] = 1500
tracks_obj.params['ISO_SMOOTH'] = 3
tracks_obj.params['ISO_THRESH'] = 8
tracks_obj.params['MAX_DISPARITY'] = 999
tracks_obj.params['MAX_FLOW_MAG'] = 50
tracks_obj.params['MAX_SHIFT_DISP'] = 15
tracks_obj.params['MIN_SIZE'] = 4
tracks_obj.params['SEARCH_MARGIN'] = 4000


# Get tracks from grid generator
print(tracks_obj.params)
tracks_obj.get_tracks(grid_gen)
# %%
# Inspect tracks
print(tracks_obj.tracks)



#for i in range(0,500,1):
#    for j in range(0,500,1):
#        k = b[i][j]
#        u = str(k)
#        if k == 'nan':
#            print('[' + str(i) + ']' + '[' + str(j) + ']' + '\n')
        

# Create generator of the same grids for animator
#anim_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)

# Create animation in current working directory
#animate(tracks_obj, anim_gen, 'tint_test_animation', alt=1500)
        
    

        

#xlist = x.tolist()
#ylist = y.tolist()
#loc = []
#
#for i in range(0,500,1):
#    
#    loc.append((xlist[i],ylist[i]))
    
