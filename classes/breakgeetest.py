import cv2
import time
import numpy as np
from PIL import Image
import urllib.request
import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from random import randint

from scipy import ndimage, misc
from scipy.spatial.distance import hamming

#from selenium import webdriver

from classes.auxiliary_function import draw_bounding_box, find_bounding_box, segment_pictures
def solvegee(usethis,confirmgee):
    template = cv2.imread('playing.png')
    print(template.shape)
    src = template.copy() 
    print(math.ceil(usethis[2][1]),math.ceil(confirmgee[2][1]),(math.ceil(usethis[2][0])),math.ceil(confirmgee[3][0]))
    dst = src[math.ceil(confirmgee[2][1]):math.ceil(usethis[2][1]),(math.ceil(usethis[2][0])):math.ceil(confirmgee[3][0])]
    cv2.imwrite('imageedst.png', dst)

    img_grey = cv2.cvtColor(dst,  cv2.COLOR_BGR2GRAY)

    print('shape:', dst.shape)
    print('size:', dst.size)
    print('--- arr ---\n', dst, '\n--- end ---')
    cv2.imwrite('imagee.png', img_grey)
    # crop image
    main_pane = img_grey[50:,:]
    cv2.imwrite('main_pane.png', main_pane)
    cv2.imwrite('target.png', img_grey[:60,:])

    # Image preprocessing

    color_threshold = 180
    main_pane = cv2.blur(main_pane,(3,3)) # By blurring, we can remove some white pixels which may affecting the matching
    main_pane[main_pane<color_threshold] = 0
    main_pane[main_pane>=color_threshold] = 255
    Image.fromarray(main_pane)
    print('start  bounding')
    icons_rect_coordinates = find_bounding_box(main_pane, (20,20), (100,100),sort=False)
    print('finish bounding')
    icons = segment_pictures(main_pane,icons_rect_coordinates,(30,30))
    draw_bounding_box(main_pane, icons_rect_coordinates)
    target_color_threshold = 40
    print('start target')
    target_pane = 255 - img_grey[:50,:]
    cv2.imwrite('target.png', img_grey[:60,:])
    target_pane[target_pane<target_color_threshold] = 0
    target_pane[target_pane>=target_color_threshold] = 255

    Image.fromarray(target_pane)
    print('start finding target bounding')

    targets_rect_coordinates = find_bounding_box(target_pane, (5,5), (100,100)) 
    targets = segment_pictures(target_pane,targets_rect_coordinates,(30,30))
    draw_bounding_box(target_pane, targets_rect_coordinates)
    '''
    similarity_matrix = [[a1, a2, a3, a4, a5],
                        [b1, b2, b3, b4, b5],
                        [c1, c2, c3, c4, c5],
                        [d1, d2, d3, d4, d5],
                        ]
                        
    There are 4 targets and 5 icons, so it is 4x5 matrix. For example, b3 denotes the similarity between second target and
    third icon
    '''

    similarity_matrix = []
    for target in targets:
        similarity_per_target = []
        for icon in icons:
            similarity_per_target.append(calculate_max_matching(target,icon,6))
        similarity_matrix.append(similarity_per_target)
    fig,ax = plt.subplots(1)
    ax.imshow(main_pane)

    # Calculate Mapping
    target_candidates = [False for _ in range(len(targets))]
    icon_candidates = [False for _ in range(len(icons))]

    mapping = {}

    # Approach 1 (May not work, because collision may occur)
    # Using np.argsort(-arr)

    '''
    similarity_matrix = [[0.49798074, 0.61611921, 0.56135607, 0.43419564, 0.61747766],
                        [0.5085994 , 0.53169155, 0.70087528, 0.30092609, 0.53550088],
                        [0.62834615, 0.49904037, 0.46511394, 0.31213483, 0.46880326],
                        [0.53429979, 0.59877342, 0.56217539, 0.37746215, 0.73305559]]


    np.argsort(np.array(similarity_matrix),axis=1) = [[3, 0, 2, 1, 4],
                                                    [3, 0, 1, 4, 2],
                                                    [3, 2, 4, 1, 0],
                                                    [3, 0, 2, 1, 4]]

    In this approach, 
    First target matches with fifth icon
    Second target matches with second icon
    Third target matches with fist icon
    Fourth target matches with fifth icon

    Collision happens! As both first target and fourth target matches the same icon
    '''


    # Sort the flatted similarity matrix in descending order, and assign the pair between target and icon if both of them
    # havem't been assigned.
    arr = np.array(similarity_matrix).flatten()
    arg_sorted = np.argsort(-arr)

    for e in arg_sorted:
        col = e //len(icons)
        row = e % len(icons)
        
        if target_candidates[col] == False and icon_candidates[row] == False:
            target_candidates[col], icon_candidates[row] = True, True
            mapping[col] = row

    # Circling the most similar icon,
    # blue circle: first target
    # red circle: second target
    # yellow circle: third target
    # green circle: fourth target
    color_map = {1:'b',2:'r',3:'y',4:'g'}
    for key in mapping:
        x,y,w,h = icons_rect_coordinates[mapping[key]]
        
        # x,y is the coordinate of top left hand corner
        # Bounding box is 70x70, so centre of circle = (x+70/2, y+70/2), i.e. (x+35, y+35)
        centre_x = x+(w//2)
        centre_y = y+(h//2)
        # Plot circle
        circle = plt.Circle((centre_x,centre_y), 20, color=color_map[key+1], fill=False, linewidth=5)
        # Plot centre
        plt.plot([centre_x], [centre_y], marker='o', markersize=10, color="white")
        ax.add_patch(circle)
        
    plt.show()            
    # red circle: second target
    # yellow circle: third target
    # green circle: fourth target
    Image.fromarray(img_grey[350:,:110])

    # # Uncomment this part for real Geetest CAPTCHA


    time.sleep(10)
    for i, target in enumerate(targets):
        key = i
        x,y,w,h = icons_rect_coordinates[mapping[key]]
        
    #     # x,y is the coordinate of top left hand corner
    #     # Bounding box is 70x70, so centre of circle = (x+70/2, y+70/2), i.e. (x+35, y+35)
        centre_x = x+(w//2)
        centre_y = y+(h//2)
        
        #ele=driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='加载中...'])[1]/following::div[1]")
    #    action = webdriver.common.action_chains.ActionChains(driver)
    #    action.move_to_element_with_offset(ele, centre_x, centre_y)
    #    time.sleep(randint(100,700)/1000) # Random Pause between two consecutive clicks
    #    action.click()
    #    action.perform()

    # # Click Ok button in CAPTCHA after some random pause
    time.sleep(randint(100,700)/1000)
    # driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='帮助反馈'])[1]/following::div[2]").click()
def calculate_max_matching(target,icon,d):
    largest_val = 0
    for degree in range(0,360,d):
        tmp = ndimage.rotate(target, degree, reshape=False)
        res = cv2.matchTemplate(icon,tmp,cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > largest_val:
            largest_val = max_val
    return largest_val

    # Calculate similarity matrix for each target, icon pair