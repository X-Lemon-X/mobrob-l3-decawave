# Reconstructed from the CDR bytes of the lab rosbags (field names guessed,
# binary layout verified). header.frame_id holds the anchor id, e.g. "1419".
std_msgs/Header header
float64 x
float64 y
float64 z
float64 qf           # always 1.0 in the lab bags
float64 distance     # measured tag-anchor range [m]
float64 distance_qf  # always 1.0 in the lab bags
