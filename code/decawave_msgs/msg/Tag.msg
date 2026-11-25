# Published on /pioneerX/tag_pose: built-in position estimate of the tag.
std_msgs/Header header
float64 x
float64 y
float64 z
float64 quality      # 0.0 .. 1.0
int32 anchor_count   # anchors used (3 or 4 in the lab bags)
