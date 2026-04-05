# Quick test of a function


# Given index for a buffer, and its dimentions, return xy pos
def index_to_buffer_xy(index, b_width, b_height):
    rows = index // b_width
    index -= b_width * rows
    return (index - 1, rows)  # Should be xy of a buffer


# inverse of index_to_buffer_xy()
def xy_to_buffer_index(xy, b_width, b_height):
    return (xy[1]) * b_width + (xy[0] + 1)  # Should be index for a buffer


if __name__ == "__main__":
    print(index_to_buffer_xy(14, 5, 5))
    print(xy_to_buffer_index(index_to_buffer_xy(14, 5, 5), 5, 5))
