''' coords.py - helpers for dealing with coord systems '''


from collections import namedtuple


# TODO(Keagan): we might need to make a proper Vec2 class when the need for
# more complex vector calculations arises. As for now I don't see a need.
# the only things that I forsee making use of them are the chess pieces in 
# board_data.py... And then we might as well write those calculations straight
# in their functions

Vec2 = namedtuple('Vec2', ['x', 'y']) 


def screen_coord_to_pixel(screen_size: (int, int), coord: (float, float)) \
    -> (int, int):

    ''' Take a floating point coordinate and convert it to a
    actual pixel location and return it 
    '''

    # gets x coord multiplied no. of pixels on x axis
    x_pixel_pos = coord[0] * screen_size[0] 
    # gets y coord multiplied no. of pixels on y axis
    y_pixel_pos = coord[1] * screen_size[1]

    return (int(x_pixel_pos), int(y_pixel_pos))


def pixel_to_screen_coord(screen_size: (int, int), pixel_pos: (int, int)) \
    -> (float, float):

    ''' Take a pixel location and convert it to a floating point coord with x
    and y components between 0.0 and 1.0
    '''

    x_coord = pixel_pos[0] / screen_size[0]
    y_coord = pixel_pos[1] / screen_size[1]

    return (x_coord, y_coord)
 